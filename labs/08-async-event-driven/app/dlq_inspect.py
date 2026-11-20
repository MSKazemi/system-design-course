"""Peek at dead-lettered messages (get + requeue, so nothing is lost)."""
from common import DLQ, connect

conn = connect()
ch = conn.channel()
seen = []
while True:
    method, props, body = ch.basic_get(DLQ, auto_ack=False)
    if method is None:
        break
    deaths = (props.headers or {}).get("x-death", [])
    reason = deaths[0].get("reason") if deaths else "?"
    count = deaths[0].get("count") if deaths else "?"
    print(f"DLQ message_id={props.message_id} reason={reason} x-death.count={count} body={body[:40]!r}")
    seen.append(method.delivery_tag)
for tag in seen:
    ch.basic_nack(tag, requeue=True)
print(f"{len(seen)} message(s) in {DLQ}")
conn.close()
