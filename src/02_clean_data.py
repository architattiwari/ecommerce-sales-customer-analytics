"""Step 2: clean the raw CSV files and add the derived metrics.

Reads data/raw/ (never changed) and writes data/processed/.
Every fix is counted and saved to reports/cleaning_log.csv.
"""
import pandas as pd

from common import PROCESSED_DIR, RAW_DIR, REPORTS_DIR

cleaning_log = []

CATEGORY_NAMES = {
    "electronics": "Electronics", "electronic": "Electronics",
    "fashion": "Fashion",
    "home & kitchen": "Home & Kitchen", "home and kitchen": "Home & Kitchen",
    "beauty & personal care": "Beauty & Personal Care", "beauty and personal care": "Beauty & Personal Care",
    "beauty": "Beauty & Personal Care",
    "books": "Books",
    "sports & fitness": "Sports & Fitness", "sports and fitness": "Sports & Fitness", "sports": "Sports & Fitness",
    "toys & games": "Toys & Games", "toys and games": "Toys & Games", "toys": "Toys & Games",
    "grocery": "Grocery", "groceries": "Grocery",
}
STATUS_NAMES = {"delivered": "Delivered", "shipped": "Shipped", "processing": "Processing",
                "cancelled": "Cancelled", "returned": "Returned"}
PAYMENT_NAMES = {"upi": "UPI", "credit card": "Credit Card", "debit card": "Debit Card",
                 "cash on delivery": "Cash on Delivery", "cod": "Cash on Delivery",
                 "net banking": "Net Banking", "netbanking": "Net Banking", "wallet": "Wallet"}


def log(table, issue, rows):
    cleaning_log.append({"table": table, "issue": issue, "rows_affected": int(rows)})
    print(f"  {table}: {issue} -> {int(rows):,} rows")


