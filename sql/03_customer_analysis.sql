-- 03_customer_analysis.sql
-- Customer behaviour. "Orders" here means valid sales (not Cancelled / Returned).

-- Q1: How many orders do customers place? (distribution, 15 means "15 or more")
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders
    FROM valid_sales
    GROUP BY customer_id
)
SELECT LEAST(orders, 15) AS orders_placed, COUNT(*) AS customers
FROM customer_orders
GROUP BY LEAST(orders, 15)
ORDER BY orders_placed;

-- Q2: Top 20 customers by lifetime revenue, with their rank
WITH customer_revenue AS (
    SELECT customer_id,
           COUNT(DISTINCT order_id) AS orders,
           SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY customer_id
)
SELECT RANK() OVER (ORDER BY cr.revenue DESC) AS revenue_rank,
       c.customer_id, c.customer_name, c.city, c.customer_segment,
       cr.orders,
       ROUND(cr.revenue, 0) AS lifetime_revenue
FROM customer_revenue AS cr
JOIN customers AS c ON c.customer_id = cr.customer_id
ORDER BY revenue_rank
LIMIT 20;

-- Q3: Split buyers into 10 equal groups (deciles) by revenue. How much do the top 10% bring?
WITH customer_revenue AS (
    SELECT customer_id, SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY customer_id
),
deciles AS (
    SELECT customer_id, revenue,
           NTILE(10) OVER (ORDER BY revenue DESC) AS decile   -- 1 = best customers
    FROM customer_revenue
)
SELECT decile,
       COUNT(*) AS customers,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_revenue
FROM deciles
GROUP BY decile
ORDER BY decile;

-- Q4: One-time, repeat and frequent buyers: how many customers and how much revenue?
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders, SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY customer_id
)
SELECT CASE WHEN orders = 1 THEN '1 order (one-time)'
            WHEN orders BETWEEN 2 AND 4 THEN '2-4 orders (repeat)'
            ELSE '5+ orders (frequent)' END AS buyer_type,
       COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_revenue
FROM customer_orders
GROUP BY 1
ORDER BY MIN(orders);

-- Q5: How many days pass between a customer's first and second order?
WITH numbered_orders AS (
    SELECT customer_id, order_date,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_number
    FROM orders
    WHERE order_status NOT IN ('Cancelled', 'Returned')
)
SELECT ROUND(AVG(second.order_date::date - first.order_date::date), 1) AS avg_days_to_second_order,
       COUNT(*) AS customers_with_second_order
FROM numbered_orders AS first
JOIN numbered_orders AS second
  ON second.customer_id = first.customer_id
 AND first.order_number = 1
 AND second.order_number = 2;

-- Q6: New vs returning customers: revenue by month
WITH first_order AS (
    SELECT customer_id, DATE_TRUNC('month', MIN(order_date))::date AS first_order_month
    FROM valid_sales
    GROUP BY customer_id
)
SELECT vs.order_month,
       ROUND(SUM(CASE WHEN vs.order_month = f.first_order_month THEN vs.revenue ELSE 0 END), 0) AS new_customer_revenue,
       ROUND(SUM(CASE WHEN vs.order_month > f.first_order_month THEN vs.revenue ELSE 0 END), 0) AS returning_customer_revenue
FROM valid_sales AS vs
JOIN first_order AS f ON f.customer_id = vs.customer_id
GROUP BY vs.order_month
ORDER BY vs.order_month;

-- Q7: At-risk customers: 2+ orders, but nothing in the last 120 days
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders, MAX(order_date) AS last_order
    FROM valid_sales
    GROUP BY customer_id
),
snapshot AS (
    SELECT DATE_TRUNC('day', MAX(order_date)) + INTERVAL '1 day' AS snapshot_date
    FROM valid_sales
)
SELECT COUNT(*) AS at_risk_customers
FROM customer_orders AS co
CROSS JOIN snapshot AS s
WHERE co.orders >= 2
  AND EXTRACT(DAY FROM (s.snapshot_date - co.last_order)) > 120;

-- Q8: Which states have the most high-spending customers (lifetime revenue above 50,000)?
WITH customer_revenue AS (
    SELECT customer_id, SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY customer_id
)
SELECT c.state,
       COUNT(*) AS customers_over_50k,
       ROUND(AVG(cr.revenue), 0) AS avg_lifetime_revenue
FROM customer_revenue AS cr
JOIN customers AS c ON c.customer_id = cr.customer_id
WHERE cr.revenue > 50000
GROUP BY c.state
ORDER BY customers_over_50k DESC
LIMIT 10;
