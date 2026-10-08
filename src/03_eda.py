"""Step 3: exploratory data analysis. Prints key numbers and saves charts to reports/figures/."""
import matplotlib.pyplot as plt
import seaborn as sns

from common import (DELIVERY_SLA_DAYS, MAIN_COLOR, NON_SALE_STATUSES, add_discount_band, build_sales_table,
                    load_processed, million_formatter, save_figure)


def print_headline_numbers(sales):
    order_values = sales.groupby("order_id")["revenue"].sum()
    print("Total revenue  :", round(sales["revenue"].sum()))
    print("Total profit   :", round(sales["profit"].sum()))
    print("Profit margin  :", round(sales["profit"].sum() / sales["revenue"].sum() * 100, 1), "%")
    print("Valid orders   :", sales["order_id"].nunique())
    print("Customers      :", sales["customer_id"].nunique())
    print("Average order value:", round(order_values.mean()), "| median:", round(order_values.median()))
    print("Order value 90th percentile:", round(order_values.quantile(0.9)))


def plot_monthly_trend(sales):
    monthly = sales.groupby("order_month").agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
    labels = monthly.index.strftime("%b")
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(labels, monthly["revenue"], marker="o", color=MAIN_COLOR)
    axes[0].yaxis.set_major_formatter(million_formatter)
    axes[0].set_title("Monthly revenue")
    axes[1].bar(labels, monthly["orders"], color="#6baed6")
    axes[1].set_title("Monthly orders")
    print("\nMonthly revenue (millions):\n", (monthly["revenue"] / 1e6).round(1).to_string())
    save_figure("01_monthly_revenue_and_orders.png")


def plot_category_revenue(sales):
    by_category = sales.groupby("category").agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    by_category["margin_pct"] = by_category["profit"] / by_category["revenue"] * 100
    by_category = by_category.sort_values("revenue")
    print("\nCategory performance:\n", by_category.round(1).sort_values("revenue", ascending=False).to_string())

    ax = by_category["revenue"].plot.barh(color=MAIN_COLOR, figsize=(9, 5))
    ax.xaxis.set_major_formatter(million_formatter)
    labels = [f"{r / 1e6:.0f}M  (margin {m:.0f}%)" for r, m in zip(by_category["revenue"], by_category["margin_pct"])]
    ax.bar_label(ax.containers[0], labels=labels, padding=4)
    ax.set_xlim(0, by_category["revenue"].max() * 1.45)
    ax.set_title("Revenue by category")
    ax.set_ylabel("")
    save_figure("02_revenue_by_category.png")


def plot_top_products(sales):
    top = sales.groupby("product_name")["revenue"].sum().nlargest(10).sort_values()
    print("\nTop 10 products by revenue (millions):\n", (top.sort_values(ascending=False) / 1e6).round(2).to_string())
    ax = top.plot.barh(color=MAIN_COLOR, figsize=(9, 5))
    ax.xaxis.set_major_formatter(million_formatter)
    ax.set_title("Top 10 products by revenue")
    ax.set_ylabel("")
    save_figure("03_top_10_products.png")


def plot_state_revenue(sales):
    top = sales.groupby("shipping_state")["revenue"].sum().nlargest(10).sort_values()
    print("\nTop states share of revenue (%):\n", (top.sort_values(ascending=False) / sales["revenue"].sum() * 100).round(1).to_string())
    ax = top.plot.barh(color=MAIN_COLOR, figsize=(9, 5))
    ax.xaxis.set_major_formatter(million_formatter)
    ax.set_title("Top 10 states by revenue")
    ax.set_ylabel("")
    save_figure("04_revenue_by_state.png")


def plot_order_status(orders):
    status_counts = orders["order_status"].value_counts()
    print("\nOrder status (%):\n", (status_counts / len(orders) * 100).round(1).to_string())
    ax = status_counts.plot.bar(color=MAIN_COLOR, figsize=(8, 5), rot=0)
    ax.bar_label(ax.containers[0], labels=[f"{c / len(orders) * 100:.1f}%" for c in status_counts])
    ax.set_title("Order status distribution (all orders)")
    ax.set_xlabel("")
    save_figure("05_order_status_distribution.png")


def plot_delivery_time(orders):
    delivered = orders[(orders["order_status"] == "Delivered") & orders["delivery_days"].notna()]
    on_time = (delivered["delivery_days"] <= DELIVERY_SLA_DAYS).mean() * 100
    print(f"\nAverage delivery days: {delivered['delivery_days'].mean():.2f}")
    print(f"Delivered within {DELIVERY_SLA_DAYS} days: {on_time:.1f}%")

    by_month = delivered.groupby(delivered["order_date"].dt.month)["delivery_days"].mean()
    print("Average delivery days by month:\n", by_month.round(2).to_string())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.histplot(delivered["delivery_days"], discrete=True, color=MAIN_COLOR, ax=axes[0])
    axes[0].set_xlabel("Delivery days")
    axes[0].axvline(DELIVERY_SLA_DAYS + 0.5, color="red", linestyle="--", label=f"{DELIVERY_SLA_DAYS}-day target")
    axes[0].set_title("Delivery time (days)")
    axes[0].legend()
    axes[1].plot(by_month.index, by_month.values, marker="o", color=MAIN_COLOR)
    axes[1].set_title("Average delivery days by order month")
    axes[1].set_xlabel("Month")
    save_figure("06_delivery_time.png")


