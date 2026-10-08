-- 05_business_questions.sql
-- The 20 business questions of the project, answered one by one.
-- "Sales" means order lines from orders that are NOT Cancelled or Returned (view: valid_sales).
-- All money is in Indian rupees (INR).

-- Q1: How much revenue is the company generating?
SELECT ROUND(SUM(revenue), 2) AS total_revenue
FROM valid_sales;

-- Q2: How much profit does that revenue leave after product costs? (and the profit margin)
SELECT ROUND(SUM(profit), 2) AS total_profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS profit_margin_pct
FROM valid_sales;

-- Q3: How many orders were placed, and how many of them count as sales?
SELECT COUNT(*) AS all_orders,
       COUNT(*) FILTER (WHERE order_status NOT IN ('Cancelled', 'Returned')) AS valid_orders
FROM orders;

-- Q4: How many customers do we have, and how many of them bought something?
SELECT (SELECT COUNT(*) FROM customers) AS registered_customers,
       (SELECT COUNT(DISTINCT customer_id) FROM valid_sales) AS customers_with_a_sale;

-- Q5: What is the average order value (revenue per valid order)?
SELECT ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM valid_sales;

-- Q6: How does revenue change month by month?
SELECT order_month, ROUND(SUM(revenue), 0) AS revenue
FROM valid_sales
GROUP BY order_month
ORDER BY order_month;

-- Q7: How many orders are placed each month?
SELECT order_month, COUNT(DISTINCT order_id) AS orders
FROM valid_sales
GROUP BY order_month
ORDER BY order_month;

-- Q8: Which 10 products earn the most revenue?
SELECT product_id, product_name, category,
       SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 0) AS revenue
FROM valid_sales
GROUP BY product_id, product_name, category
ORDER BY SUM(revenue) DESC
LIMIT 10;

-- Q9: Which categories earn the most revenue, and what share of the total is that?
SELECT category,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_total
FROM valid_sales
GROUP BY category
ORDER BY revenue DESC;

-- Q10: Which states generate the most revenue? (shipping state)
SELECT shipping_state,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_total
FROM valid_sales
GROUP BY shipping_state
ORDER BY revenue DESC
LIMIT 10;

-- Q11: Which categories perform weakly? (lowest revenue, and lowest profit margin)
SELECT category,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct,
       RANK() OVER (ORDER BY SUM(revenue)) AS revenue_rank_from_bottom,
       RANK() OVER (ORDER BY SUM(profit) / SUM(revenue)) AS margin_rank_from_bottom
FROM valid_sales
GROUP BY category
ORDER BY revenue;

-- Q12: Which products have the highest margin? (only products with at least 20 units sold)
SELECT product_id, product_name, category,
       SUM(quantity) AS units_sold,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct,
       ROUND(SUM(profit), 0) AS profit
FROM valid_sales
GROUP BY product_id, product_name, category
HAVING SUM(quantity) >= 20
ORDER BY margin_pct DESC
LIMIT 10;

-- Q13: Which customers have spent the most over the year?
SELECT c.customer_id, c.customer_name, c.city,
       COUNT(DISTINCT vs.order_id) AS orders,
       ROUND(SUM(vs.revenue), 0) AS lifetime_revenue
FROM valid_sales AS vs
JOIN customers AS c ON c.customer_id = vs.customer_id
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY SUM(vs.revenue) DESC
LIMIT 10;

-- Q14: How many customers are repeat customers (2 or more valid orders)?
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders
    FROM valid_sales
    GROUP BY customer_id
)
SELECT COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE orders >= 2) AS repeat_customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE orders >= 2) / COUNT(*), 1) AS repeat_customer_pct
FROM customer_orders;

-- Q15: How long does delivery take? (delivered orders with a valid delivery date)
SELECT ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
       ROUND(100.0 * AVG(CASE WHEN delivery_days <= 5 THEN 1 ELSE 0 END), 1) AS delivered_within_5_days_pct,
       COUNT(*) AS orders_measured
FROM orders
WHERE order_status = 'Delivered' AND delivery_days IS NOT NULL;

-- Q16: How much revenue comes from each payment method?
SELECT payment_method,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_total
FROM valid_sales
GROUP BY payment_method
ORDER BY revenue DESC;

-- Q17: How do the customer plan segments (Standard, Premium, Student, Business) compare?
SELECT c.customer_segment,
       COUNT(DISTINCT vs.customer_id) AS buying_customers,
       COUNT(DISTINCT vs.order_id) AS orders,
       ROUND(SUM(vs.revenue), 0) AS revenue,
       ROUND(SUM(vs.revenue) / COUNT(DISTINCT vs.order_id), 0) AS avg_order_value,
       ROUND(1.0 * COUNT(DISTINCT vs.order_id) / COUNT(DISTINCT vs.customer_id), 1) AS orders_per_customer
FROM valid_sales AS vs
JOIN customers AS c ON c.customer_id = vs.customer_id
GROUP BY c.customer_segment
ORDER BY revenue DESC;

-- Q18: Do bigger discounts bring more revenue? (revenue, units and margin by discount band)
SELECT CASE WHEN discount = 0 THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            WHEN discount <= 0.30 THEN '21-30%'
            ELSE 'Over 30%' END AS discount_band,
       COUNT(*) AS order_lines,
       SUM(quantity) AS units_sold,
       ROUND(SUM(discount_amount), 0) AS discount_given,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
GROUP BY 1
ORDER BY MIN(discount);

-- Q19: How many new customers sign up each month?
SELECT DATE_TRUNC('month', signup_date)::date AS signup_month,
       COUNT(*) AS new_customers
FROM customers
WHERE signup_date >= DATE '2025-01-01'
GROUP BY 1
ORDER BY 1;

-- Q20: How does every category and subcategory perform? (revenue, profit, units, average discount)
SELECT category, subcategory,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct,
       SUM(quantity) AS units_sold,
       ROUND(100.0 * SUM(discount_amount) / SUM(gross_sales), 1) AS avg_discount_pct
FROM valid_sales
GROUP BY category, subcategory
ORDER BY category, revenue DESC;
