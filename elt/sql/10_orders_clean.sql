INSERT INTO silver.orders_clean
SELECT
    order_id,
    customer_id,
    TRY_TO_DECIMAL(amount, 12, 2) * IFF(UPPER(currency) = 'USD', 83.0, 1.0),
    TRY_TO_DATE(order_date),
    updated_at,
    source,
    SHA2(CONCAT_WS('|', order_id, customer_id, amount, currency, order_date), 256)
FROM bronze.orders_raw
WHERE TRY_TO_DECIMAL(amount, 12, 2) IS NOT NULL
  AND UPPER(currency) IN ('INR', 'USD')
  AND TRY_TO_DATE(order_date) IS NOT NULL;

INSERT INTO silver.orders_quarantine (order_id, customer_id, amount_inr, order_date, updated_at, source, row_hash)
SELECT order_id, customer_id, TRY_TO_DECIMAL(amount, 12, 2), TRY_TO_DATE(order_date),
       updated_at, source, SHA2(CONCAT_WS('|', order_id, customer_id, amount, currency, order_date), 256)
FROM bronze.orders_raw
WHERE TRY_TO_DECIMAL(amount, 12, 2) IS NULL
   OR UPPER(currency) NOT IN ('INR', 'USD')
   OR TRY_TO_DATE(order_date) IS NULL;
