# FreshCart Pipelines

An end-to-end data engineering assignment covering Git and CI, FreshCart ELT
on Snowflake, a tested Mage-style ML pipeline, and RabbitMQ topic routing.

## Repository layout

```text
freshcart-pipelines/
├── elt/                 # Snowflake SQL and executable notebook
├── iris_project/        # Mage-compatible Iris pipeline blocks
├── stream/              # RabbitMQ dispatcher and driver
├── tests/               # Local tests and pipeline checks
├── REPORT.md            # Submission report and run evidence checklist
└── .github/workflows/   # Python 3.12 CI
```

## Local checks

```powershell
python -m pip install -r requirements.txt
pytest -q
```

## External services

The ELT notebook requires a Snowflake connection. The stream scripts require a
RabbitMQ broker; set `RABBITMQ_URL` rather than committing a URL. For example:

```powershell
$env:RABBITMQ_URL = "amqp://guest:guest@localhost:5672/%2F"
python stream\dispatcher.py --count 10 --interval 0.1
python stream\driver.py --driver ravi --max-messages 10
```

The scripts are intentionally importable without a running broker, which keeps
the unit tests deterministic.

The optional Part D bonus bridge is in
`stream/bonus_bridge.py`. Start the dispatcher, set `RABBITMQ_URL`, and run:

```powershell
python stream\bonus_bridge.py --duration 60
```

The bridge writes a JSON Lines landing file. The bonus section in
`elt/freshcart_elt.ipynb` calls `load_file()`, reruns the Silver/Gold SQL, and
compares Gold totals after loading the same batch twice.

The local ML experiment table can be generated with:

```powershell
python -m iris_project.run_experiments
```

The Snowflake setup and sample load are in `elt/sql/01_setup.sql` and
`elt/sql/05_load_sample.sql`; run those before the cleaning, deduplication,
gold merge, and quality-check scripts.

The ML pipeline also writes `iris_confusion_matrix.csv` from the evaluation
branch alongside the metrics table.

