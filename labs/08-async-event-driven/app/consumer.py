"""Payment consumer with an optional inbox (dedup) table.

IDEMPOTENT=1: record payment_id and apply the balance change in ONE local SQLite
transaction; a duplicate delivery hits the primary key and is acknowledged without effect.
IDEMPOTENT=0: apply the balance change blindly (at-least-once delivery => double effects).

Error handling:
  * unparseable body  -> basic_reject(requeue=False)  -> dead-lettered at once (non-retryable)
  * processing error  -> basic_reject(requeue=True)   -> retried; after x-delivery-limit -> DLQ
    (RabbitMQ 4.3+ counts basic.reject, not basic.nack, towards the delivery limit.)
  * CRASH_ONCE_ON=<id> -> process exits after the DB commit but before the ack, once.
  * RETRY_VERB=nack     -> use basic_nack(requeue=True) for retries instead (experiment 4).
"""
import json
import os
import sqlite3
import time

from common import QUEUE, connect, declare_topology

IDEMPOTENT = os.environ.get("IDEMPOTENT", "1") == "1"
CRASH_ONCE_ON = os.environ.get("CRASH_ONCE_ON", "")
PREFETCH = int(os.environ.get("PREFETCH", "10"))
WORK_MS = int(os.environ.get("WORK_MS", "0"))
RETRY_VERB = os.environ.get("RETRY_VERB", "reject")
DB_PATH = "/data/ledger.db"


def open_db() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH, isolation_level=None)  # explicit BEGIN/COMMIT below
    db.execute("CREATE TABLE IF NOT EXISTS inbox (message_id TEXT PRIMARY KEY, seen_at REAL)")
    db.execute("CREATE TABLE IF NOT EXISTS accounts (account TEXT PRIMARY KEY, balance INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS effects (n INTEGER)")  # count of applied effects
    return db


def apply_payment(db: sqlite3.Connection, msg_id: str, account: str, amount: int) -> bool:
    """Return True if the effect was applied, False if it was a duplicate."""
    db.execute("BEGIN IMMEDIATE")
    try:
        if IDEMPOTENT:
            try:
                db.execute("INSERT INTO inbox VALUES (?, ?)", (msg_id, time.time()))
            except sqlite3.IntegrityError:
                db.execute("ROLLBACK")
                return False
        db.execute(
            "INSERT INTO accounts VALUES (?, ?) "
            "ON CONFLICT(account) DO UPDATE SET balance = balance + excluded.balance",
            (account, amount),
        )
        db.execute("INSERT INTO effects VALUES (1)")
        db.execute("COMMIT")
        return True
    except Exception:
        db.execute("ROLLBACK")
        raise


def main() -> None:
    db = open_db()
    conn = connect()
    ch = conn.channel()
    declare_topology(ch)
    ch.basic_qos(prefetch_count=PREFETCH)  # backpressure: at most PREFETCH unacked messages
    print(f"consumer up: idempotent={IDEMPOTENT} prefetch={PREFETCH} retry={RETRY_VERB} crash_once_on={CRASH_ONCE_ON or '-'}", flush=True)

    def on_message(ch, method, props, body):
        headers = props.headers or {}
        dc = headers.get("x-delivery-count", 0)
        msg_id = props.message_id or "?"
        if WORK_MS:
            time.sleep(WORK_MS / 1000)
        try:
            evt = json.loads(body)
        except ValueError:
            print(f"POISON {msg_id}: unparseable body -> reject(requeue=False) -> DLQ", flush=True)
            ch.basic_reject(method.delivery_tag, requeue=False)
            return
        try:
            if evt.get("simulate") == "always_fail":
                raise RuntimeError("downstream rejected the payment")
            applied = apply_payment(db, msg_id, evt["account"], int(evt["amount"]))
        except Exception as exc:  # retryable failure
            print(f"FAIL {msg_id} (x-delivery-count={dc}): {exc} -> {RETRY_VERB}(requeue=True)", flush=True)
            if RETRY_VERB == "nack":
                time.sleep(0.2)  # slow the loop down: nack-requeue does not count towards the limit on 4.3+
                ch.basic_nack(method.delivery_tag, requeue=True)
            else:
                ch.basic_reject(method.delivery_tag, requeue=True)
            return
        marker = f"/data/crashed-{msg_id}"
        if applied and msg_id == CRASH_ONCE_ON and not os.path.exists(marker):
            open(marker, "w").close()
            print(f"CRASH after committing {msg_id}, before ack (redelivered={method.redelivered})", flush=True)
            os._exit(1)
        state = "applied" if applied else "DUPLICATE skipped"
        print(f"OK {msg_id} {state} (redelivered={method.redelivered}, x-delivery-count={dc})", flush=True)
        ch.basic_ack(method.delivery_tag)

    ch.basic_consume(QUEUE, on_message, auto_ack=False)
    ch.start_consuming()


if __name__ == "__main__":
    main()
