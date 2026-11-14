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
        SELECT 'gold_amount_present', COUNT_IF(amount_inr IS NULL) FROM gold.orders
        UNION ALL
        SELECT 'gold_tier_present', COUNT_IF(tier IS NULL) FROM gold.orders
        UNION ALL
        SELECT 'quarantine_has_reason', COUNT_IF(ARRAY_SIZE(reasons) = 0) FROM silver.orders_quarantine
    );
END;
$$;
