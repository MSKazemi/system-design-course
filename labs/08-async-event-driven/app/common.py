"""Shared topology for lab L08 (SYSDESIGN-08).

Topology:
  exchange  payments        (direct)  --routing key "payment"-->  queue payments.q (quorum)
  exchange  payments.dlx    (fanout)  ------------------------->  queue payments.dlq (quorum)

payments.q dead-letters to payments.dlx when a message is rejected without requeue,
or when its delivery count exceeds x-delivery-limit.
"""
import os
import time

import pika

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@localhost:10856/%2F")
EXCHANGE = "payments"
DLX = "payments.dlx"
QUEUE = "payments.q"
DLQ = "payments.dlq"
ROUTING_KEY = "payment"
DELIVERY_LIMIT = int(os.environ.get("DELIVERY_LIMIT", "3"))


def connect(retries: int = 30) -> pika.BlockingConnection:
    params = pika.URLParameters(AMQP_URL)
    for attempt in range(1, retries + 1):
        try:
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError:
            print(f"broker not reachable yet (attempt {attempt}/{retries})", flush=True)
            time.sleep(2)
    raise SystemExit("could not connect to RabbitMQ")


def declare_topology(ch) -> None:
    ch.exchange_declare(EXCHANGE, exchange_type="direct", durable=True)
    ch.exchange_declare(DLX, exchange_type="fanout", durable=True)
    ch.queue_declare(DLQ, durable=True, arguments={"x-queue-type": "quorum"})
    ch.queue_bind(DLQ, DLX)
    ch.queue_declare(
        QUEUE,
        durable=True,
        arguments={
            "x-queue-type": "quorum",
            "x-dead-letter-exchange": DLX,
            "x-delivery-limit": DELIVERY_LIMIT,
        },
    )
    ch.queue_bind(QUEUE, EXCHANGE, routing_key=ROUTING_KEY)
