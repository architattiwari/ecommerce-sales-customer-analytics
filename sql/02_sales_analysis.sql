-- 02_sales_analysis.sql
-- Sales trends and order patterns.
-- "Sales" means order lines from orders that are not Cancelled or Returned (view: valid_sales).

-- Q1: How does revenue change month to month? (LAG gives last month's value)
WITH monthly AS (
    SELECT order_month, SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY order_month
)
SELECT order_month,
       ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
             / LAG(revenue) OVER (ORDER BY order_month), 1) AS growth_vs_last_month_pct
FROM monthly
ORDER BY order_month;

-- Q2: What is the running (cumulative) revenue through the year?
WITH monthly AS (
    SELECT order_month, SUM(revenue) AS revenue
    FROM valid_sales
    GROUP BY order_month
)
SELECT order_month,
       ROUND(revenue, 0) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY order_month), 0) AS running_revenue
FROM monthly
ORDER BY order_month;

-- Q3: Revenue and profit by quarter
SELECT 'Q' || EXTRACT(QUARTER FROM order_date) AS quarter,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
GROUP BY EXTRACT(QUARTER FROM order_date)
ORDER BY 1;

-- Q4: Which days of the week are busiest? (ISODOW: 1 = Monday ... 7 = Sunday)
SELECT TO_CHAR(order_date, 'Dy') AS weekday,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0) AS revenue
FROM valid_sales
GROUP BY TO_CHAR(order_date, 'Dy'), EXTRACT(ISODOW FROM order_date)
ORDER BY EXTRACT(ISODOW FROM order_date);

-- Q5: How big is the festive period (Oct-Nov) compared with the rest of the year?
SELECT CASE WHEN EXTRACT(MONTH FROM order_date) IN (10, 11) THEN 'Festive (Oct-Nov)'
            ELSE 'Rest of year' END AS period,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 0) AS avg_order_value,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_year_revenue
FROM valid_sales
GROUP BY 1;

-- Q6: Which cities bring the most revenue?
SELECT shipping_city, shipping_state,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0) AS revenue
FROM valid_sales
GROUP BY shipping_city, shipping_state
ORDER BY revenue DESC
LIMIT 10;

-- Q7: Cancellation and return rates by payment method (uses ALL orders, not only sales)
SELECT payment_method,
       COUNT(*) AS orders,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END), 1) AS cancelled_pct,
       ROUND(100.0 * AVG(CASE WHEN order_status = 'Returned'  THEN 1 ELSE 0 END), 1) AS returned_pct
FROM orders
GROUP BY payment_method
ORDER BY cancelled_pct DESC;

-- Q8: How much revenue is lost to cancelled and returned orders?
SELECT o.order_status,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(oi.revenue), 0) AS order_value
FROM orders AS o
JOIN order_items AS oi ON oi.order_id = o.order_id
WHERE o.order_status IN ('Cancelled', 'Returned')
GROUP BY o.order_status;

-- Q9: Which states wait longest for delivery? (states with at least 500 delivered orders)
SELECT shipping_state,
       COUNT(*) AS delivered_orders,
       ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
       ROUND(100.0 * AVG(CASE WHEN delivery_days <= 5 THEN 1 ELSE 0 END), 1) AS delivered_within_5_days_pct
FROM orders
WHERE order_status = 'Delivered' AND delivery_days IS NOT NULL
GROUP BY shipping_state
HAVING COUNT(*) >= 500
ORDER BY avg_delivery_days DESC
LIMIT 10;

-- Q10: Is delivery slower in the festive months?
SELECT TO_CHAR(order_date, 'YYYY-MM') AS order_month,
       ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM orders
WHERE order_status = 'Delivered' AND delivery_days IS NOT NULL
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY order_month;