def inspect_table(name, df):
    print(f"\n{name}: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("  data types:", dict(df.dtypes.astype(str)))
    missing = df.isna().sum()
    print("  missing values:", missing[missing > 0].to_dict() or "none")
    print("  fully duplicated rows:", df.duplicated().sum())


def clean_text(series):
    return series.str.strip().str.title()


def count_changes(before, after):
    return (before.fillna("") != after.fillna("")).sum()


# ---------------------------------------------------------------------------
# One function per table
# ---------------------------------------------------------------------------
def clean_customers(customers):
    name = "customers"
    for column in ["city", "state"]:
        cleaned = clean_text(customers[column])
        if column == "city":
            cleaned = cleaned.replace({"Bangalore": "Bengaluru"})
        log(name, f"{column} spelling/capitalisation fixed", count_changes(customers[column], cleaned))
        customers[column] = cleaned

    customers["customer_name"] = customers["customer_name"].str.strip().str.title()
    customers["email"] = customers["email"].str.strip().str.lower()

    segment = customers["customer_segment"].str.strip().str.title()
    log(name, "segment capitalisation fixed", count_changes(customers["customer_segment"], segment) - segment.isna().sum())
    log(name, "missing segment filled with most common value", segment.isna().sum())
    customers["customer_segment"] = segment.fillna(segment.mode()[0])
    log(name, "missing email (left empty)", customers["email"].isna().sum())

    customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
    log(name, "duplicate customer records removed", customers.duplicated("customer_id").sum())
    return customers.drop_duplicates(subset="customer_id")


def clean_products(products):
    name = "products"
    category = products["category"].str.strip().str.lower().map(CATEGORY_NAMES)
    if category.isna().any():
        raise ValueError("Found a category name that is not in CATEGORY_NAMES")
    log(name, "category names standardised", count_changes(products["category"], category))
    products["category"] = category

    log(name, "duplicate products removed", products.duplicated("product_id").sum())
    products = products.drop_duplicates(subset="product_id").copy()

    # missing cost price: use the typical cost-to-price ratio of the same category
    cost_ratio = (products["cost_price"] / products["unit_price"]).groupby(products["category"]).transform("median")
    log(name, "missing cost_price estimated from category ratio", products["cost_price"].isna().sum())
    products["cost_price"] = products["cost_price"].fillna((products["unit_price"] * cost_ratio).round(2))
    return products


def clean_orders(orders, customers):
    name = "orders"
    log(name, "duplicate orders removed", orders.duplicated("order_id").sum())
    orders = orders.drop_duplicates(subset="order_id").copy()

    status = orders["order_status"].str.strip().str.lower().map(STATUS_NAMES)
    payment = orders["payment_method"].str.strip().str.lower().map(PAYMENT_NAMES)
    if status.isna().any() or payment.isna().any():
        raise ValueError("Found a status or payment name that is not in the mapping")
    log(name, "order_status standardised", count_changes(orders["order_status"], status))
    log(name, "payment_method standardised", count_changes(orders["payment_method"], payment))
    orders["order_status"] = status
    orders["payment_method"] = payment
    orders["shipping_city"] = clean_text(orders["shipping_city"])

    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    log(name, "invalid order_date, orders removed", orders["order_date"].isna().sum())
    orders = orders.dropna(subset=["order_date"]).copy()

    orders["delivery_date"] = pd.to_datetime(orders["delivery_date"], errors="coerce")
    too_early = orders["delivery_date"] < orders["order_date"].dt.normalize()
    log(name, "delivery_date before order_date, set to empty", too_early.sum())
    orders.loc[too_early, "delivery_date"] = pd.NaT
    missing_delivery = orders["order_status"].isin(["Delivered", "Returned"]) & orders["delivery_date"].isna()
    log(name, "delivered orders without delivery_date (kept, excluded from delivery stats)", missing_delivery.sum())

    # missing shipping state: look it up from the shipping city
    city_to_state = customers.drop_duplicates("city").set_index("city")["state"]
    log(name, "missing shipping_state filled from shipping_city", orders["shipping_state"].isna().sum())
    orders["shipping_state"] = clean_text(orders["shipping_state"]).fillna(orders["shipping_city"].map(city_to_state))

    unknown_customer = ~orders["customer_id"].isin(customers["customer_id"])
    log(name, "orders with unknown customer removed", unknown_customer.sum())
    orders = orders[~unknown_customer].copy()

    orders["delivery_days"] = (orders["delivery_date"] - orders["order_date"].dt.normalize()).dt.days.astype("Int64")
    return orders


def clean_order_items(order_items, orders, products):
    name = "order_items"
    log(name, "duplicate order lines removed", order_items.duplicated(["order_id", "product_id"]).sum())
    order_items = order_items.drop_duplicates(subset=["order_id", "product_id"]).copy()

    log(name, "missing discount set to 0", order_items["discount"].isna().sum())
    order_items["discount"] = order_items["discount"].fillna(0)
    entered_as_percent = order_items["discount"] > 1
    log(name, "discount entered as percent (e.g. 15) converted to 0.15", entered_as_percent.sum())
    order_items.loc[entered_as_percent, "discount"] = order_items["discount"] / 100

    list_price = order_items["product_id"].map(products.set_index("product_id")["unit_price"])
    log(name, "missing unit_price filled from products table", order_items["unit_price"].isna().sum())
    order_items["unit_price"] = order_items["unit_price"].fillna(list_price)

    bad_quantity = order_items["quantity"] <= 0
    log(name, "quantity zero or negative, lines removed", bad_quantity.sum())
    order_items = order_items[~bad_quantity]

    orphan = ~order_items["order_id"].isin(orders["order_id"]) | ~order_items["product_id"].isin(products["product_id"])
    log(name, "lines without a valid order/product removed", orphan.sum())
    return order_items[~orphan].copy()


def clean_reviews(reviews, order_items):
    name = "reviews"
    log(name, "duplicate reviews removed", reviews.duplicated("review_id").sum())
    reviews = reviews.drop_duplicates(subset="review_id").copy()

    invalid_rating = ~reviews["rating"].between(1, 5)
    log(name, "rating outside 1-5, reviews removed", invalid_rating.sum())
    reviews = reviews[~invalid_rating].copy()
    reviews["rating"] = reviews["rating"].astype(int)

    reviews["review_date"] = pd.to_datetime(reviews["review_date"], errors="coerce")
    reviews["review_text"] = reviews["review_text"].str.strip().replace("", pd.NA)

    valid_pairs = order_items.set_index(["order_id", "product_id"]).index
    review_pairs = pd.MultiIndex.from_frame(reviews[["order_id", "product_id"]])
    orphan = ~review_pairs.isin(valid_pairs)
    log(name, "reviews without a matching order line removed", orphan.sum())
    return reviews[~orphan].copy()


# ---------------------------------------------------------------------------
# Derived metrics and final checks
# ---------------------------------------------------------------------------
def add_metrics(order_items, orders, products):
    order_items["cost_price"] = order_items["product_id"].map(products.set_index("product_id")["cost_price"])
    order_items["gross_sales"] = order_items["quantity"] * order_items["unit_price"]
    order_items["discount_amount"] = order_items["gross_sales"] * order_items["discount"]
    order_items["revenue"] = order_items["gross_sales"] - order_items["discount_amount"]
    order_items["cost"] = order_items["quantity"] * order_items["cost_price"]
    order_items["profit"] = order_items["revenue"] - order_items["cost"]
    order_items["profit_margin"] = order_items["profit"] / order_items["revenue"]
    order_items = order_items.drop(columns="cost_price")

    money_columns = ["gross_sales", "discount_amount", "revenue", "cost", "profit"]
    order_items[money_columns] = order_items[money_columns].round(2)
    order_items["profit_margin"] = order_items["profit_margin"].round(4)

    orders["order_revenue"] = orders["order_id"].map(order_items.groupby("order_id")["revenue"].sum()).fillna(0).round(2)
    return order_items, orders


def fix_signup_dates(customers, orders):
    """A customer cannot sign up after their first order."""
    first_order = customers["customer_id"].map(orders.groupby("customer_id")["order_date"].min().dt.normalize())
    wrong = customers["signup_date"] > first_order
    log("customers", "signup_date after first order, set to first order date", wrong.sum())
    customers.loc[wrong, "signup_date"] = first_order[wrong]
    return customers


def run_checks(customers, products, orders, order_items, reviews):
    assert customers["customer_id"].is_unique and products["product_id"].is_unique
    assert orders["order_id"].is_unique and reviews["review_id"].is_unique
    assert not order_items.duplicated(["order_id", "product_id"]).any()
    assert orders["customer_id"].isin(customers["customer_id"]).all()
    assert order_items["order_id"].isin(orders["order_id"]).all()
    assert order_items["product_id"].isin(products["product_id"]).all()
    assert (order_items["quantity"] > 0).all()
    assert order_items["discount"].between(0, 1).all()
    assert (order_items["revenue"] > 0).all() and (orders["order_revenue"] > 0).all()
    assert reviews["rating"].between(1, 5).all()
    assert (orders["delivery_days"].dropna() >= 0).all()
    assert customers["state"].notna().all() and orders["shipping_state"].notna().all()
    assert products["category"].nunique() == 8
    print("\nAll validation checks passed.")


def save_tables(customers, products, orders, order_items, reviews):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")
    orders["delivery_date"] = orders["delivery_date"].dt.strftime("%Y-%m-%d")
    reviews["review_date"] = reviews["review_date"].dt.strftime("%Y-%m-%d")

    tables = {"customers": customers, "products": products, "orders": orders,
              "order_items": order_items, "reviews": reviews}
    for table_name, table in tables.items():
        table.to_csv(PROCESSED_DIR / f"{table_name}.csv", index=False)
        print(f"Saved data/processed/{table_name}.csv ({len(table):,} rows)")


def main():
    names = ["customers", "products", "orders", "order_items", "reviews"]
    raw = {name: pd.read_csv(RAW_DIR / f"{name}.csv") for name in names}

    print("=== Inspecting raw data ===")
    for name, table in raw.items():
        inspect_table(name, table)

    print("\n=== Cleaning ===")
    customers = clean_customers(raw["customers"])
    products = clean_products(raw["products"])
    orders = clean_orders(raw["orders"], customers)
    order_items = clean_order_items(raw["order_items"], orders, products)
    reviews = clean_reviews(raw["reviews"], order_items)

    has_lines = orders["order_id"].isin(order_items["order_id"])
    log("orders", "orders left without any order line, removed", (~has_lines).sum())
    orders = orders[has_lines].copy()

    customers = fix_signup_dates(customers, orders)
    order_items, orders = add_metrics(order_items, orders, products)

    run_checks(customers, products, orders, order_items, reviews)
    save_tables(
        customers[["customer_id", "customer_name", "email", "city", "state", "signup_date", "customer_segment"]],
        products[["product_id", "product_name", "category", "subcategory", "unit_price", "cost_price"]],
        orders[["order_id", "customer_id", "order_date", "order_status", "payment_method", "shipping_city",
                "shipping_state", "delivery_date", "delivery_days", "order_revenue"]],
        order_items, reviews)

    REPORTS_DIR.mkdir(exist_ok=True)
    pd.DataFrame(cleaning_log).to_csv(REPORTS_DIR / "cleaning_log.csv", index=False)


if __name__ == "__main__":
    main()
