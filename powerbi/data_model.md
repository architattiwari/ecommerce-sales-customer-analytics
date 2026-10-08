# Power BI data model

The dashboard uses a **star schema**: one fact table in the middle, four dimension tables around it.
All files are in [`powerbi/data/`](data/) and are created by `src/06_export_dashboard_data.py`.

```
                    dim_date
                       |
 dim_customer ---- fact_orders ---- dim_product
                       |
                  dim_location
```

## Tables

### fact_orders (162,810 rows)
**Grain: one row per order line** (an order with 3 products has 3 rows).

| Column | Meaning |
|---|---|
| order_id | Order number (repeats for each line of the same order) |
| customer_key, product_key, date_key, location_key | Keys to the four dimensions |
| order_status | Delivered, Shipped, Processing, Cancelled, Returned |
| payment_method | UPI, Credit Card, Debit Card, Cash on Delivery, Net Banking, Wallet |
| is_valid_sale | 1 if the order is not Cancelled/Returned, otherwise 0 |
| quantity, unit_price, discount | As sold. `discount` is a fraction (0.15 = 15%) |
| gross_sales | quantity x unit_price |
| discount_amount | gross_sales x discount |
| revenue | gross_sales - discount_amount |
| cost | quantity x product cost price |
| profit | revenue - cost |
| delivery_days | Days from order to delivery (empty if not delivered or date missing) |
| delivery_status | "On Time" (5 days or less) or "Late" for delivered orders |
| rating | Customer rating 1-5 for that product in that order (empty if no review) |

### dim_customer (20,000 rows)
customer_key, customer_id, customer_name, city, state, signup_date, **plan_segment** (Standard / Premium / Student / Business, chosen at signup), **value_segment** (High Value / Regular / Occasional / At Risk / Inactive, from `src/04_customer_analysis.py`), total_orders and total_revenue (valid sales, whole year), clv_estimate.

### dim_product (5,000 rows)
product_key, product_id, product_name, category, subcategory, unit_price, cost_price.

### dim_date (365 rows)
date_key (YYYYMMDD number), date, year, quarter, month_number, month_name, month_year, day_of_week, is_weekend.

### dim_location (37 rows)
location_key, city, state. `fact_orders[location_key]` is the **shipping** city/state of the order.

## Relationships

Create these in Model view (drag the key from the fact table to the dimension). All are **many-to-one**, **single direction** (dimension filters the fact).

| From (fact_orders) | To | Cardinality |
|---|---|---|
| customer_key | dim_customer[customer_key] | Many to one |
| product_key | dim_product[product_key] | Many to one |
| date_key | dim_date[date_key] | Many to one |
| location_key | dim_location[location_key] | Many to one |

## Import steps

1. Power BI Desktop > **Get data > Text/CSV**. Load the 5 files from `powerbi/data/`.
2. In Power Query check the data types:
   - `dim_date[date]` and `dim_customer[signup_date]` > **Date**
   - `unit_price`, `discount`, `gross_sales`, `discount_amount`, `revenue`, `cost`, `profit`, `total_revenue`, `clv_estimate` > **Decimal number**
   - all `*_key`, `date_key`, `quantity`, `delivery_days`, `is_valid_sale`, `total_orders` > **Whole number**
3. Select `dim_date` > **Table tools > Mark as date table** > choose `date`.
4. Sort `dim_date[month_name]` by `month_number` (Column tools > Sort by column) so months show Jan-Dec.
5. Create the relationships above, then add the measures from [`measures.dax`](measures.dax).

## Notes and assumptions

- Revenue, profit and orders always use `is_valid_sale = 1` inside the measures. A raw `SUM(fact_orders[revenue])` would include cancelled and returned orders.
- "On time" means delivered within 5 days. This is an assumption made for the project.
- Customer value segments, `total_orders` and `total_revenue` are calculated in Python for the whole year and stored in `dim_customer`, so they do not change when you filter by date.
