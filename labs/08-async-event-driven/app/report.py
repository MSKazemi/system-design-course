"""Print ledger state and queue depths."""
import os
import sqlite3

from common import DLQ, QUEUE, connect

if os.path.exists("/data/ledger.db"):
    db = sqlite3.connect("/data/ledger.db")
    for acct, bal in db.execute("SELECT account, balance FROM accounts ORDER BY account"):
        print(f"balance[{acct}] = {bal}")
    print("effects applied =", db.execute("SELECT COUNT(*) FROM effects").fetchone()[0])
    print("inbox rows      =", db.execute("SELECT COUNT(*) FROM inbox").fetchone()[0])
else:
    print("no ledger yet")

conn = connect()
ch = conn.channel()
for q in (QUEUE, DLQ):
    r = ch.queue_declare(q, passive=True)
    print(f"queue {q}: ready={r.method.message_count} consumers={r.method.consumer_count}")
conn.close()
