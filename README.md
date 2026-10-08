# E-Commerce Sales & Customer Analytics

An end-to-end data analyst project: generate and clean a realistic e-commerce dataset, analyse it with **SQL (PostgreSQL)** and **Python**, summarise it in **Excel**, and prepare a **Power BI** dashboard model.

> **The data is synthetic.** All customers, products, orders and numbers were generated with Python for portfolio and learning purposes. No real company or person is represented, and no real dataset was downloaded.

## Overview

A fictional online store sells 5,000 products in 8 categories to 20,000 customers across 21 Indian states and union territories. The dataset has 99,830 orders from 1 January to 31 December 2025. The project follows the work of a data analyst: raw data with quality problems, cleaning, business KPIs, trends, customer and product analysis, and recommendations.

## Business Problem

The company wants to know how much it earns, which categories, products and locations perform best, how discounts affect sales, how well it delivers, who its best customers are, and what it should do to improve revenue and customer experience.

## Objectives

- Clean raw transactional data and document every fix
- Calculate business KPIs (revenue, profit, margin, orders, average order value, customers)
- Find trends and weak spots in sales, products, customers and delivery
- Query the data with PostgreSQL and answer 20 business questions
- Build an Excel workbook and a Power BI-ready star schema
- Turn the numbers into findings and recommendations

## Tech Stack

PostgreSQL | SQL | Python | Pandas | NumPy | Matplotlib | Seaborn | Excel (openpyxl) | Power BI (model, DAX, layout guide) | Git/GitHub

## Dataset

| Table | Rows (clean) | Main columns |
|---|---|---|
| customers | 20,000 | customer_id, name, email, city, state, signup_date, customer_segment |
| products | 5,000 | product_id, name, category, subcategory, unit_price, cost_price |
| orders | 99,830 | order_id, customer_id, order_date, order_status, payment_method, shipping city/state, delivery_date |
| order_items | 162,810 | order_id, product_id, quantity, unit_price, discount |
| reviews | 46,106 | review_id, order_id, customer_id, product_id, rating, review_date, review_text |

`customer_id`, `product_id` and `order_id` link the tables. Raw files in `data/raw/` contain small, intentional problems (duplicates, missing values, inconsistent spelling, invalid dates and ratings). Cleaned files in `data/processed/` add derived columns such as revenue, cost, profit and delivery days.

**Money formulas:** `revenue = quantity x unit_price x (1 - discount)`, `profit = revenue - quantity x cost_price`. **Sales** exclude orders with status Cancelled or Returned. Currency is INR.

## Project Architecture

```
src/01 generate data  ->  data/raw/  ->  src/02 clean data  ->  data/processed/
                                                                      |
        +-------------------+---------------------+-------------------+-------------------+
        |                   |                     |                                       |
   PostgreSQL           Python EDA           Excel workbook                      Power BI star schema
 (database/ + sql/)   (03, 04, 05 + charts)  (reports/*.xlsx)          (powerbi/data + DAX + layout guide)
        |                   |                     |                                       |
        +-------------------+---------------------+---------------------------------------+
                                       reports/business_insights.md
```

Each tool has its own job, so work is not repeated four times:

| Tool | Used for |
|---|---|
| Python | Data generation, cleaning, EDA, customer segmentation, product flags |
| SQL | Querying the database and answering the 20 business questions |
| Excel | Quick business summaries, formula-driven KPI sheets, product lookup |
| Power BI | Interactive dashboard model and visuals for business users |

## Repository Structure

```
ecommerce-sales-customer-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── data/
│   ├── raw/                       customers, products, orders, order_items, reviews (with data issues)
│   └── processed/                 cleaned tables + customer_summary.csv + product_summary.csv
├── database/
│   ├── schema.sql                 tables, keys, indexes, valid_sales view
│   ├── load_data.sql              loads the processed CSV files (psql)
│   └── setup_database.py          optional: same setup using Python and .env
├── sql/
│   ├── 01_data_quality.sql
│   ├── 02_sales_analysis.sql
│   ├── 03_customer_analysis.sql
│   ├── 04_product_analysis.sql
│   └── 05_business_questions.sql  the 20 business questions
├── src/
│   ├── common.py                  paths and small shared helpers
│   ├── 01_generate_data.py
│   ├── 02_clean_data.py
│   ├── 03_eda.py
│   ├── 04_customer_analysis.py
│   ├── 05_product_analysis.py
│   ├── 06_export_dashboard_data.py
│   └── 07_build_excel_report.py
├── notebooks/
│   └── ecommerce_eda.ipynb
├── reports/
│   ├── figures/                   15 charts (PNG)
│   ├── cleaning_log.csv           every cleaning fix with row counts
│   ├── business_insights.md
│   ├── project_report.md
│   └── ecommerce_analysis.xlsx
└── powerbi/
    ├── data/                      fact_orders + 4 dimension CSV files
    ├── data_model.md
    ├── dashboard_layout.md
    └── measures.dax
```

## Data Cleaning

