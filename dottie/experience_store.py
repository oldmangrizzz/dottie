"""Scoped experience storage with explicit, receipt-backed consolidation.

A receipt string is an audit reference, not proof of a human approval.
Callers must validate review receipts against an independent authority before
using this research implementation for consequential autobiographical writes.
"""
import sqlite3
import uuid
from pathlib import Path


class ExperienceStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS experience (
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, mission TEXT NOT NULL,
            kind TEXT NOT NULL, content TEXT NOT NULL, source_ref TEXT NOT NULL,
            review_receipt TEXT, promoted INTEGER NOT NULL DEFAULT 0
        )""")
        self.db.commit()

    def record(self, owner, mission, kind, content, source_ref):
        if kind not in ("direct", "retrieved", "inferred", "reported"):
            raise ValueError("Invalid experience provenance")
        if any(not isinstance(value, str) or not value.strip()
               for value in (owner, mission, content, source_ref)):
            raise ValueError("All experience fields must be nonempty")
        event_id = str(uuid.uuid4())
        with self.db:
            self.db.execute(
                "INSERT INTO experience(id,owner,mission,kind,content,source_ref) VALUES(?,?,?,?,?,?)",
                (event_id, owner, mission, kind, content, source_ref),
            )
        return event_id

    def promote(self, owner, event_id, review_receipt):
        if not isinstance(review_receipt, str) or not review_receipt.strip():
            raise PermissionError("Review receipt required")
        with self.db:
            row = self.db.execute(
                "SELECT owner,kind,promoted FROM experience WHERE id=?", (event_id,)
            ).fetchone()
            if row is None or row[0] != owner:
                raise PermissionError("Cross-identity promotion denied")
            if row[1] != "direct":
                raise PermissionError("Only directly experienced events can enter autobiography")
            if row[2]:
                raise ValueError("Experience already promoted")
            self.db.execute(
                "UPDATE experience SET promoted=1,review_receipt=? WHERE id=?",
                (review_receipt, event_id),
            )

    def autobiography(self, owner):
        rows = self.db.execute(
            """SELECT id,mission,kind,content,source_ref,review_receipt
               FROM experience WHERE owner=? AND promoted=1 ORDER BY rowid""",
            (owner,),
        ).fetchall()
        return [dict(zip(("id","mission","kind","content","source_ref","review_receipt"), row))
                for row in rows]

    def close(self):
        self.db.close()
