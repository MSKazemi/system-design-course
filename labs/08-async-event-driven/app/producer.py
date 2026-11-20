"""Publish payment events with an idempotency key (AMQP message_id = payment_id).

Examples:
  python producer.py --payments 10                 # 10 payments of 10 to account A
  python producer.py --payments 10 --duplicate     # also re-send pay-0003 (simulated producer retry)
  python producer.py --poison --always-fail        # one unparseable body, one message that always fails
"""
import argparse
import json

import pika

from common import EXCHANGE, ROUTING_KEY, connect, declare_topology


def publish(ch, payment_id: str, body: bytes) -> None:
    ch.basic_publish(
        EXCHANGE,
        ROUTING_KEY,
        body,
        properties=pika.BasicProperties(
            message_id=payment_id,
            delivery_mode=pika.DeliveryMode.Persistent,
            content_type="application/json",
        ),
        mandatory=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payments", type=int, default=0)
    ap.add_argument("--start", type=int, default=1, help="first payment number")
    ap.add_argument("--amount", type=int, default=10)
    ap.add_argument("--account", default="A")
    ap.add_argument("--duplicate", action="store_true", help="re-publish payment #3 (same key)")
    ap.add_argument("--poison", action="store_true", help="publish one unparseable message")
    ap.add_argument("--always-fail", action="store_true", help="publish one message that always throws")
    args = ap.parse_args()

    conn = connect()
    ch = conn.channel()
    declare_topology(ch)
    ch.confirm_delivery()  # publisher confirms: basic_publish raises if the broker nacks

    sent = 0
    for i in range(args.start, args.start + args.payments):
        pid = f"pay-{i:04d}"
        body = json.dumps({"payment_id": pid, "account": args.account, "amount": args.amount}).encode()
        publish(ch, pid, body)
        sent += 1
    if args.duplicate:
        pid = f"pay-{args.start + 2:04d}"
        body = json.dumps({"payment_id": pid, "account": args.account, "amount": args.amount}).encode()
        publish(ch, pid, body)
        sent += 1
        print(f"re-published {pid} (simulated producer retry after a lost confirm)")
    if args.poison:
        publish(ch, "poison-0001", b"{not json")
        sent += 1
    if args.always_fail:
        body = json.dumps({"payment_id": "fail-0001", "account": "X", "amount": 1, "simulate": "always_fail"}).encode()
        publish(ch, "fail-0001", body)
        sent += 1
    print(f"published {sent} message(s), all confirmed by the broker")
    conn.close()


if __name__ == "__main__":
    main()