`src/02_clean_data.py` loads the raw files, checks shape, data types, missing values and duplicates, fixes the problems, validates keys and ranges, adds derived metrics and writes `data/processed/`. Examples of what it fixes: 200 duplicate customers, 8,155 inconsistent status/payment/category values, 100 orders with impossible timestamps (removed), 282 delivery dates before the order date, 466 invalid ratings. The full list is in `reports/cleaning_log.csv`.

## SQL Analysis

PostgreSQL schema with primary keys, foreign keys, CHECK constraints and indexes. Queries use SELECT, WHERE, GROUP BY, ORDER BY, CASE, JOIN, LEFT JOIN, CTEs, aggregate functions, date functions and window functions (LAG, RANK, NTILE, ROW_NUMBER, SUM OVER). Every query has a comment with the business question above it.

## Python Analysis

- `03_eda.py`: headline numbers and 11 charts (trends, categories, products, states, status, delivery, ratings, discounts, order frequency, order value, cancellations)
- `04_customer_analysis.py`: customer table, simple CLV estimate and value segments (High Value, Regular, Occasional, At Risk, Inactive)
- `05_product_analysis.py`: product, category and subcategory performance, discount effect by category, products needing attention
- `notebooks/ecommerce_eda.ipynb`: readable walk-through from raw data to findings

No machine learning is used; this is a descriptive analytics project.

## Excel Analysis

`reports/ecommerce_analysis.xlsx` has 7 sheets: KPI_Summary, Dashboard_Data, Monthly_Sales, Category_Analysis, Product_Analysis, Customer_Analysis, Geography. Built with live formulas (SUMIFS, COUNTIFS, IF, RANK, INDEX/MATCH), a category-by-month pivot-style table, a product lookup box and reconciliation checks that confirm all sheets add up to the same revenue. Blue numbers are values from Python, black numbers are formulas. INDEX/MATCH is used for the lookup (works in every Excel version); the XLOOKUP version is shown as text in the sheet.

## Power BI Dashboard

**No `.pbix` file is included.** Power BI Desktop files could not be created in the environment used to build this repository, so the dashboard has to be built from the files in `powerbi/`:

- `powerbi/data/`: star schema CSV files (`fact_orders`, `dim_customer`, `dim_product`, `dim_date`, `dim_location`)
- `powerbi/data_model.md`: tables, relationships and import steps
- `powerbi/measures.dax`: 20 DAX measures (Total Revenue, Total Profit, Total Orders, Average Order Value, Total Customers, Profit Margin, Average Delivery Days, Repeat Customer Rate and more)
- `powerbi/dashboard_layout.md`: exactly how to build the 4 pages (Executive Overview, Product Performance, Customer Analytics, Operations)

**Star schema:** `fact_orders` (one row per order line) connects to `dim_customer`, `dim_product`, `dim_date` and `dim_location` through `customer_key`, `product_key`, `date_key` and `location_key`. All relationships are many-to-one with a single filter direction.

## Key KPIs

| KPI | Value |
|---|---|
| Total revenue | ₹554.7M (₹554,657,724) |
| Total profit | ₹102.8M |
| Profit margin | 18.5% |
| Valid orders (not cancelled/returned) | 91,641 |
| Average order value | ₹6,053 |
| Customers with a sale | 19,710 of 20,000 |
| Repeat customer rate | 81.8% |
| Average delivery time | 4.42 days (75.9% within 5 days) |
| Average rating | 3.92 |

## Business Questions

1. How much revenue is generated, and how much profit?
2. Which categories and products perform best?
3. Which states and cities generate the most revenue?
4. What is the average order value?
5. How does revenue change over time?
6. Which products and categories perform weakly?
7. How do discounts affect sales and margin?
8. How good is delivery performance?
9. Which customers are high-value, and who is at risk?
10. What actions can improve revenue and customer experience?

All 20 SQL queries answering these are in `sql/05_business_questions.sql`.

## Key Insights

- **Electronics** is 55.5% of revenue but has the lowest margin (9.0%). **Beauty** (47.5%) and **Fashion** (39.3%) have the highest.
- **Electronics discounts above 10% lose money** (margin -0.7% at 11-20% and -13.8% at 21-30%).
- **Oct-Nov brings 29.9% of annual revenue**, but delivery slows to 5.6 days (from 3.9) and only 54.7% of orders arrive within 5 days.
- **Late delivery lowers ratings:** 3.98 stars on time vs 3.74 when late.
- **Cash on Delivery** orders are cancelled 8.0% of the time vs 2.9% for other payment methods.
- **Top 20% of customers = 62.6% of revenue;** 1,959 repeat customers are At Risk.
- **Top 5 states = 51.1% of revenue.**

Full findings with evidence: [`reports/business_insights.md`](reports/business_insights.md). Full write-up: [`reports/project_report.md`](reports/project_report.md).

## Business Recommendations

1. Cap Electronics discounts at 10% and track Electronics margin monthly.
2. Move marketing spend towards Fashion and Beauty.
3. Prepare delivery capacity before October; give remote states a realistic delivery promise.
4. Offer a prepaid incentive to reduce Cash on Delivery cancellations.
5. Improve Fashion size guides to cut returns.
6. Run a loyalty programme for High Value customers and a win-back campaign for At Risk customers.
7. Delist products with no sales and review suppliers of the lowest-rated subcategories.

