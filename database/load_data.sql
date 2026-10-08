-- Loads the cleaned CSV files into PostgreSQL.
-- Run from the PROJECT ROOT so the relative paths below work:
--   psql -d ecommerce_analytics -f database/load_data.sql
-- (\copy reads the files on your own machine, so no server file permissions are needed.)

TRUNCATE reviews, order_items, orders, products, customers;

\copy customers   FROM 'data/processed/customers.csv'   WITH (FORMAT csv, HEADER true)
\copy products    FROM 'data/processed/products.csv'    WITH (FORMAT csv, HEADER true)
\copy orders      FROM 'data/processed/orders.csv'      WITH (FORMAT csv, HEADER true)
\copy order_items FROM 'data/processed/order_items.csv' WITH (FORMAT csv, HEADER true)
\copy reviews     FROM 'data/processed/reviews.csv'     WITH (FORMAT csv, HEADER true)

-- Quick check: row counts should match the CSV files
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products',    COUNT(*) FROM products
UNION ALL SELECT 'orders',      COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews',     COUNT(*) FROM reviews;
