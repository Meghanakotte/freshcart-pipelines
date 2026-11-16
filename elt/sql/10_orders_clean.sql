MERGE INTO silver.orders_clean AS target
USING (
    SELECT
        order_id,
        customer_id,
        COALESCE(TRY_TO_DECIMAL(amount, 12, 2), 0) * IFF(UPPER(currency) = 'USD', 83.0, 1.0) AS amount_inr,
        TRY_TO_DATE(order_date) AS order_date,
        updated_at,
        source,
        SHA2(CONCAT_WS('|', order_id, customer_id, amount, currency, order_date, updated_at), 256) AS row_hash
    FROM bronze.orders_raw
    WHERE (amount IS NULL OR TRY_TO_DECIMAL(amount, 12, 2) IS NOT NULL)
      AND UPPER(currency) IN ('INR', 'USD')
      AND TRY_TO_DATE(order_date) IS NOT NULL
) AS source
ON target.row_hash = source.row_hash
WHEN NOT MATCHED THEN INSERT (
    order_id, customer_id, amount_inr, order_date, updated_at, source, row_hash
) VALUES (
    source.order_id, source.customer_id, source.amount_inr, source.order_date,
    source.updated_at, source.source, source.row_hash
);

MERGE INTO silver.orders_quarantine AS target
USING (
    SELECT
        order_id,
        customer_id,
        COALESCE(TRY_TO_DECIMAL(amount, 12, 2), 0) * IFF(UPPER(currency) = 'USD', 83.0, 1.0) AS amount_inr,
        TRY_TO_DATE(order_date) AS order_date,
        updated_at,
        source,
        SHA2(CONCAT_WS('|', order_id, customer_id, amount, currency, order_date, updated_at), 256) AS row_hash,
        ARRAY_CONSTRUCT_COMPACT(
            IFF(amount IS NOT NULL AND TRY_TO_DECIMAL(amount, 12, 2) IS NULL, 'invalid_amount', NULL),
            IFF(UPPER(currency) NOT IN ('INR', 'USD'), 'unsupported_currency', NULL),
            IFF(TRY_TO_DATE(order_date) IS NULL, 'invalid_order_date', NULL)
        ) AS reasons
    FROM bronze.orders_raw
    WHERE (amount IS NOT NULL AND TRY_TO_DECIMAL(amount, 12, 2) IS NULL)
       OR UPPER(currency) NOT IN ('INR', 'USD')
       OR TRY_TO_DATE(order_date) IS NULL
) AS source
ON target.row_hash = source.row_hash
WHEN NOT MATCHED THEN INSERT (
    order_id, customer_id, amount_inr, order_date, updated_at, source, row_hash, reasons
) VALUES (
    source.order_id, source.customer_id, source.amount_inr, source.order_date,
    source.updated_at, source.source, source.row_hash, source.reasons
);