## How to Run

You need Python 3.10 or newer. PostgreSQL is only needed for the SQL part. The CSV files, charts, Excel workbook and Power BI data are already included, so you can browse everything without running anything.

```bash
git clone <your-repository-url>
cd ecommerce-sales-customer-analytics

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/01_generate_data.py     # data/raw/ (re-creates the same data, seed 42)
python src/02_clean_data.py        # data/processed/ + reports/cleaning_log.csv
python src/03_eda.py               # charts in reports/figures/
python src/04_customer_analysis.py # customer_summary.csv + 2 charts
python src/05_product_analysis.py  # product_summary.csv + 2 charts
python src/06_export_dashboard_data.py   # powerbi/data/
python src/07_build_excel_report.py      # reports/ecommerce_analysis.xlsx
```

Run the scripts in this order, from any folder. Open the notebook with `jupyter notebook notebooks/ecommerce_eda.ipynb`.

## PostgreSQL Setup

Run these from the **project root** (the `\copy` paths in `load_data.sql` are relative):

```bash
createdb -U postgres ecommerce_analytics
psql -U postgres -d ecommerce_analytics -f database/schema.sql
psql -U postgres -d ecommerce_analytics -f database/load_data.sql

psql -U postgres -d ecommerce_analytics -f sql/01_data_quality.sql
psql -U postgres -d ecommerce_analytics -f sql/02_sales_analysis.sql
psql -U postgres -d ecommerce_analytics -f sql/03_customer_analysis.sql
psql -U postgres -d ecommerce_analytics -f sql/04_product_analysis.sql
psql -U postgres -d ecommerce_analytics -f sql/05_business_questions.sql
```

`load_data.sql` ends with row counts that should be 20,000 customers, 5,000 products, 99,830 orders, 162,810 order items and 46,106 reviews.

**Alternative (no psql needed):** copy `.env.example` to `.env`, put your password in `DB_PASSWORD`, then run `python database/setup_database.py`. It creates the database, runs the schema and loads the files. `.env` is ignored by Git.

## Python Setup

```bash
pip install -r requirements.txt
```

Libraries: pandas, numpy, matplotlib, seaborn, openpyxl (Excel), psycopg2-binary and python-dotenv (only for `database/setup_database.py`), notebook and ipykernel (only for the notebook).

## Power BI Setup

1. Install Power BI Desktop and load the 5 CSV files from `powerbi/data/`.
2. Follow `powerbi/data_model.md` (data types, date table, relationships).
3. Paste the measures from `powerbi/measures.dax`.
4. Build the pages with `powerbi/dashboard_layout.md`.
5. Check your totals against the table in that guide (revenue 554,657,723.90, profit 102,787,209.56, 91,641 orders, 19,710 customers).

## Project Workflow

1. Generate synthetic raw data with realistic relationships and a few quality problems
2. Inspect and clean the data, validate relationships, add revenue, cost and profit
3. Load into PostgreSQL and answer business questions with SQL
4. Explore with Python (EDA, customer segments, product flags)
5. Summarise in Excel and prepare the Power BI star schema
6. Write findings and recommendations from the calculated results

## Skills Demonstrated

- Data cleaning and validation with Pandas
- Writing PostgreSQL schemas and analytical queries (joins, CTEs, window functions)
- Exploratory data analysis and clear charts with Matplotlib and Seaborn
- Business KPIs, customer segmentation and product performance analysis
- Excel formulas (SUMIFS, COUNTIFS, INDEX/MATCH, IF, RANK) and reconciliation checks
- Star-schema design and DAX measures for Power BI
- Turning data into recommendations; Git/GitHub project organisation

## Tested

| Part | Result |
|---|---|
| Python scripts 01-07 | Ran end to end; outputs checked |
| Notebook | Executed top to bottom without errors |
| PostgreSQL 16 | `schema.sql`, `load_data.sql` and all 5 SQL files ran without errors; `database/setup_database.py` also tested |
| SQL vs Python | Revenue, profit, order, customer and at-risk counts match |
| Excel | Recalculated with LibreOffice, 0 formula errors, all reconciliation checks OK |
| Power BI / DAX | **Not tested.** No Power BI Desktop was available. DAX measures were written to match the data model but never executed |

## Limitations

- The data is synthetic: patterns such as COD cancellations, festive delivery delays and the discount effect were built into the generator, so the findings demonstrate the method, not real market behaviour.
- One year of data only; no year-on-year view.
- The 5-day delivery target and the CLV formula are simple assumptions.
- The Excel file uses pivot-style formula tables instead of real PivotTables.
- No `.pbix` file is included and the DAX was not executed.

## Future Improvements

- Repeat the analysis on a real public e-commerce dataset
- Add monthly revenue forecasting and a significance test for discount effects
- Add RFM quintile scoring, cohort retention and market-basket analysis
- Build the Power BI report and add screenshots here
- Automate the pipeline and the PostgreSQL load

## Author

**Archita**, B.Tech student in Artificial Intelligence, building a Data Analyst portfolio.