def plot_ratings(reviews):
    counts = reviews["rating"].value_counts().sort_index()
    print(f"\nAverage rating: {reviews['rating'].mean():.2f} from {len(reviews):,} reviews")
    ax = counts.plot.bar(color=MAIN_COLOR, figsize=(8, 5), rot=0)
    ax.bar_label(ax.containers[0])
    ax.set_title("Rating distribution")
    ax.set_xlabel("Rating")
    save_figure("07_rating_distribution.png")


def plot_discount_effect(sales):
    sales = add_discount_band(sales.copy())
    by_band = sales.groupby("discount_band", observed=True).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), avg_quantity=("quantity", "mean"), lines=("order_id", "size"))
    by_band["margin_pct"] = by_band["profit"] / by_band["revenue"] * 100
    print("\nDiscount band analysis:\n", by_band.round(2).to_string())

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(by_band.index.astype(str), by_band["revenue"], color="#6baed6")
    ax.yaxis.set_major_formatter(million_formatter)
    ax.set_ylabel("Revenue")
    ax2 = ax.twinx()
    ax2.plot(by_band.index.astype(str), by_band["margin_pct"], color="red", marker="o")
    ax2.set_ylabel("Profit margin %")
    ax2.grid(False)
    ax.set_title("Revenue (bars) and profit margin (line) by discount band")
    save_figure("08_discount_vs_revenue.png")


def plot_order_frequency(sales):
    orders_per_customer = sales.groupby("customer_id")["order_id"].nunique()
    print(f"\nCustomers with 2+ orders: {(orders_per_customer >= 2).mean() * 100:.1f}%")
    print("Orders per customer: mean", round(orders_per_customer.mean(), 2), "| median", orders_per_customer.median())
    ax = orders_per_customer.clip(upper=15).value_counts().sort_index().plot.bar(color=MAIN_COLOR, figsize=(9, 5))
    ax.set_title("Customer order frequency (15 = 15 or more orders)")
    ax.set_xlabel("Orders per customer")
    ax.set_ylabel("Customers")
    save_figure("09_customer_order_frequency.png")


def plot_order_value(sales):
    order_values = sales.groupby("order_id")["revenue"].sum()
    clipped = order_values[order_values <= order_values.quantile(0.99)]
    ax = sns.histplot(clipped, bins=50, color=MAIN_COLOR)
    ax.axvline(order_values.mean(), color="red", linestyle="--", label=f"Mean ₹{order_values.mean():,.0f}")
    ax.axvline(order_values.median(), color="green", linestyle="--", label=f"Median ₹{order_values.median():,.0f}")
    ax.legend()
    ax.set_title("Order value distribution (top 1% hidden)")
    ax.set_xlabel("Order value (₹)")
    save_figure("10_order_value_distribution.png")


def plot_cancellation_by_payment(orders):
    rates = orders.groupby("payment_method")["order_status"].agg(
        cancelled=lambda s: (s == "Cancelled").mean() * 100, returned=lambda s: (s == "Returned").mean() * 100)
    rates = rates.sort_values("cancelled", ascending=False)
    print("\nCancellation and return rate by payment method (%):\n", rates.round(1).to_string())
    ax = rates.plot.bar(figsize=(9, 5), rot=20, color=["#d95f02", "#7570b3"])
    ax.set_title("Cancellation and return rate by payment method")
    ax.set_ylabel("% of orders")
    ax.set_xlabel("")
    save_figure("11_cancellation_by_payment_method.png")


def main():
    _, _, orders, _, reviews = load_processed()
    sales = build_sales_table(valid_only=True)
    print(f"Orders: {len(orders):,} | valid sales order lines: {len(sales):,}")
    print(f"(Sales exclude orders with status {', '.join(NON_SALE_STATUSES)})\n")

    print_headline_numbers(sales)
    plot_monthly_trend(sales)
    plot_category_revenue(sales)
    plot_top_products(sales)
    plot_state_revenue(sales)
    plot_order_status(orders)
    plot_delivery_time(orders)
    plot_ratings(reviews)
    plot_discount_effect(sales)
    plot_order_frequency(sales)
    plot_order_value(sales)
    plot_cancellation_by_payment(orders)


if __name__ == "__main__":
    main()
