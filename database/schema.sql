-- PostgreSQL schema for the E-Commerce Sales & Customer Analytics project.
-- Column order matches the CSV files in data/processed/ exactly.
-- Run: psql -d ecommerce_analytics -f database/schema.sql

DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    customer_id       VARCHAR(10)  PRIMARY KEY,
    customer_name     VARCHAR(100) NOT NULL,
    email             VARCHAR(150),
    city              VARCHAR(60)  NOT NULL,
    state             VARCHAR(60)  NOT NULL,
    signup_date       DATE         NOT NULL,
    customer_segment  VARCHAR(20)  NOT NULL
);

CREATE TABLE products (
    product_id    VARCHAR(10)   PRIMARY KEY,
    product_name  VARCHAR(150)  NOT NULL,
    category      VARCHAR(50)   NOT NULL,
    subcategory   VARCHAR(60)   NOT NULL,
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    cost_price    NUMERIC(10,2) NOT NULL CHECK (cost_price > 0)
);

CREATE TABLE orders (
    order_id         VARCHAR(10)   PRIMARY KEY,
    customer_id      VARCHAR(10)   NOT NULL REFERENCES customers (customer_id),
    order_date       TIMESTAMP     NOT NULL,
    order_status     VARCHAR(20)   NOT NULL,
    payment_method   VARCHAR(30)   NOT NULL,
    shipping_city    VARCHAR(60)   NOT NULL,
    shipping_state   VARCHAR(60)   NOT NULL,
    delivery_date    DATE,                       -- empty for cancelled / not yet delivered orders
    delivery_days    INTEGER,                    -- delivery_date minus order date
    order_revenue    NUMERIC(12,2) NOT NULL      -- sum of revenue of the order lines
);

CREATE TABLE order_items (
    order_id         VARCHAR(10)   NOT NULL REFERENCES orders (order_id),
    product_id       VARCHAR(10)   NOT NULL REFERENCES products (product_id),
    quantity         INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price       NUMERIC(10,2) NOT NULL,
    discount         NUMERIC(4,2)  NOT NULL CHECK (discount BETWEEN 0 AND 1),
    gross_sales      NUMERIC(12,2) NOT NULL,     -- quantity x unit_price
    discount_amount  NUMERIC(12,2) NOT NULL,     -- gross_sales x discount
    revenue          NUMERIC(12,2) NOT NULL,     -- gross_sales - discount_amount
    cost             NUMERIC(12,2) NOT NULL,     -- quantity x product cost_price
    profit           NUMERIC(12,2) NOT NULL,     -- revenue - cost
    profit_margin    NUMERIC(8,4)  NOT NULL,     -- profit / revenue
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE reviews (
    review_id    VARCHAR(10)  PRIMARY KEY,
    order_id     VARCHAR(10)  NOT NULL,
    customer_id  VARCHAR(10)  NOT NULL REFERENCES customers (customer_id),
    product_id   VARCHAR(10)  NOT NULL,
    rating       SMALLINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_date  DATE         NOT NULL,
    review_text  TEXT,
    FOREIGN KEY (order_id, product_id) REFERENCES order_items (order_id, product_id)
);

-- One row per SOLD order line: Cancelled and Returned orders are left out.
-- Most analysis queries start from this view so the join and the filter are written only once.
CREATE VIEW valid_sales AS
SELECT
    oi.order_id,
    o.customer_id,
    o.order_date,
    DATE_TRUNC('month', o.order_date)::date AS order_month,
    o.order_status,
    o.payment_method,
    o.shipping_city,
    o.shipping_state,
    o.delivery_days,
    oi.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.gross_sales,
    oi.discount_amount,
    oi.revenue,
    oi.cost,
    oi.profit
FROM order_items AS oi
JOIN orders      AS o ON o.order_id   = oi.order_id
JOIN products    AS p ON p.product_id = oi.product_id
WHERE o.order_status NOT IN ('Cancelled', 'Returned');

-- Indexes for the joins and filters used in the analysis queries
CREATE INDEX idx_customers_state       ON customers (state);
CREATE INDEX idx_products_category     ON products (category);
CREATE INDEX idx_orders_customer       ON orders (customer_id);
CREATE INDEX idx_orders_order_date     ON orders (order_date);
CREATE INDEX idx_orders_status         ON orders (order_status);
CREATE INDEX idx_order_items_product   ON order_items (product_id);
CREATE INDEX idx_reviews_product       ON reviews (product_id);
