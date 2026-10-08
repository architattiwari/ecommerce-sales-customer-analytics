-- 04_product_analysis.sql
-- Product, category and discount analysis. "Sales" = valid_sales view (no Cancelled / Returned orders).

-- Q1: Top 3 products inside each category by revenue (ROW_NUMBER restarts for every category)
WITH product_revenue AS (
    SELECT category, product_name, SUM(revenue) AS revenue, SUM(quantity) AS units
    FROM valid_sales
    GROUP BY category, product_name
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category
    FROM product_revenue
)
SELECT category, rank_in_category, product_name, ROUND(revenue, 0) AS revenue, units
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- Q2: Share of each subcategory inside its category (window function with PARTITION BY)
SELECT category, subcategory,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (PARTITION BY category), 1) AS pct_of_category,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
GROUP BY category, subcategory
ORDER BY category, revenue DESC;

-- Q3: Products that never sold (LEFT JOIN keeps products with no matching sales)
SELECT p.category, COUNT(*) AS products_with_no_sales
FROM products AS p
LEFT JOIN valid_sales AS vs ON vs.product_id = p.product_id
WHERE vs.product_id IS NULL
GROUP BY p.category
ORDER BY products_with_no_sales DESC;

-- Q4: Loss-making products (total profit below zero)
SELECT product_id, product_name, category,
       SUM(quantity) AS units,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(SUM(profit), 0) AS profit
FROM valid_sales
GROUP BY product_id, product_name, category
HAVING SUM(profit) < 0
ORDER BY profit
LIMIT 15;

-- Q5: Profit margin tiers: how much revenue sits in thin-margin products?
WITH product_margin AS (
    SELECT product_id, SUM(revenue) AS revenue, 100.0 * SUM(profit) / SUM(revenue) AS margin_pct
    FROM valid_sales
    GROUP BY product_id
)
SELECT CASE WHEN margin_pct < 10 THEN '1. Under 10%'
            WHEN margin_pct < 25 THEN '2. 10% to 25%'
            WHEN margin_pct < 40 THEN '3. 25% to 40%'
            ELSE '4. Over 40%' END AS margin_tier,
       COUNT(*) AS products,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_revenue
FROM product_margin
GROUP BY 1
ORDER BY 1;

-- Q6: How does the discount level change quantity and margin?
SELECT CASE WHEN discount = 0 THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            WHEN discount <= 0.30 THEN '21-30%'
            ELSE 'Over 30%' END AS discount_band,
       COUNT(*) AS order_lines,
       ROUND(AVG(quantity), 2) AS avg_quantity_per_line,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
GROUP BY 1
ORDER BY MIN(discount);

-- Q7: Same question for Electronics only. Do discounts still make money there?
SELECT CASE WHEN discount = 0 THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            ELSE 'Over 20%' END AS discount_band,
       COUNT(*) AS order_lines,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
WHERE category = 'Electronics'
GROUP BY 1
ORDER BY MIN(discount);

-- Q8: Which price range sells best?
SELECT CASE WHEN unit_price < 500 THEN '1. Under 500'
            WHEN unit_price < 2000 THEN '2. 500 - 1,999'
            WHEN unit_price < 10000 THEN '3. 2,000 - 9,999'
            ELSE '4. 10,000 and above' END AS price_range,
       COUNT(DISTINCT product_id) AS products,
       SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 1) AS margin_pct
FROM valid_sales
GROUP BY 1
ORDER BY 1;

-- Q9: Average rating and return rate by category
WITH ratings AS (
    SELECT p.category, AVG(r.rating) AS avg_rating, COUNT(*) AS reviews
    FROM reviews AS r
    JOIN products AS p ON p.product_id = r.product_id
    GROUP BY p.category
),
returns AS (
    SELECT p.category,
           100.0 * AVG(CASE WHEN o.order_status = 'Returned' THEN 1 ELSE 0 END) AS return_rate_pct
    FROM order_items AS oi
    JOIN orders   AS o ON o.order_id   = oi.order_id
    JOIN products AS p ON p.product_id = oi.product_id
    WHERE o.order_status IN ('Delivered', 'Returned')
    GROUP BY p.category
)
SELECT ra.category, ROUND(ra.avg_rating, 2) AS avg_rating, ra.reviews, ROUND(re.return_rate_pct, 1) AS return_rate_pct
FROM ratings AS ra
JOIN returns AS re ON re.category = ra.category
ORDER BY avg_rating;

-- Q10: Lowest-rated subcategories (only those with at least 200 reviews)
SELECT p.category, p.subcategory,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(*) AS reviews
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
GROUP BY p.category, p.subcategory
HAVING COUNT(*) >= 200
ORDER BY avg_rating
LIMIT 5;
