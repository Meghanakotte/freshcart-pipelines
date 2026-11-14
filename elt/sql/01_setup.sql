CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS bronze.orders_raw (
    order_id VARCHAR,
    customer_id VARCHAR,
    amount VARCHAR,
    currency VARCHAR,
    order_date VARCHAR,
    updated_at TIMESTAMP_NTZ,
    source VARCHAR,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS silver.orders_clean (
    order_id VARCHAR,
    customer_id VARCHAR,
    amount_inr NUMBER(12, 2),
    order_date DATE,
    updated_at TIMESTAMP_NTZ,
    source VARCHAR,
    row_hash VARCHAR,
    cleaned_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS silver.orders_dedup LIKE silver.orders_clean;
CREATE TABLE IF NOT EXISTS silver.orders_quarantine (
    order_id VARCHAR,
    customer_id VARCHAR,
    amount_inr NUMBER(12, 2),
    order_date DATE,
    updated_at TIMESTAMP_NTZ,
    source VARCHAR,
    row_hash VARCHAR,
    reasons ARRAY,
    quarantined_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
CREATE TABLE IF NOT EXISTS gold.orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    amount_inr NUMBER(12, 2),
    loyalty_points NUMBER(12, 2),
    tier VARCHAR,
    published_at TIMESTAMP_NTZ,
    row_hash VARCHAR
);
