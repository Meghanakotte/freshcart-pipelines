"""Consume one driver's topic binding with explicit ACK/NACK behavior."""

import argparse
import json
import os

import pika

try:
    from stream.dispatcher import EXCHANGE
    from stream.routing import DRIVER_PATTERNS
except ModuleNotFoundError:
    from dispatcher import EXCHANGE
    from routing import DRIVER_PATTERNS


def consume(driver: str, url: str, max_messages: int = 0) -> None:
    if driver not in DRIVER_PATTERNS:
        raise ValueError(f"unknown driver: {driver}")
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    queue = channel.queue_declare(queue=f"driver.{driver}", exclusive=False, durable=False).method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=DRIVER_PATTERNS[driver])
    seen = 0

    def handle(ch, method, properties, body):
        nonlocal seen
        message = json.loads(body)
        if not message.get("zone"):
            print(f"NACK {message.get('id', '<unknown>')}: missing zone")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            print(f"ACK {driver} {method.routing_key}: {message['id']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        seen += 1
        if max_messages and seen >= max_messages:
            ch.stop_consuming()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=handle, auto_ack=False)
    try:
        channel.start_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--driver", choices=sorted(DRIVER_PATTERNS), required=True)
    parser.add_argument("--max-messages", type=int, default=0)
    parser.add_argument("--url", default=os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F"))
    args = parser.parse_args()
    consume(args.driver, args.url, args.max_messages)
