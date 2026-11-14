CREATE OR REPLACE PROCEDURE silver.quality_checks()
RETURNS TABLE ()
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
    );
END;
$$;
