"""Step 5: product and category analysis.

Output: data/processed/product_summary.csv (one row per product, with an attention flag)
"""
import matplotlib.pyplot as plt

from common import MAIN_COLOR, PROCESSED_DIR, add_discount_band, build_sales_table, load_processed, save_figure

LOW_REVENUE_PERCENTILE = 0.10   # bottom 10% of selling products are flagged as low revenue


def build_product_summary(products, sales, reviews):
    per_product = sales.groupby("product_id").agg(
        quantity_sold=("quantity", "sum"), orders=("order_id", "nunique"), gross_sales=("gross_sales", "sum"),
        discount_amount=("discount_amount", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
    ratings = reviews.groupby("product_id")["rating"].agg(avg_rating="mean", review_count="size")

    summary = products.merge(per_product, on="product_id", how="left").merge(ratings, on="product_id", how="left")
    summary[["quantity_sold", "orders", "gross_sales", "discount_amount", "revenue", "profit"]] = summary[
        ["quantity_sold", "orders", "gross_sales", "discount_amount", "revenue", "profit"]].fillna(0)
    summary["review_count"] = summary["review_count"].fillna(0).astype(int)

    summary["avg_selling_price"] = (summary["revenue"] / summary["quantity_sold"]).round(2)
    summary["avg_discount_pct"] = (summary["discount_amount"] / summary["gross_sales"] * 100).round(1)
    summary["profit_margin_pct"] = (summary["profit"] / summary["revenue"] * 100).round(1)
    summary["avg_rating"] = summary["avg_rating"].round(2)
    return summary


def flag_products_needing_attention(summary):
    selling = summary["revenue"] > 0
    low_revenue_cutoff = summary.loc[selling, "revenue"].quantile(LOW_REVENUE_PERCENTILE)
    summary["attention_reason"] = ""
    summary.loc[summary["revenue"] <= low_revenue_cutoff, "attention_reason"] = "Low revenue"
    summary.loc[summary["profit"] < 0, "attention_reason"] = "Loss-making"
    summary.loc[~selling, "attention_reason"] = "No sales"
    print(f"Low revenue cutoff: products earning under {low_revenue_cutoff:,.0f} in the year")
    print("\nProducts needing attention:\n", summary["attention_reason"].replace("", "OK").value_counts().to_string())
    return summary


def build_category_table(summary, sales, all_sales):
    table = sales.groupby("category").agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), quantity=("quantity", "sum"),
        gross_sales=("gross_sales", "sum"), discount_amount=("discount_amount", "sum"))
    table["margin_pct"] = table["profit"] / table["revenue"] * 100
    table["revenue_share_pct"] = table["revenue"] / table["revenue"].sum() * 100
    table["avg_discount_pct"] = table["discount_amount"] / table["gross_sales"] * 100

    delivered_or_returned = all_sales[all_sales["order_status"].isin(["Delivered", "Returned"])]
    table["return_rate_pct"] = delivered_or_returned.groupby("category")["order_status"].apply(
        lambda s: (s == "Returned").mean() * 100)
    table["avg_rating"] = summary.groupby("category")["avg_rating"].mean()
    table = table.sort_values("revenue", ascending=False)
    print("\nCategory table:\n", table.drop(columns=["gross_sales", "discount_amount"]).round(1).to_string())
    return table


def print_subcategory_and_product_tables(summary, sales):
    sub = sales.groupby(["category", "subcategory"]).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    sub["margin_pct"] = sub["profit"] / sub["revenue"] * 100
    print("\nSubcategories, lowest revenue:\n", sub.nsmallest(5, "revenue").round(1).to_string())
    print("\nSubcategories, lowest margin:\n", sub.nsmallest(5, "margin_pct").round(1).to_string())

    selling = summary[summary["revenue"] > 0]
    columns = ["product_name", "category", "revenue", "profit", "profit_margin_pct", "quantity_sold", "avg_discount_pct"]
    print("\nTop 5 products by revenue:\n", selling.nlargest(5, "revenue")[columns].round(1).to_string(index=False))
    print("\nBottom 5 selling products by revenue:\n", selling.nsmallest(5, "revenue")[columns].round(1).to_string(index=False))
    print("\nHighest margin products (min 20 units sold):\n",
          selling[selling["quantity_sold"] >= 20].nlargest(5, "profit_margin_pct")[columns].round(1).to_string(index=False))
    return sub


def print_discount_by_category(sales):
    sales = add_discount_band(sales.copy())
    grouped = sales.groupby(["category", "discount_band"], observed=True).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    margin = (grouped["profit"] / grouped["revenue"] * 100).unstack().round(1)
    print("\nProfit margin % by category and discount band:\n", margin.to_string())

    electronics = sales[sales["category"] == "Electronics"]
    losing_lines = (electronics["profit"] < 0).mean() * 100
    print(f"\nElectronics order lines sold at a loss: {losing_lines:.1f}%")


def plot_category_charts(table):
    table = table.sort_values("margin_pct")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].barh(table.index, table["margin_pct"], color=MAIN_COLOR)
    axes[0].set_title("Profit margin % by category")
    axes[1].barh(table.index, table["return_rate_pct"], color="#d95f02")
    axes[1].set_title("Return rate % by category (delivered orders)")
    save_figure("14_category_margin_and_returns.png")


def plot_subcategories(sub):
    sub = sub.reset_index()
    plt.figure(figsize=(10, 6))
    plt.scatter(sub["revenue"] / 1e6, sub["margin_pct"], s=70, color=MAIN_COLOR)
    for _, row in sub.iterrows():
        plt.annotate(row["subcategory"], (row["revenue"] / 1e6, row["margin_pct"]), fontsize=7, xytext=(4, 3), textcoords="offset points")
    plt.xscale("log")
    plt.xlabel("Revenue (₹ millions, log scale)")
    plt.ylabel("Profit margin %")
    plt.title("Subcategories: revenue vs profit margin")
    save_figure("15_subcategory_revenue_vs_margin.png")


def main():
    _, products, _, _, reviews = load_processed()
    sales = build_sales_table(valid_only=True)
    all_sales = build_sales_table(valid_only=False)

    summary = build_product_summary(products, sales, reviews)
    summary = flag_products_needing_attention(summary)
    table = build_category_table(summary, sales, all_sales)
    sub = print_subcategory_and_product_tables(summary, sales)
    print_discount_by_category(sales)
    plot_category_charts(table)
    plot_subcategories(sub)

    summary.to_csv(PROCESSED_DIR / "product_summary.csv", index=False)
    print(f"\nSaved data/processed/product_summary.csv ({len(summary):,} products)")


if __name__ == "__main__":
    main()
