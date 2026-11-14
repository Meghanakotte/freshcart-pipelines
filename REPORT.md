# Assignment report: From Git to Gold

This report is the submission-ready narrative. Replace the marked evidence
items with screenshots from the actual GitHub Actions, Snowflake, Mage, and
RabbitMQ runs before exporting to the required PDF filename.

## Part A - Git and CI/CD

The repository follows `working folder -> local Git -> remote Git -> CI/CD`.
`git add` changes the staging area, `git commit` records the staged snapshot in
the local repository, `git push` sends commits to the remote, and `git pull`
downloads and integrates remote commits. A commit alone is not visible to a
teammate until it has been pushed. The CI workflow checks out the commit,
installs Python 3.12 dependencies, and runs pytest on every push and pull
request.

## Part B - FreshCart ELT

The pipeline extracts API-shaped records into `bronze.orders_raw`, loads and
normalizes them into `silver.orders_clean`, sends invalid records to
`silver.orders_quarantine`, deduplicates with `ROW_NUMBER()` into
`silver.orders_dedup`, and merges current records into `gold.orders`.
`ORD-1003` demonstrates schema normalization and latest-record wins:
the mobile record has the later `updated_at`, so its amount survives the
deduplication. Loyalty points are `amount_inr * tier multiplier`; the current
SCD2 customer row supplies the tier. `ORD-1005` earns Gold points only when
the effective customer dimension row says Gold, while its earlier Silver
version is retained for history.

The currency rule accepts only INR and USD. Unsupported currencies are added to
the quarantine reason array as `unsupported_currency` and cannot affect gold
totals. Silver and quarantine use a content hash as their merge key, while the
deduplication table is rebuilt from the current clean set, so a rerun does not
add duplicate rows.

**B4 prediction before execution:** one current SCD2 row for CUST-02, Gold for
ORD-1002, and two Gold rows updated only when the source hash changes. The
`MERGE` is safe to rerun because it matches on `order_id` and updates only when
`row_hash` differs.

**B5 quality check:** the sixth check is `quarantine_has_reason`, which checks
that every quarantined row has at least one reason. ELT is a
better fit here because Snowflake can load raw data first and apply auditable
SQL transformations and quarantine rules close to the data. ETL would still
win when a source cannot legally or practically land raw data, or when
transformation must happen before storage.

## Part C - Mage ML pipeline

The block graph is `load_iris -> prepare_data -> train_model`, with parallel
downstream blocks `save_results`, `evaluate_model`, and `export_metrics`.
`train_model` has an `@test`-equivalent gate requiring at least 0.80 test
accuracy. Therefore a failed test stops `save_results`; saving first and
checking later would leave an invalid artifact behind. Run with:

```text
python -m iris_project.run_pipeline --max-depth 3
```

The evaluation branch writes `iris_metrics.csv`, and the custom exporter
provides a separately tested metrics artifact. The five-run experiment table
is generated with `python -m iris_project.run_experiments`.

The local gate experiment produced the following results:

| max_depth | Test accuracy | Test passed? | Predictions created? |
|---:|---:|---|---|
| 1 | failed gate | No | No |
| 2 | 0.9333 | Yes | Yes |
| 3 | 0.9667 | Yes | Yes |
| 4 | 0.9333 | Yes | Yes |
| 5 | 0.9333 | Yes | Yes |

## Part D - RabbitMQ stream

RabbitMQ topic matching uses `*` for exactly one word and `#` for zero or more
words. Thus `bangalore.koramangala.food` reaches Ravi and Control; the
two-word `bangalore.koramangala` reaches only Control; and
`chennai.whitefield.ride` is dropped by the listed bindings. Drivers ACK
valid messages and NACK invalid messages with `requeue=False`, so a missing
zone is discarded instead of retrying forever. With `requeue=True`, a
permanently invalid message would be redelivered repeatedly and block useful
work.

The routing answers are:

| Routing key | Receiving queues |
|---|---|
| `bangalore.koramangala.food` | Ravi, Meena, Control |
| `bangalore.indiranagar.ride` | Priya, Arjun, Control |
| `bangalore.whitefield.ride` | Arjun, Control |
| `chennai.tnagar.food` | Karthik |
| `chennai.whitefield.ride` | Dropped |
| `bangalore.koramangala` | Control only |

## Part E - Reflection and evidence

The most failure-prone integration point was keeping topic routing and
validation consistent between publisher and consumers. I isolated matching in
`stream/routing.py`, added deterministic tests, and made the consumer's ACK/NACK
decision explicit. Attach the required green/red CI screenshots, Snowflake
query outputs, Mage graph/output, RabbitMQ console output, and the final
`git log --oneline` in an appendix.
