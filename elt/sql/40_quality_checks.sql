CREATE OR REPLACE PROCEDURE silver.quality_checks()
RETURNS TABLE (check_name VARCHAR, failures NUMBER)
LANGUAGE SQL
AS
$$
BEGIN
    RETURN TABLE (
        SELECT 'gold_order_id_not_null' AS check_name, COUNT_IF(order_id IS NULL) AS failures FROM gold.orders
        UNION ALL
        SELECT 'gold_loyalty_non_negative', COUNT_IF(loyalty_points < 0) FROM gold.orders
        UNION ALL
        SELECT 'dedup_order_date_not_future', COUNT_IF(order_date > CURRENT_DATE()) FROM silver.orders_dedup
        UNION ALL
        SELECT
            'gold_amount_present',
            COUNT_IF(
                g.amount_inr IS NULL
                OR b.order_id IS NULL
                OR g.amount_inr <> (
                    COALESCE(TRY_TO_DECIMAL(b.amount, 12, 2), 0)
                    * IFF(UPPER(b.currency) = 'USD', 83.0, 1.0)
                )
            )
        FROM gold.orders g
        LEFT JOIN (
            SELECT order_id, amount, currency
            FROM bronze.orders_raw
            WHERE (amount IS NULL OR TRY_TO_DECIMAL(amount, 12, 2) IS NOT NULL)
              AND UPPER(currency) IN ('INR', 'USD')
              AND TRY_TO_DATE(order_date) IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY order_id ORDER BY updated_at DESC NULLS LAST
            ) = 1
        ) b ON b.order_id = g.order_id
        UNION ALL
        SELECT 'gold_tier_present', COUNT_IF(tier IS NULL) FROM gold.orders
        UNION ALL
        SELECT 'quarantine_has_reason', COUNT_IF(ARRAY_SIZE(reasons) = 0) FROM silver.orders_quarantine
    );
END;
$$;
