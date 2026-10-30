"""Dottie-owned durable identity baseline independent of LLM provider.

SQLite local persistence. This is not a GrizOS integration or consciousness
implementation. No identity migration without explicit separate governance.
"""
import sqlite3
from pathlib import Path


class IdentityStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path)
        self._db.execute("PRAGMA busy_timeout=5000")
        self._db.execute("""CREATE TABLE IF NOT EXISTS identities (
            identity_id TEXT PRIMARY KEY NOT NULL,
            baseline_ref TEXT NOT NULL,
            active_model TEXT NOT NULL DEFAULT 'unbound'
        )""")
        self._db.commit()

    def establish(self, identity_id, baseline_ref):
        if not isinstance(identity_id, str) or not identity_id.strip():
            raise ValueError("Identity ID required")
        if not isinstance(baseline_ref, str) or not baseline_ref.strip():
            raise ValueError("Baseline reference required")
        existing = self._db.execute(
            "SELECT baseline_ref FROM identities WHERE identity_id=?", (identity_id,)
        ).fetchone()
        if existing:
            if existing[0] != baseline_ref:
                raise ValueError("Identity baseline change requires explicit migration")
            return
        with self._db:
            self._db.execute(
                "INSERT INTO identities(identity_id,baseline_ref) VALUES(?,?)",
                (identity_id, baseline_ref),
            )

    def read(self, identity_id):
        row = self._db.execute(
            "SELECT identity_id,baseline_ref,active_model FROM identities WHERE identity_id=?",
            (identity_id,),
        ).fetchone()
        if row is None:
            raise KeyError("Unknown identity")
        return dict(zip(("identity_id", "baseline_ref", "active_model"), row))

    def record_model(self, identity_id, model):
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Model name required")
        with self._db:
            result = self._db.execute(
                "UPDATE identities SET active_model=? WHERE identity_id=?",
                (model, identity_id),
            )
            if result.rowcount != 1:
                raise KeyError("Unknown identity")

    def close(self):
        self._db.close()
