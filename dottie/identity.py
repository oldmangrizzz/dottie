"""Multi-user identity and role grants for Dottie.

Password authentication uses scrypt and constant-time comparison.
This module is a local identity backend, not an Apple Sign-In integration.
"""
import hashlib
import hmac
import os
import sqlite3
import uuid

ROLES = frozenset({"owner", "administrator", "researcher", "reviewer", "viewer"})
ROLE_PERMISSIONS = {
    "owner": frozenset({"users:manage", "agents:dispatch", "evidence:write", "evidence:read", "memory:read", "memory:write"}),
    "administrator": frozenset({"users:manage", "agents:dispatch", "evidence:write", "evidence:read", "memory:read", "memory:write"}),
    "researcher": frozenset({"agents:dispatch", "evidence:write", "evidence:read", "memory:read", "memory:write"}),
    "reviewer": frozenset({"evidence:read", "memory:read"}),
    "viewer": frozenset({"evidence:read"}),
}

class IdentityStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE,
            password_hash BLOB NOT NULL, salt BLOB NOT NULL,
            role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1)""")
        self.db.commit()

    def create_user(self, username, password, role, actor_id=None):
        if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or len(password) < 12:
            raise ValueError("username and password of at least 12 characters required")
        if role not in ROLES:
            raise ValueError("unsupported role")
        count = self.db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count:
            if not actor_id or not self.allowed(actor_id, "users:manage"):
                raise PermissionError("user management authorization required")
        elif role != "owner":
            raise PermissionError("first user must be owner")
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        user_id = str(uuid.uuid4())
        with self.db:
            self.db.execute("INSERT INTO users VALUES (?,?,?,?,?,1)",
                            (user_id, username.strip(), digest, salt, role))
        return user_id

    def authenticate(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            return None
        row = self.db.execute("""SELECT id,password_hash,salt FROM users
            WHERE username=? AND active=1""", (username,)).fetchone()
        if row is None:
            return None
        candidate = hashlib.scrypt(password.encode(), salt=row[2], n=2**14, r=8, p=1)
        return row[0] if hmac.compare_digest(candidate, row[1]) else None

    def allowed(self, user_id, permission):
        row = self.db.execute("SELECT role FROM users WHERE id=? AND active=1",
                              (user_id,)).fetchone()
        return bool(row and permission in ROLE_PERMISSIONS[row[0]])

    def close(self):
        self.db.close()
