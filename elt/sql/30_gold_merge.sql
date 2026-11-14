MERGE INTO gold.orders AS target
USING (
    SELECT d.order_id, d.customer_id, d.amount_inr, d.updated_at, d.row_hash,
           c.tier,
           d.amount_inr * CASE c.tier WHEN 'Gold' THEN 2 WHEN 'Silver' THEN 1.5 ELSE 1 END AS loyalty_points
    FROM silver.orders_dedup d
    LEFT JOIN (
        SELECT customer_id, tier
        FROM dim.customers_scd2
        WHERE effective_from <= CURRENT_DATE()
          AND (effective_to IS NULL OR effective_to > CURRENT_DATE())
        QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY effective_from DESC) = 1
    ) c USING (customer_id)
) AS source
ON target.order_id = source.order_id
WHEN MATCHED AND target.row_hash <> source.row_hash THEN UPDATE SET
    customer_id = source.customer_id,
    amount_inr = source.amount_inr,
    loyalty_points = source.loyalty_points,
    tier = source.tier,
    published_at = CURRENT_TIMESTAMP(),
    row_hash = source.row_hash
WHEN NOT MATCHED THEN INSERT (
    order_id, customer_id, amount_inr, loyalty_points, tier, published_at, row_hash
) VALUES (
    source.order_id, source.customer_id, source.amount_inr, source.loyalty_points,
    source.tier, CURRENT_TIMESTAMP(), source.row_hash
);
