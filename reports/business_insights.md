# Business insights

Every number below is calculated from the project data (`data/processed/`) by the scripts in `src/` and the queries in `sql/`.
The data is **synthetic**, so the patterns reflect how the dataset was generated. The value of this document is the method: finding, evidence, implication and action.

Definitions: *sales* are order lines from orders that are not Cancelled or Returned; revenue = quantity x unit price x (1 - discount); profit = revenue - product cost; amounts in INR (M = million).

---

## 1. Electronics drives most revenue but earns a thin margin

**Finding:** Electronics is the largest category by far, but it is one of the least profitable per rupee sold.

**Evidence:** Electronics generated ₹307.6M (55.5% of revenue) at a 9.0% profit margin. It produced 26.9% of total profit. Home & Kitchen brought 19.3% of revenue at a 25.7% margin. The company-wide margin is 18.5%.

**Business implication:** A small change in Electronics pricing or discounting moves total profit more than any other category. The business depends on a category with little room for error.

**Recommendation:** Track Electronics margin as a separate KPI each month. Set a minimum margin per product before a discount is approved (see finding 3).

---

## 2. Fashion and Beauty earn far more profit per rupee of revenue

**Finding:** The highest-margin categories are small in revenue terms.

**Evidence:** Beauty & Personal Care has a 47.5% margin and Fashion 39.3%. Fashion is 10.9% of revenue but 23.2% of profit. Beauty is 3.7% of revenue and 9.5% of profit.

**Business implication:** Growing Fashion and Beauty sales adds more profit than the same revenue growth in Electronics or Grocery (10.8% margin).

**Recommendation:** Shift part of the marketing budget towards Fashion and Beauty, and bundle low-ticket Beauty items with Electronics orders.

---

## 3. Discounts above 10% on Electronics lose money

**Finding:** Deep discounts are profitable in most categories but not in Electronics.

**Evidence:** Electronics margin by discount band: 0% discount 16.4%, 1-10% 9.7%, 11-20% -0.7%, 21-30% -13.8%. 61.4% of Electronics order lines sold with more than 10% discount made a loss, and these lines are 23.5% of Electronics revenue. Across all categories, margin falls from 23.7% (no discount) to 11.8% (21-30% discount) while the average quantity per line only rises from 1.61 to 1.68.

**Business implication:** Extra units sold because of a discount do not pay for the lost margin. The "Over 30%" band looks better (16.1%) only because those discounts are given on Fashion and Toys items, which start with higher margins than Electronics. It is a category-mix effect, not proof that deep discounts work.

**Recommendation:** Cap Electronics discounts at 10% unless the product has a margin above the discount. Keep promotional depth for Fashion and Beauty, and review the result after one festive season.

---

## 4. The festive season carries the year, and delivery breaks down in it

**Finding:** October and November bring a large share of revenue, and delivery speed drops in exactly those months.

**Evidence:** Oct-Nov revenue was ₹165.8M, which is 29.9% of the year from 2 of 12 months. Monthly revenue grew from ₹25.4M in January to a peak of ₹85.8M in November. Average delivery time was 5.6 days for Oct-Nov orders against 3.9 days for Jan-Sep orders. Orders delivered within 5 days fell from 84.4% to 54.7%.

**Business implication:** The busiest and most valuable period is when customers have the worst delivery experience.

**Recommendation:** Plan courier capacity and warehouse staffing for October before the sale starts, and show realistic delivery dates during the festive period.
*(Note: December delivery averages look fast only because orders still in transit on 31 Dec are not counted as delivered yet.)*

---

## 5. Late delivery lowers customer ratings

**Finding:** Ratings fall as delivery gets slower.

**Evidence:** Average rating is 3.92 overall. Reviews on orders delivered within 5 days average 3.98; orders delivered after 5 days average 3.74; orders that took more than 8 days average 3.44. 6.4% of reviews are 1 or 2 stars.

**Business implication:** Delivery delays reduce customer satisfaction even when the product is good.

**Recommendation:** Track "% delivered within 5 days" next to revenue on the dashboard, and proactively message customers when an order will miss the promised date.

---

## 6. Remote states wait longest and almost never meet the 5-day target

