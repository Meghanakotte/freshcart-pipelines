-- B4: Apply Arjun's Silver-to-Gold SCD Type 2 event.
-- The update closes the previous Silver record.
-- The MERGE inserts the new Gold record only once.

UPDATE dim.customers_scd2
SET effective_to = '2026-08-15'::DATE
WHERE customer_id = 'CUST-02'
  AND tier = 'Silver'
  AND effective_to IS NULL
  AND effective_from < '2026-08-15'::DATE;

MERGE INTO dim.customers_scd2 AS target
USING (
    SELECT
        'CUST-02' AS customer_id,
        'Arjun' AS customer_name,
        'arjun.k@yahoo.in' AS email,
        'Gold' AS tier,
        '2026-08-15'::DATE AS effective_from,
        NULL::DATE AS effective_to
) AS source
ON target.customer_id = source.customer_id
   AND target.effective_from = source.effective_from

WHEN NOT MATCHED THEN INSERT (
    customer_id,
    customer_name,
    email,
    tier,
    effective_from,
    effective_to
)
VALUES (
    source.customer_id,
    source.customer_name,
    source.email,
    source.tier,
    source.effective_from,
    source.effective_to
);
