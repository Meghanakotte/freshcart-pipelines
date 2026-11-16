CREATE SCHEMA IF NOT EXISTS dim;

CREATE TABLE IF NOT EXISTS dim.customers_scd2 (
    customer_id VARCHAR,
    customer_name VARCHAR,
    email VARCHAR,
    tier VARCHAR,
    effective_from DATE,
    effective_to DATE
);

UPDATE dim.customers_scd2 AS target
SET effective_to = source.effective_from
FROM (
    SELECT * FROM VALUES
        ('CUST-01', 'Asha', 'asha@example.com', 'Silver', '2025-01-01'::DATE, NULL::DATE),
        ('CUST-02', 'Arjun', 'arjun@example.com', 'Gold', '2026-02-01'::DATE, NULL::DATE),
        ('CUST-05', 'Priya', 'priya@example.com', 'Gold', '2025-01-01'::DATE, NULL::DATE)
) AS source(customer_id, customer_name, email, tier, effective_from, effective_to)
WHERE target.customer_id = source.customer_id
  AND target.effective_from < source.effective_from
  AND (target.effective_to IS NULL OR target.effective_to > source.effective_from);

MERGE INTO dim.customers_scd2 AS target
USING (
    SELECT * FROM VALUES
        ('CUST-01', 'Asha', 'asha@example.com', 'Silver', '2025-01-01'::DATE, NULL::DATE),
        ('CUST-02', 'Arjun', 'arjun@example.com', 'Gold', '2026-02-01'::DATE, NULL::DATE),
        ('CUST-05', 'Priya', 'priya@example.com', 'Gold', '2025-01-01'::DATE, NULL::DATE)
) AS source(customer_id, customer_name, email, tier, effective_from, effective_to)
ON target.customer_id = source.customer_id
   AND target.effective_from = source.effective_from
WHEN NOT MATCHED THEN INSERT VALUES (
    source.customer_id, source.customer_name, source.email, source.tier,
    source.effective_from, source.effective_to
);

MERGE INTO bronze.orders_raw AS target
USING (
    SELECT * FROM VALUES
    ('ORD-1001', 'CUST-01', '1001', 'INR', '2026-01-05', '2026-01-05 10:00:00'::TIMESTAMP_NTZ, 'website'),
    ('ORD-1002', 'CUST-02', '1500', 'INR', '2026-01-06', '2026-01-06 10:00:00'::TIMESTAMP_NTZ, 'website'),
    ('ORD-1003', 'CUST-01', NULL, 'INR', '2026-01-07', '2026-01-07 10:00:00'::TIMESTAMP_NTZ, 'website'),
    ('ORD-1003', 'CUST-01', '2100', 'INR', '2026-01-07', '2026-01-08 10:00:00'::TIMESTAMP_NTZ, 'mobile'),
    ('ORD-1005', 'CUST-05', '3184', 'INR', '2026-01-09', '2026-01-09 11:00:00'::TIMESTAMP_NTZ, 'mobile'),
    ('ORD-1005', 'CUST-05', '3184', 'INR', '2026-01-09', '2026-01-09 10:00:00'::TIMESTAMP_NTZ, 'website'),
    ('ORD-1004', 'CUST-01', 'bad', 'INR', '2026-01-10', '2026-01-10 10:00:00'::TIMESTAMP_NTZ, 'website'),
    ('ORD-1006', 'CUST-02', '100', 'EUR', '2026-01-11', '2026-01-11 10:00:00'::TIMESTAMP_NTZ, 'mobile')
) AS source(order_id, customer_id, amount, currency, order_date, updated_at, source)
ON target.order_id = source.order_id
   AND target.updated_at = source.updated_at
   AND target.source = source.source
WHEN NOT MATCHED THEN INSERT
    (order_id, customer_id, amount, currency, order_date, updated_at, source)
VALUES (
    source.order_id, source.customer_id, source.amount, source.currency,
    source.order_date, source.updated_at, source.source
);