**Finding:** A group of smaller states has much slower delivery than the rest of the country.

**Evidence:** For Jan-Sep orders (before the festive slowdown), Jammu & Kashmir, Jharkhand, Goa, Uttarakhand, Assam average 7.0 to 7.2 days, and only 10% to 14% of orders arrive within 5 days. Together these five states bring 4.7% of revenue.

**Business implication:** These customers are a small but real part of revenue and get a much worse service.

**Recommendation:** Negotiate a regional courier partner for these states, or give them a realistic 7-day delivery promise instead of 5.

---

## 7. Cash on Delivery orders are cancelled almost three times as often

**Finding:** Payment method is a strong predictor of cancellation.

**Evidence:** Cash on Delivery (COD) is 17.2% of orders but has an 8.0% cancellation rate, against 2.9% for all other payment methods. COD accounts for 1,367 of the 3,759 cancelled orders (36%). Cancelled and returned orders together represent ₹52.5M of order value (₹21.8M cancelled, ₹30.7M returned).

**Business implication:** COD orders cost shipping and handling effort and then often produce no sale.

**Recommendation:** Offer a small prepaid discount (for example on UPI), and add order confirmation by SMS for high-value COD orders.

---

## 8. Fashion has the highest return rate

**Finding:** Fashion orders come back almost twice as often as other categories.

**Evidence:** Return rate among delivered orders is 7.4% for Fashion against an average of 4.4% for the other seven categories. Fashion also has the highest average discount (18.0%).

**Business implication:** Returns erase part of Fashion's strong margin and add reverse-logistics cost.

**Recommendation:** Improve size guides and product photos, and check which Fashion subcategories drive returns before raising discounts further.

---

## 9. A small group of customers brings most of the revenue

**Finding:** Revenue is concentrated in the best customers.

**Evidence:** The top 20% of buyers bring 62.6% of revenue and the top 10% bring 42.4%. The High Value segment (buyers with at least ₹71,943 revenue in the year) is 9.6% of customers but 41.4% of revenue, with 13.0 orders per customer on average. Premium-plan customers place 7.0 orders each against 3.5 for Students.

**Business implication:** Losing a few High Value customers hurts more than losing many Occasional ones.

**Recommendation:** Create a loyalty or early-access programme for the High Value segment and assign it a retention KPI.

---

## 10. Almost 2,000 repeat customers are going quiet

**Finding:** A group of customers who used to buy several times has stopped.

**Evidence:** 1,959 customers (9.8%) are "At Risk": 2 or more orders but nothing in the last 120 days. They brought ₹33.1M so far. 81.8% of buyers ordered at least twice, so repeat behaviour is strong and the lapsed group is worth winning back.

**Business implication:** These customers already know the shop and have a proven buying habit, so winning them back is cheaper than finding new customers.

**Recommendation:** Send a win-back offer to the At Risk list (available in `data/processed/customer_summary.csv` and the Power BI customer page).

---

## 11. Sales are concentrated in a few states

**Finding:** Half of revenue comes from five states.

**Evidence:** The top 5 states bring 51.1% of revenue and the top 3 bring 34.5%. Maharashtra alone is 15.6%. At the other end, Jammu & Kashmir brings ₹3.0M.

**Business implication:** Regional demand shocks, courier problems or competitors in a few states would affect the whole business.

**Recommendation:** Run a targeted campaign in mid-size states (for example Rajasthan, Telangana, Kerala) where demand already exists but share is lower.

---

## 12. Some products and subcategories need attention

**Finding:** A long tail of products sells nothing or loses money, and three subcategories have low ratings.

**Evidence:** 155 of 5,000 products had no sales in the year, 483 more are in the bottom 10% of selling products (together under 0.2% of revenue) and 17 products lost money overall. The lowest-rated subcategories (at least 200 reviews) are Remote Control Toys (3.39), Footwear (3.40) and Smart Watches (3.41), against 3.92 overall.

**Business implication:** The weak tail adds catalogue and storage cost without adding revenue. Low ratings in Footwear and Smart Watches affect sizeable revenue streams.

**Recommendation:** Review or delist the products with no sales, stop discounting the loss-making ones, and start a supplier quality review for the three low-rated subcategories.
