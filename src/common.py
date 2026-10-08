"""Shared paths and small helpers used by the analysis scripts."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
POWERBI_DIR = BASE_DIR / "powerbi" / "data"

# Orders with these statuses are not counted as sales
NON_SALE_STATUSES = ["Cancelled", "Returned"]

# An order is "on time" if it is delivered within this many days
DELIVERY_SLA_DAYS = 5

sns.set_theme(style="whitegrid")
MAIN_COLOR = "#2a6f97"
million_formatter = FuncFormatter(lambda value, _: f"₹{value / 1e6:.0f}M")

DISCOUNT_BANDS = ["0%", "1-10%", "11-20%", "21-30%", "Over 30%"]


def load_processed():
    """Load the cleaned tables produced by 02_clean_data.py."""
    customers = pd.read_csv(PROCESSED_DIR / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(PROCESSED_DIR / "products.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders.csv", parse_dates=["order_date", "delivery_date"])
    order_items = pd.read_csv(PROCESSED_DIR / "order_items.csv")
    reviews = pd.read_csv(PROCESSED_DIR / "reviews.csv", parse_dates=["review_date"])
    return customers, products, orders, order_items, reviews


def build_sales_table(valid_only=True):
    """One row per order line, joined with order, product and customer details."""
    customers, products, orders, order_items, _ = load_processed()
    sales = order_items.merge(orders, on="order_id")
    sales = sales.merge(products[["product_id", "product_name", "category", "subcategory"]], on="product_id")
    sales = sales.merge(customers[["customer_id", "customer_segment"]], on="customer_id")
    sales["order_month"] = sales["order_date"].dt.to_period("M").dt.to_timestamp()
    if valid_only:
        sales = sales[~sales["order_status"].isin(NON_SALE_STATUSES)]
    return sales


def add_discount_band(df):
    """Group the discount rate into bands, e.g. 0.15 -> '11-20%'."""
    df["discount_band"] = pd.cut(df["discount"], bins=[-0.01, 0, 0.10, 0.20, 0.30, 1.0], labels=DISCOUNT_BANDS)
    return df


def save_figure(file_name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / file_name, dpi=130)
    plt.close()
    print(f"Saved reports/figures/{file_name}")
