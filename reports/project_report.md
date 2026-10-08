# Project report: E-Commerce Sales & Customer Analytics

*Synthetic data created for portfolio and learning purposes. No real company or customers are described. Amounts in INR; M = million.*

## 1. Executive Summary

The fictional company sold ₹554.7M of goods in 2025 from 91,641 valid orders placed by 19,710 customers, with a profit margin of 18.5%.

- **Electronics** brings 55.5% of revenue but only a 9.0% margin; discounts above 10% on Electronics make a loss.
- **Fashion and Beauty** are small (14.6% of revenue together) but earn 32.7% of profit.
- **Oct-Nov** brings 29.9% of annual revenue, and delivery slows from 3.9 to 5.6 days in those months.
- **Cash on Delivery** orders are cancelled 8.0% of the time against 2.9% for other payment methods.
- The top 20% of buyers bring 62.6% of revenue, and 1,959 repeat customers are at risk of leaving.

The main actions are: cap Electronics discounts, prepare delivery capacity before the festive sale, discourage COD with a prepaid incentive, and run retention campaigns for High Value and At Risk customers.

## 2. Business Problem

The company wants to know: how much revenue it makes, which categories, products and locations perform best or worst, the average order value, how revenue changes over time, how discounts affect sales, how well it delivers, who its high-value customers are, and what actions will improve revenue and customer experience. Section 10 and `reports/business_insights.md` answer these using calculated results.

## 3. Dataset

Five related tables were generated with Python (`src/01_generate_data.py`, fixed random seed 42). Dates cover 1 Jan to 31 Dec 2025.

| Table | Raw rows | Clean rows | Description |
|---|---|---|---|
| customers | 20,200 | 20,000 | Name, email, city, state, signup date, plan segment |
| products | 5,015 | 5,000 | 8 categories, 33 subcategories, unit and cost price |
| orders | 100,300 | 99,830 | Status, payment method, shipping location, delivery date |
| order_items | 163,464 | 162,810 | Quantity, selling price, discount per product in an order |
| reviews | 46,803 | 46,106 | Ratings and review text on delivered orders |

Built-in relationships: delivery comes after the order, customers cannot order before signing up, heavy and light buyers exist, prices differ by category (Electronics expensive, Grocery cheap), costs give each category a different margin, reviews exist only for delivered orders, and festive months have more orders, deeper discounts and slower delivery.

## 4. Data Cleaning

A small number of problems were added to the raw files on purpose. `src/02_clean_data.py` inspects, fixes and counts them (full list in `reports/cleaning_log.csv`). Raw files are never changed.

| Table | Issue fixed | Rows |
|---|---|---|
| customers | city spelling/capitalisation fixed | 1,669 |
| customers | state spelling/capitalisation fixed | 405 |
| customers | segment capitalisation fixed | 100 |
| customers | missing segment filled with most common value | 100 |
| customers | missing email (left empty) | 302 |
| customers | duplicate customer records removed | 200 |
| products | category names standardised | 301 |
| products | duplicate products removed | 15 |
| products | missing cost_price estimated from category ratio | 20 |
| orders | duplicate orders removed | 300 |
| orders | order_status standardised | 5,398 |
| orders | payment_method standardised | 2,456 |
| orders | invalid order_date, orders removed | 100 |
| orders | delivery_date before order_date, set to empty | 282 |
| orders | delivered orders without delivery_date (kept, excluded from delivery stats) | 732 |
| orders | missing shipping_state filled from shipping_city | 499 |
| orders | orders with unknown customer removed | 0 |
| order_items | duplicate order lines removed | 326 |
| order_items | missing discount set to 0 | 815 |
| order_items | discount entered as percent (e.g. 15) converted to 0.15 | 223 |
| order_items | missing unit_price filled from products table | 489 |
| order_items | quantity zero or negative, lines removed | 163 |
| order_items | lines without a valid order/product removed | 165 |
| reviews | duplicate reviews removed | 139 |
| reviews | rating outside 1-5, reviews removed | 466 |
| reviews | reviews without a matching order line removed | 92 |
| orders | orders left without any order line, removed | 70 |
| customers | signup_date after first order, set to first order date | 60 |

After cleaning, the script checks primary keys, foreign keys, positive quantities, discount range 0 to 1, rating range 1 to 5, and that delivery is not before the order date.

Decisions worth explaining: missing delivery dates are kept empty (they are not guessed) and left out of delivery statistics; missing cost prices use the median cost ratio of the category; a customer cannot sign up after the first order, so such signup dates are replaced with the first order date.

## 5. SQL Analysis

PostgreSQL schema in `database/schema.sql` (primary keys, foreign keys, checks, indexes, and a `valid_sales` view that removes cancelled and returned orders). Queries in `sql/`:

| File | Purpose |
|---|---|
| 01_data_quality.sql | Row counts, orphan checks, formula checks |
| 02_sales_analysis.sql | Monthly growth (LAG), running totals, quarters, weekdays, festive vs normal, cancellation by payment method |
| 03_customer_analysis.sql | Lifetime revenue ranking, deciles (NTILE), one-time vs repeat buyers, days to second order, new vs returning revenue, at-risk count |
| 04_product_analysis.sql | Top products per category (ROW_NUMBER), margin tiers, never-sold products, discount bands, ratings and returns |
| 05_business_questions.sql | The 20 business questions, each with a comment |

SQL results match the Python results exactly (revenue ₹554,657,724, 91,641 orders, 19,710 customers, 1,959 at-risk customers).

