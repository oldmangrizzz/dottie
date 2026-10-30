"""Persistent, scoped memory for Dottie and independent AEGIS agents.

SQLite is used for durable local storage. Retrieval is always scoped by
both namespace and owner; there is deliberately no unscoped search method.
"""
import json
import sqlite3
from datetime import datetime, timezone

SCOPES = frozenset({
    "dottie-private", "gmri-institutional", "aegis-shared",
    "agent-private", "mission", "evidence", "gev-world"
})
OWNER_SCOPES = frozenset({"dottie-private", "agent-private", "mission"})

class ScopedMemory:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS memory (
            scope TEXT NOT NULL, owner TEXT NOT NULL, key TEXT NOT NULL,
            value TEXT NOT NULL, updated_at TEXT NOT NULL,
            PRIMARY KEY (scope, owner, key))""")
        self.db.commit()

    @staticmethod
    def _validate(scope: str, owner: str, key: str):
        if scope not in SCOPES:
            raise ValueError("unknown memory scope")
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("owner required")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key required")
        if scope == "dottie-private" and owner != "dottie":
            raise PermissionError("Dottie private memory requires Dottie owner")
        if scope in OWNER_SCOPES and owner == "*":
            raise PermissionError("wildcard owner forbidden")

    def put(self, scope: str, owner: str, key: str, value):
        self._validate(scope, owner, key)
        timestamp = datetime.now(timezone.utc).isoformat()
        with self.db:
            self.db.execute("""INSERT INTO memory VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(scope, owner, key) DO UPDATE SET
                value=excluded.value, updated_at=excluded.updated_at""",
                (scope, owner, key, json.dumps(value), timestamp))

    def get(self, scope: str, owner: str, key: str):
        self._validate(scope, owner, key)
        row = self.db.execute(
            "SELECT value FROM memory WHERE scope=? AND owner=? AND key=?",
            (scope, owner, key)).fetchone()
        return json.loads(row[0]) if row else None

    def close(self):
        self.db.close()
