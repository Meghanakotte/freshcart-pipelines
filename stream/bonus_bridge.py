"""Collect RabbitMQ order events and load them into the FreshCart Bronze table."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pika

try:
    from stream.dispatcher import EXCHANGE
except ModuleNotFoundError:
    from dispatcher import EXCHANGE


def write_landing(
    records: list[dict], run_id: str, landing_dir: str = "freshcart_landing"
) -> Path:
    """Write raw RabbitMQ records as JSON Lines and return the file path."""
    directory = Path(landing_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"rabbitmq__{run_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")
    return path


def consume_for_minute(
    url: str, duration_seconds: int = 60, queue_name: str | None = None
) -> list[dict]:
    """Consume matching events for a bounded period and acknowledge each event."""
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    queue = channel.queue_declare(
        queue=queue_name or f"bonus.{uuid4()}",
        exclusive=True,
        auto_delete=True,
    ).method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue, routing_key="#")

    records: list[dict] = []
    deadline = time.monotonic() + duration_seconds
    try:
        for method, _properties, body in channel.consume(
            queue, inactivity_timeout=1, auto_ack=False
        ):
            if time.monotonic() >= deadline:
                break
            if method is None:
                continue
            message = json.loads(body)
            records.append(message)
            channel.basic_ack(delivery_tag=method.delivery_tag)
    finally:
        channel.cancel()
        connection.close()
    return records


def load_file(connection, path: Path) -> int:
    """PUT a JSON Lines landing file into Bronze and return copied-row count."""
    file_format = "bronze.bonus_json"
    stage = "bronze.bonus_stage"
    staged_name = path.name
    file_uri = path.resolve().as_uri()
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE FILE FORMAT IF NOT EXISTS {file_format} TYPE = JSON"
        )
        cursor.execute(
            f"CREATE STAGE IF NOT EXISTS {stage} FILE_FORMAT = {file_format}"
        )
        cursor.execute(
            f"PUT '{file_uri}' @{stage} AUTO_COMPRESS = FALSE OVERWRITE = TRUE"
        )
        cursor.execute(
            f"""
            COPY INTO bronze.orders_raw
                (order_id, customer_id, amount, currency, order_date, updated_at, source)
            FROM (
                SELECT
                    $1:order_id::VARCHAR,
                    $1:customer_id::VARCHAR,
                    $1:amount::VARCHAR,
                    $1:currency::VARCHAR,
                    $1:order_date::VARCHAR,
                    $1:updated_at::TIMESTAMP_NTZ,
                    $1:source::VARCHAR
                FROM @{stage}
            )
            FILES = ('{staged_name}')
            FILE_FORMAT = (FORMAT_NAME = {file_format})
            ON_ERROR = 'ABORT_STATEMENT'
            """
        )
        result = cursor.fetchall()
    return int(result[0][3]) if result else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--landing-dir", default="freshcart_landing")
    parser.add_argument("--url", default=os.getenv("RABBITMQ_URL"))
    args = parser.parse_args()
    if not args.url:
        raise SystemExit("Set RABBITMQ_URL before running the bonus bridge")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    records = consume_for_minute(args.url, args.duration)
    path = write_landing(records, run_id, args.landing_dir)
    print(f"received={len(records)} landing_file={path}")


if __name__ == "__main__":
    main()
