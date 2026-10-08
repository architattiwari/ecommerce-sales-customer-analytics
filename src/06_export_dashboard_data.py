"""Step 6: export a star schema for Power BI to powerbi/data/.

fact_orders    one row per order line (an order with 3 products has 3 rows)
dim_customer, dim_product, dim_date, dim_location
"""
import pandas as pd

from common import DELIVERY_SLA_DAYS, NON_SALE_STATUSES, POWERBI_DIR, PROCESSED_DIR, load_processed


def build_dim_customer(customers):
    summary = pd.read_csv(PROCESSED_DIR / "customer_summary.csv")
    dim = customers.merge(summary[["customer_id", "value_segment", "total_orders", "total_revenue", "clv_estimate"]], on="customer_id", how="left")
    dim = dim.rename(columns={"customer_segment": "plan_segment"})
    dim.insert(0, "customer_key", range(1, len(dim) + 1))
    return dim[["customer_key", "customer_id", "customer_name", "city", "state", "signup_date",
                "plan_segment", "value_segment", "total_orders", "total_revenue", "clv_estimate"]]


def build_dim_product(products):
    dim = products.copy()
    dim.insert(0, "product_key", range(1, len(dim) + 1))
    return dim


def build_dim_location(customers, orders):
    cities = pd.concat([customers[["city", "state"]],
                        orders[["shipping_city", "shipping_state"]].set_axis(["city", "state"], axis=1)])
    dim = cities.drop_duplicates().sort_values(["state", "city"]).reset_index(drop=True)
    dim.insert(0, "location_key", range(1, len(dim) + 1))
    return dim


def build_dim_date(orders):
    dates = pd.date_range(orders["order_date"].min().normalize(), orders["order_date"].max().normalize())
    dim = pd.DataFrame({"date": dates})
    dim["date_key"] = dim["date"].dt.strftime("%Y%m%d").astype(int)
    dim["year"] = dim["date"].dt.year
    dim["quarter"] = "Q" + dim["date"].dt.quarter.astype(str)
    dim["month_number"] = dim["date"].dt.month
    dim["month_name"] = dim["date"].dt.strftime("%b")
    dim["month_year"] = dim["date"].dt.strftime("%b %Y")
    dim["day_of_week"] = dim["date"].dt.strftime("%a")
    dim["is_weekend"] = (dim["date"].dt.dayofweek >= 5).astype(int)
    dim["date"] = dim["date"].dt.strftime("%Y-%m-%d")
    return dim[["date_key", "date", "year", "quarter", "month_number", "month_name", "month_year",
                "day_of_week", "is_weekend"]]


def build_fact_orders(orders, order_items, reviews, dim_customer, dim_product, dim_location):
    fact = order_items.merge(orders.drop(columns="order_revenue"), on="order_id")
    fact = fact.merge(reviews[["order_id", "product_id", "rating"]], on=["order_id", "product_id"], how="left")

    fact["customer_key"] = fact["customer_id"].map(dim_customer.set_index("customer_id")["customer_key"])
    fact["product_key"] = fact["product_id"].map(dim_product.set_index("product_id")["product_key"])
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    location_lookup = dim_location.set_index(["city", "state"])["location_key"]
    fact["location_key"] = pd.MultiIndex.from_frame(fact[["shipping_city", "shipping_state"]]).map(location_lookup)

    fact["delivery_days"] = fact["delivery_days"].astype("Int64")
    fact["is_valid_sale"] = (~fact["order_status"].isin(NON_SALE_STATUSES)).astype(int)
    fact["delivery_status"] = pd.Series(pd.NA, index=fact.index, dtype="object")
    delivered = (fact["order_status"] == "Delivered") & fact["delivery_days"].notna()
    fact.loc[delivered, "delivery_status"] = "Late"
    fact.loc[delivered & (fact["delivery_days"] <= DELIVERY_SLA_DAYS), "delivery_status"] = "On Time"

    columns = ["order_id", "customer_key", "product_key", "date_key", "location_key", "order_status", "payment_method",
               "is_valid_sale", "quantity", "unit_price", "discount", "gross_sales", "discount_amount", "revenue",
               "cost", "profit", "delivery_days", "delivery_status", "rating"]
    return fact[columns]


def check_keys(fact, dim_customer, dim_product, dim_date, dim_location):
    assert fact["customer_key"].isin(dim_customer["customer_key"]).all()
    assert fact["product_key"].isin(dim_product["product_key"]).all()
    assert fact["date_key"].isin(dim_date["date_key"]).all()
    assert fact["location_key"].isin(dim_location["location_key"]).all()
    print("Key check passed: every fact row matches one row in each dimension.")


def main():
    customers, products, orders, order_items, reviews = load_processed()
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    dim_customer = build_dim_customer(customers)
    dim_product = build_dim_product(products)
    dim_location = build_dim_location(customers, orders)
    dim_date = build_dim_date(orders)
    fact_orders = build_fact_orders(orders, order_items, reviews, dim_customer, dim_product, dim_location)
    check_keys(fact_orders, dim_customer, dim_product, dim_date, dim_location)

    tables = {"fact_orders": fact_orders, "dim_customer": dim_customer, "dim_product": dim_product,
              "dim_date": dim_date, "dim_location": dim_location}
    for name, table in tables.items():
        table.to_csv(POWERBI_DIR / f"{name}.csv", index=False)
        print(f"Saved powerbi/data/{name}.csv ({len(table):,} rows)")

    valid = fact_orders[fact_orders["is_valid_sale"] == 1]
    print(f"\nReconciliation: fact revenue (valid sales) = {valid['revenue'].sum():,.2f}")


if __name__ == "__main__":
    main()
