# Power BI dashboard layout

No `.pbix` file is included in this repository. Power BI Desktop files cannot be created with the tools used to build this project, so the dashboard has to be built by following this guide (about 1 to 2 hours the first time).

**Before you start:** load the data and create the relationships ([data_model.md](data_model.md)), then add the measures ([measures.dax](measures.dax)).

**General settings**
- Canvas: 16:9, four pages, same page background on all pages.
- Colours: one main blue for bars/lines, orange/red only for problems (loss, late, cancelled).
- Add the same slicers on every page (sync them: View > Sync slicers): **Month** (`dim_date[month_year]`), **Category** (`dim_product[category]`), **State** (`dim_location[state]`).
- Currency: format money measures as Currency (INR) or use "Display units: Millions".

---

## Page 1: Executive Overview

**Card visuals (top row, one measure each)**

| Card | Measure |
|---|---|
| Total Revenue | `[Total Revenue]` |
| Total Profit | `[Total Profit]` |
| Total Orders | `[Total Orders]` |
| Average Order Value | `[Average Order Value]` |
| Customers | `[Total Customers]` |
| Profit Margin | `[Profit Margin]` (format as %) |

**Charts**

| Visual | Type | Axis / Legend | Values |
|---|---|---|---|
| Monthly Revenue | Line chart | `dim_date[month_year]` (sorted by month_number) | `[Total Revenue]` |
| Monthly Orders | Column chart | `dim_date[month_year]` | `[Total Orders]` |
| Revenue by Category | Bar chart | `dim_product[category]` | `[Total Revenue]` |
| Revenue by State | Filled map or bar chart (top 10) | `dim_location[state]` | `[Total Revenue]` |
| Top Products | Bar chart, filter **Top N = 10** by `[Total Revenue]` | `dim_product[product_name]` | `[Total Revenue]` |

---

## Page 2: Product Performance

| Visual | Type | Fields |
|---|---|---|
| Category revenue | Bar chart | Axis `dim_product[category]`, Values `[Total Revenue]` |
| Product revenue | Table, sorted by revenue | `dim_product[product_name]`, `[Total Revenue]`, `[Total Profit]`, `[Profit Margin]`, `[Units Sold]` |
| Profit by category | Clustered bar | Axis `dim_product[category]`, Values `[Total Profit]`, `[Profit Margin]` as a second visual or tooltip |
| Quantity sold | Column chart | Axis `dim_product[subcategory]`, Values `[Units Sold]` |
| Discount analysis | Scatter chart | Details `dim_product[category]`, X `[Average Discount %]`, Y `[Profit Margin]`, Size `[Total Revenue]` |

Tip: conditional formatting (Format > Cell elements > Background colour) on `[Profit Margin]` in the product table: red below 0.

---

## Page 3: Customer Analytics

| Visual | Type | Fields |
|---|---|---|
| Customer segments | Donut chart | Legend `dim_customer[value_segment]`, Values `[Total Customers]` |
| Revenue by segment | Column chart | Axis `dim_customer[value_segment]`, Values `[Total Revenue]` |
| Repeat customers | Two cards | `[Repeat Customers]` and `[Repeat Customer Rate]` |
| Customer revenue distribution | Column chart | Axis `dim_customer[total_revenue]` grouped in bins of 10,000 (right-click the field > New group > Bin), Values = count of `dim_customer[customer_key]` |
| Customer order frequency | Column chart | Axis `dim_customer[total_orders]` (bin size 1), Values = count of `dim_customer[customer_key]` |

These two charts use whole-year customer totals stored in `dim_customer`, so they do not react to the date slicer.

Add a table visual: `dim_customer[customer_name]`, `dim_customer[city]`, `[Total Revenue]`, `[Total Orders]`, filtered to `value_segment = "At Risk"` to give the marketing team a call list.

---

## Page 4: Operations

| Visual | Type | Fields |
|---|---|---|
| Delivery time | Card + column chart | Card `[Average Delivery Days]`; column chart axis `dim_date[month_name]`, values `[Average Delivery Days]` |
| Order status | Donut or bar chart | Legend `fact_orders[order_status]`, Values distinct count of `fact_orders[order_id]` |
| Delivery performance | Gauge or card | `[On-Time Delivery %]`, target 85% |
| Rating analysis | Column chart + card | Card `[Average Rating]`; chart axis `dim_product[category]`, values `[Average Rating]` |
| Cancellations by payment method | Bar chart | Axis `fact_orders[payment_method]`, Values `[Cancellation Rate]` |

The target of 85% for on-time delivery is an example. Change it to whatever the business wants.

---

## Checks after building

Select no filters and compare with the numbers in `reports/ecommerce_analysis.xlsx` (sheet KPI_Summary) and the SQL results:

| KPI | Expected |
|---|---|
| Total Revenue | 554,657,723.90 |
| Total Profit | 102,787,209.56 |
| Total Orders | 91,641 |
| Total Customers | 19,710 |

If your numbers differ, check that all measures filter on `is_valid_sale = 1` and that the relationships are many-to-one.