## 6. Python EDA

`src/03_eda.py` prints key numbers and saves 11 charts to `reports/figures/` (monthly revenue and orders, category revenue and margin, top products, states, order status, delivery time, ratings, discount effect, order frequency, order value distribution, cancellations by payment method). The notebook `notebooks/ecommerce_eda.ipynb` shows the same story step by step.

Order value is very skewed: the average order is ₹6,053 but the median is only ₹2,052, because a few Electronics orders are very large.

## 7. Customer Analysis

`src/04_customer_analysis.py` builds one row per customer (orders, revenue, average order value, days since last order, a simple CLV estimate) and assigns a value segment. Rules are checked in this order:

1. **Inactive**: no valid order
2. **At Risk**: 2+ orders but last order more than 120 days before the end of the data
3. **High Value**: lifetime revenue in the top 10% of buyers (at least ₹71,943)
4. **Regular**: 3 or more orders
5. **Occasional**: everyone else

| Segment | Customers | % of customers | Revenue | % of revenue |
|---|---|---|---|---|
| High Value | 1,913 | 9.6% | ₹229.6M | 41.4% |
| Regular | 9,447 | 47.2% | ₹240.1M | 43.3% |
| Occasional | 6,391 | 32.0% | ₹51.9M | 9.4% |
| At Risk | 1,959 | 9.8% | ₹33.1M | 6.0% |
| Inactive | 290 | 1.5% | ₹0.0M | 0.0% |

CLV estimate = average order value x orders per year x profit margin x 3 years. It is a rough teaching formula, not a prediction.

## 8. Product Analysis

`src/05_product_analysis.py` summarises each product (revenue, profit, units, average selling price, average discount, margin, rating) and flags products needing attention.

| Category | Revenue | % of revenue | Profit | Margin | Return rate |
|---|---|---|---|---|---|
| Electronics | ₹307.6M | 55.5% | ₹27.7M | 9.0% | 5.5% |
| Home & Kitchen | ₹107.0M | 19.3% | ₹27.4M | 25.7% | 4.2% |
| Fashion | ₹60.5M | 10.9% | ₹23.8M | 39.3% | 7.4% |
| Sports & Fitness | ₹23.9M | 4.3% | ₹7.2M | 30.0% | 4.6% |
| Beauty & Personal Care | ₹20.6M | 3.7% | ₹9.8M | 47.5% | 4.2% |
| Grocery | ₹19.5M | 3.5% | ₹2.1M | 10.8% | 4.2% |
| Toys & Games | ₹8.7M | 1.6% | ₹2.6M | 30.0% | 4.0% |
| Books | ₹6.9M | 1.2% | ₹2.2M | 32.2% | 3.9% |

Products needing attention: 155 with no sales, 483 in the bottom 10% of selling products, 17 loss-making. Lowest margin subcategories are all in Electronics (Smart Watches, Mobile Accessories, Laptops).

## 9. Power BI Dashboard

No `.pbix` file is included. The repository contains clean star-schema CSV files in `powerbi/data/`, the data model, 20 ready-to-paste DAX measures and a page-by-page build guide for the four report pages (Executive Overview, Product Performance, Customer Analytics, Operations). See `powerbi/`.

## 10. Key Findings

1. Electronics = 55.5% of revenue at a 9.0% margin; Fashion and Beauty earn the best margins.
2. Electronics discounts above 10% lose money (-0.7% margin at 11-20%, -13.8% at 21-30%).
3. Oct-Nov = 29.9% of revenue and the slowest delivery (5.6 days, only 54.7% on time).
4. Late delivery lowers ratings (3.98 on time vs 3.74 late).
5. COD cancellation rate 8.0% vs 2.9%; Fashion return rate 7.4% vs 4.4%.
6. Top 5 states = 51.1% of revenue; top 20% of customers = 62.6%.

Details with evidence: `reports/business_insights.md`.

## 11. Business Recommendations

- Cap Electronics discounts at 10% and review Electronics margin monthly.
- Move marketing spend towards Fashion and Beauty.
- Prepare courier capacity before October and give remote states a realistic delivery promise.
- Offer a prepaid incentive to reduce Cash on Delivery cancellations.
- Improve size guides for Fashion to cut returns.
- Build a loyalty programme for High Value customers and a win-back campaign for At Risk customers.
- Delist products with no sales and review suppliers of the lowest-rated subcategories.

## 12. Limitations

- The data is synthetic. Patterns such as COD cancellations, festive delays and the discount effect were built into the generator, so these findings show the method, not real market behaviour.
- Only one year of data, so there is no year-on-year comparison and the growth trend is partly caused by customers joining during the year.
- Delivery SLA (5 days) and the CLV formula are simple assumptions.
- December delivery statistics are biased because orders still in transit are not yet counted.
- The Excel workbook uses pivot-style SUMIFS tables, not real PivotTables. XLOOKUP is not used (an INDEX/MATCH lookup is used instead, with the XLOOKUP formula shown as text).
- The Power BI dashboard was not built in this repository and the DAX measures were not executed. Review them in Power BI Desktop before publishing.

## 13. Future Improvements

- Replace the synthetic data with a real public dataset and compare the findings.
- Add a time-series forecast of monthly revenue and a statistical test for the discount effect.
- Add RFM scoring with quintiles, cohort retention tables and market-basket analysis.
- Build the Power BI file and add a screenshot to the README.
- Schedule the pipeline and load data into PostgreSQL automatically.
