TRUNCATE TABLE silver.orders_dedup;

INSERT INTO silver.orders_dedup
SELECT order_id, customer_id, amount_inr, order_date, updated_at, source, row_hash, cleaned_at
FROM silver.orders_clean
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id ORDER BY updated_at DESC NULLS LAST, cleaned_at DESC
) = 1;
