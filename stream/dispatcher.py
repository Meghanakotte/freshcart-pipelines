"""Publish FreshCart-style orders to a RabbitMQ topic exchange."""

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

import pika

EXCHANGE = "rapido-dispatch"
CITIES = {"bangalore": ["koramangala", "indiranagar", "whitefield"], "chennai": ["tnagar", "whitefield"]}
ORDER_TYPES = ("ride", "food")


def make_order(order_id: str | None = None, bad: bool = False) -> dict:
    city = random.choice(tuple(CITIES))
    timestamp = datetime.now(timezone.utc)
    event_id = order_id or str(uuid4())
    order = {
        "id": event_id,
        "city": city,
        "zone": random.choice(CITIES[city]),
        "type": random.choice(ORDER_TYPES),
        "ts": timestamp.isoformat(),
        "order_id": event_id,
        "customer_id": "CUST-01",
        "amount": str(random.choice((250, 500, 750))),
        "currency": "INR",
        "order_date": timestamp.date().isoformat(),
        "updated_at": timestamp.isoformat(),
        "source": "rabbitmq",
    }
    if bad:
        order.pop("zone")
    return order


def publish(count: int, interval: float, url: str, bad_every: int = 10) -> None:
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    try:
        for index in range(1, count + 1):
            bad = index % bad_every == 0
            payload = make_order(bad=False)
            routing_key = ".".join(
                [payload["city"], payload["zone"], payload["type"]]
            )
            if bad:
                payload.pop("zone")
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(payload).encode(),
                properties=pika.BasicProperties(
                    content_type="application/json", delivery_mode=2
                ),
            )
            print(f"published {routing_key} {payload['id']}")
            time.sleep(interval)
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=0, help="0 means run forever")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--bad-every", type=int, default=10)
    parser.add_argument("--url", default=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"))
    args = parser.parse_args()
    publish(args.count or 2**31, args.interval, args.url, args.bad_every)
