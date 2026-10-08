"""Step 4: customer analysis. Builds one row per customer and assigns simple value segments.

Output: data/processed/customer_summary.csv
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import MAIN_COLOR, PROCESSED_DIR, build_sales_table, load_processed, million_formatter, save_figure

AT_RISK_DAYS = 120      # repeat customer who has not ordered for this many days
REGULAR_MIN_ORDERS = 3  # 3+ orders = Regular
HIGH_VALUE_PERCENTILE = 0.90
LIFESPAN_YEARS = 3      # assumption used in the CLV estimate


def build_customer_summary(customers, sales):
    snapshot_date = sales["order_date"].max().normalize() + pd.Timedelta(days=1)
    per_customer = sales.groupby("customer_id").agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
    )
    summary = customers[["customer_id", "customer_name", "city", "state", "customer_segment"]].merge(
        per_customer, on="customer_id", how="left")
    summary["total_orders"] = summary["total_orders"].fillna(0).astype(int)
    summary[["total_revenue", "total_profit"]] = summary[["total_revenue", "total_profit"]].fillna(0)

    summary["avg_order_value"] = (summary["total_revenue"] / summary["total_orders"]).replace(np.inf, np.nan)
    summary["recency_days"] = (snapshot_date - summary["last_order_date"]).dt.days

    # CLV estimate = avg order value x orders per year x profit margin x expected lifespan
    overall_margin = sales["profit"].sum() / sales["revenue"].sum()
    summary["clv_estimate"] = (summary["avg_order_value"] * summary["total_orders"]
                               * overall_margin * LIFESPAN_YEARS).fillna(0).round(2)
    return summary


def assign_value_segments(summary):
    """Rules are checked in this order, the first match wins."""
    high_value_cutoff = summary.loc[summary["total_orders"] > 0, "total_revenue"].quantile(HIGH_VALUE_PERCENTILE)
    print(f"High Value cutoff (top 10% of buyers): revenue >= {high_value_cutoff:,.0f}")

    conditions = [
        summary["total_orders"] == 0,
        (summary["total_orders"] >= 2) & (summary["recency_days"] > AT_RISK_DAYS),
        summary["total_revenue"] >= high_value_cutoff,
        summary["total_orders"] >= REGULAR_MIN_ORDERS,
    ]
    labels = ["Inactive", "At Risk", "High Value", "Regular"]
    summary["value_segment"] = np.select(conditions, labels, default="Occasional")
    return summary


def print_customer_findings(summary):
    buyers = summary[summary["total_orders"] > 0]
    repeat_rate = (buyers["total_orders"] >= 2).mean() * 100
    print(f"\nCustomers with at least one valid order: {len(buyers):,}")
    print(f"Repeat purchase rate (2+ orders): {repeat_rate:.1f}%")
    print(f"Average orders per buyer: {buyers['total_orders'].mean():.2f}")

    sorted_revenue = buyers["total_revenue"].sort_values(ascending=False)
    top20_share = sorted_revenue.head(int(len(sorted_revenue) * 0.2)).sum() / sorted_revenue.sum() * 100
    print(f"Top 20% of buyers generate {top20_share:.1f}% of revenue")

    by_segment = summary.groupby("value_segment").agg(
        customers=("customer_id", "size"), revenue=("total_revenue", "sum"),
        avg_orders=("total_orders", "mean"), avg_order_value=("avg_order_value", "mean"),
        avg_recency_days=("recency_days", "mean"))
    by_segment["revenue_share_pct"] = by_segment["revenue"] / by_segment["revenue"].sum() * 100
    by_segment["customer_share_pct"] = by_segment["customers"] / by_segment["customers"].sum() * 100
    print("\nValue segments:\n", by_segment.round(1).sort_values("revenue", ascending=False).to_string())
    return by_segment


def plot_segments(by_segment):
    order = ["High Value", "Regular", "Occasional", "At Risk", "Inactive"]
    by_segment = by_segment.reindex(order)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(order, by_segment["customers"], color=MAIN_COLOR)
    axes[0].set_title("Customers by value segment")
    axes[1].bar(order, by_segment["revenue"], color="#6baed6")
    axes[1].yaxis.set_major_formatter(million_formatter)
    axes[1].set_title("Revenue by value segment")
    for ax in axes:
        ax.tick_params(axis="x", rotation=20)
    save_figure("12_customer_segments.png")


def plot_revenue_concentration(summary):
    revenue = summary.loc[summary["total_orders"] > 0, "total_revenue"].sort_values(ascending=False).to_numpy()
    cumulative_share = np.cumsum(revenue) / revenue.sum() * 100
    customer_share = np.arange(1, len(revenue) + 1) / len(revenue) * 100
    plt.figure(figsize=(8, 5))
    plt.plot(customer_share, cumulative_share, color=MAIN_COLOR)
    plt.axvline(20, color="grey", linestyle="--")
    plt.title("Share of revenue vs share of customers (best customers first)")
    plt.xlabel("% of customers")
    plt.ylabel("% of revenue")
    save_figure("13_customer_revenue_concentration.png")


def main():
    customers, _, _, _, _ = load_processed()
    sales = build_sales_table(valid_only=True)

    summary = build_customer_summary(customers, sales)
    summary = assign_value_segments(summary)
    by_segment = print_customer_findings(summary)
    plot_segments(by_segment)
    plot_revenue_concentration(summary)

    summary["first_order_date"] = summary["first_order_date"].dt.strftime("%Y-%m-%d")
    summary["last_order_date"] = summary["last_order_date"].dt.strftime("%Y-%m-%d")
    summary.to_csv(PROCESSED_DIR / "customer_summary.csv", index=False)
    print(f"\nSaved data/processed/customer_summary.csv ({len(summary):,} customers)")


if __name__ == "__main__":
    main()
