-- 01_data_quality.sql
-- Checks that the cleaned data loaded into PostgreSQL is consistent.
-- Run: psql -d ecommerce_analytics -f sql/01_data_quality.sql

-- Check 1: row counts of every table
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products',    COUNT(*) FROM products
UNION ALL SELECT 'orders',      COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews',     COUNT(*) FROM reviews;

-- Check 2: a summary of problems. Every issues_found value should be 0,
-- except the two "expected" rows, which are normal for this data.
SELECT 'Orders without any order line' AS check_name, COUNT(*) AS issues_found
FROM orders AS o
LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
WHERE oi.order_id IS NULL

UNION ALL
SELECT 'Customers without any order (expected: a few, their orders had invalid dates)', COUNT(*)
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL

UNION ALL
SELECT 'Delivery date before order date', COUNT(*)
FROM orders
WHERE delivery_date < order_date::date

UNION ALL
SELECT 'Customers who signed up after their first order', COUNT(*)
FROM customers AS c
JOIN (SELECT customer_id, MIN(order_date) AS first_order FROM orders GROUP BY customer_id) AS f
  ON f.customer_id = c.customer_id
WHERE c.signup_date > f.first_order::date

UNION ALL
SELECT 'Revenue formula wrong (qty x price x (1 - discount))', COUNT(*)
FROM order_items
WHERE ABS(revenue - quantity * unit_price * (1 - discount)) > 0.02

UNION ALL
SELECT 'Order revenue differs from sum of its lines', COUNT(*)
FROM orders AS o
JOIN (SELECT order_id, SUM(revenue) AS line_total FROM order_items GROUP BY order_id) AS t
  ON t.order_id = o.order_id
WHERE ABS(o.order_revenue - t.line_total) > 0.02

UNION ALL
SELECT 'Selling price below cost price (loss-making lines, expected: some)', COUNT(*)
FROM order_items
WHERE profit < 0

UNION ALL
SELECT 'Reviews on orders that were not delivered', COUNT(*)
FROM reviews AS r
JOIN orders AS o ON o.order_id = r.order_id
WHERE o.order_status <> 'Delivered';

-- Check 3: delivered orders that have no delivery date (kept in the data, left out of delivery statistics)
SELECT COUNT(*) AS delivered_without_delivery_date
FROM orders
WHERE order_status IN ('Delivered', 'Returned') AND delivery_date IS NULL;

-- Check 4: order status values and how common each one is
SELECT order_status,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders
FROM orders
GROUP BY order_status
ORDER BY orders DESC;

-- Check 5: date range covered by the orders
SELECT MIN(order_date)::date AS first_order, MAX(order_date)::date AS last_order,
       MAX(order_date)::date - MIN(order_date)::date AS days_covered
FROM orders;

-- Check 6: missing values in the columns that are allowed to be empty
SELECT COUNT(*) FILTER (WHERE email IS NULL) AS customers_without_email
FROM customers;

SELECT COUNT(*) FILTER (WHERE review_text IS NULL) AS reviews_without_text,
       COUNT(*) AS total_reviews
FROM reviews;
