"""Scoped, expiring delegation controlled by the person receiving assistance."""
import json
import sqlite3
import time
import uuid

class Delegations:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS delegations (
            id TEXT PRIMARY KEY, principal TEXT NOT NULL, delegate TEXT NOT NULL,
            agent TEXT NOT NULL, permissions TEXT NOT NULL,
            expires_at REAL NOT NULL, revoked_at REAL)""")
        self.db.commit()

    def grant(self, principal, delegate, agent, permissions, authorized_by, ttl_seconds):
        if authorized_by != principal:
            raise PermissionError("principal authorization required")
        if principal == delegate or ttl_seconds <= 0:
            raise ValueError("invalid delegation")
        if not permissions or not all(isinstance(p, str) and p.strip() for p in permissions):
            raise ValueError("permissions required")
        if not set(permissions).issubset(DELEGATABLE_PERMISSIONS):
            raise ValueError("unsupported delegated permission")
        for user_id in (principal, delegate):
            if not self.db.execute("SELECT 1 FROM users WHERE id=? AND active=1", (user_id,)).fetchone():
                raise LookupError("unknown active user")
        if not self.db.execute("SELECT 1 FROM aegis_agents WHERE id=? AND enabled=1", (agent,)).fetchone():
            raise LookupError("unknown enabled agent")
        key = str(uuid.uuid4())
        with self.db:
            self.db.execute("INSERT INTO delegations VALUES (?,?,?,?,?,?,NULL)",
                (key, principal, delegate, agent,
                 json.dumps(sorted(set(permissions))), time.time() + ttl_seconds))
        return key

    def allowed(self, principal, delegate, agent, permission):
        for user_id in (principal, delegate):
            if not self.db.execute("SELECT 1 FROM users WHERE id=? AND active=1", (user_id,)).fetchone():
                return False
        rows = self.db.execute("""SELECT permissions FROM delegations
            WHERE principal=? AND delegate=? AND agent=? AND revoked_at IS NULL
            AND expires_at>?""", (principal, delegate, agent, time.time()))
        return any(permission in json.loads(row[0]) for row in rows)

    def revoke(self, delegation_id, authorized_by):
        row = self.db.execute("SELECT principal FROM delegations WHERE id=?", (delegation_id,)).fetchone()
        if row is None:
            raise LookupError("delegation not found")
        if row[0] != authorized_by:
            raise PermissionError("principal authorization required")
        with self.db:
            self.db.execute("UPDATE delegations SET revoked_at=? WHERE id=?",
                            (time.time(), delegation_id))

    def close(self):
        self.db.close()
