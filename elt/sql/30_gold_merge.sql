MERGE INTO gold.orders AS target
USING (
    SELECT d.order_id, d.customer_id, d.amount_inr, d.updated_at, d.row_hash,
           c.tier,
           CEIL(d.amount_inr / 100) * CASE c.tier WHEN 'Gold' THEN 2 WHEN 'Silver' THEN 1 ELSE 1 END AS loyalty_points
    FROM silver.orders_dedup d
    LEFT JOIN dim.customers_scd2 c
      ON c.customer_id = d.customer_id
     AND d.order_date >= c.effective_from
     AND (c.effective_to IS NULL OR d.order_date < c.effective_to)
) AS source
ON target.order_id = source.order_id
WHEN MATCHED AND (
    target.row_hash <> source.row_hash
    OR COALESCE(target.tier, '') <> COALESCE(source.tier, '')
) THEN UPDATE SET
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
