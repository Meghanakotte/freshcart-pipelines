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

