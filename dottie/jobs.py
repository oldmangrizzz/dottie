"""Durable job dispatch with idempotency and crash recovery.

A claimed job whose worker dies is requeued after its lease expires.
Workers must use idempotent external operations: the local queue alone
cannot guarantee exactly-once effects across external systems.
"""
import json
import sqlite3
import time
import uuid

class JobQueue:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.db.execute("PRAGMA busy_timeout=30000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, idempotency_key TEXT UNIQUE NOT NULL,
            agent TEXT NOT NULL, payload TEXT NOT NULL,
            state TEXT NOT NULL, lease_until REAL,
            result TEXT, error TEXT, attempts INTEGER NOT NULL DEFAULT 0,
            lease_token TEXT)""")

        columns = {row[1] for row in self.db.execute("PRAGMA table_info(jobs)")}
        if "lease_token" not in columns:
            self.db.execute("ALTER TABLE jobs ADD COLUMN lease_token TEXT")

    def submit(self, agent, payload, idempotency_key):
        if not agent or not idempotency_key:
            raise ValueError("agent and idempotency key required")
        self.db.execute("""INSERT OR IGNORE INTO jobs
            (id,idempotency_key,agent,payload,state) VALUES (?,?,?,?,?)""",
            (str(uuid.uuid4()), idempotency_key, agent, json.dumps(payload), "queued"))
        row = self.db.execute(
            "SELECT id FROM jobs WHERE idempotency_key=?", (idempotency_key,)).fetchone()
        return row[0]

    def claim(self, lease_seconds=60):
        if lease_seconds <= 0:
            raise ValueError("positive lease required")
        now = time.time()
        token = str(uuid.uuid4())
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("""SELECT id,agent,payload,attempts FROM jobs
                WHERE state='queued' OR (state='running' AND lease_until < ?)
                ORDER BY rowid LIMIT 1""", (now,)).fetchone()
            if row:
                self.db.execute("""UPDATE jobs SET state='running',
                    lease_until=?, lease_token=?, attempts=attempts+1 WHERE id=?""",
                    (now + lease_seconds, token, row[0]))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return ({"id":row[0], "agent":row[1], "payload":json.loads(row[2]),
                 "attempts":row[3]+1, "lease_token":token} if row else None)

    def finish(self, job_id, result, lease_token):
        cursor = self.db.execute("""UPDATE jobs SET state='completed',
            result=?, lease_until=NULL, lease_token=NULL
            WHERE id=? AND state='running' AND lease_token=? AND lease_until>=?""",
            (json.dumps(result), job_id, lease_token, time.time()))
        if cursor.rowcount != 1:
            raise PermissionError("job lease is not current")

    def fail(self, job_id, error, retry=False, lease_token=None):
        cursor = self.db.execute("""UPDATE jobs SET state=?, error=?,
            lease_until=NULL, lease_token=NULL WHERE id=? AND state='running'
            AND lease_token=? AND lease_until>=?""",
            ("queued" if retry else "failed", str(error), job_id, lease_token, time.time()))
        if cursor.rowcount != 1:
            raise PermissionError("job lease is not current")

    def status(self, job_id):
        row = self.db.execute("""SELECT state,attempts,result,error FROM jobs
            WHERE id=?""", (job_id,)).fetchone()
        return ({"state":row[0], "attempts":row[1],
                 "result":json.loads(row[2]) if row[2] is not None else None,
                 "error":row[3]} if row else None)

    def close(self):
        self.db.close()
