"""Append-only evidence ledger with source digests and conflict preservation."""
import hashlib
import json
import sqlite3
import time
import uuid

STATUSES = frozenset({"verified", "calculated", "user-reported", "disputed"})

class EvidenceLedger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY, claim_id TEXT NOT NULL, source_id TEXT NOT NULL,
            digest TEXT NOT NULL, status TEXT NOT NULL, value_json TEXT NOT NULL,
            recorded_at REAL NOT NULL)""")
        self.db.execute("CREATE INDEX IF NOT EXISTS evidence_claim_idx ON evidence(claim_id)")
        self.db.execute("""CREATE TABLE IF NOT EXISTS evidence_integrity (
            evidence_id TEXT PRIMARY KEY, record_hash TEXT NOT NULL)""")
        self.db.commit()

    @staticmethod
    def _record_hash(fields):
        return hashlib.sha256(json.dumps(fields, separators=(",", ":"),
                                         ensure_ascii=False).encode("utf-8")).hexdigest()

    def verify_integrity(self):
        rows = self.db.execute("""SELECT id,claim_id,source_id,digest,status,
            value_json,recorded_at FROM evidence""").fetchall()
        seals = dict(self.db.execute(
            "SELECT evidence_id,record_hash FROM evidence_integrity"))
        if len(rows) != len(seals):
            return False
        return all(seals.get(row[0]) == self._record_hash(row) for row in rows)

    def migrate_legacy_seals(self, allow_unverified_baseline=False):
        """Explicitly baseline existing records, not attest to their historical truth.

        Use only after external review of legacy data. A baseline cannot prove
        the rows were not altered before the migration.
        """
        if not allow_unverified_baseline:
            raise PermissionError("explicit acceptance of an unverified baseline required")
        rows = self.db.execute("""SELECT id,claim_id,source_id,digest,status,
            value_json,recorded_at FROM evidence""").fetchall()
        existing = set(row[0] for row in self.db.execute(
            "SELECT evidence_id FROM evidence_integrity"))
        missing = [row for row in rows if row[0] not in existing]
        with self.db:
            self.db.executemany(
                "INSERT INTO evidence_integrity VALUES (?,?)",
                [(row[0], self._record_hash(row)) for row in missing])
        return len(missing)

    def append(self, claim_id, source_id, source_content, status, value):
        if not claim_id or not source_id or not isinstance(source_content, (str, bytes)):
            raise ValueError("claim, source and source content required")
        if status not in STATUSES:
            raise ValueError("unsupported evidence status")
        raw = source_content.encode("utf-8") if isinstance(source_content, str) else source_content
        record_id = str(uuid.uuid4())
        row = (record_id, claim_id, source_id, hashlib.sha256(raw).hexdigest(),
               status, json.dumps(value), time.time())
        with self.db:
            self.db.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?)", row)
            self.db.execute("INSERT INTO evidence_integrity VALUES (?,?)",
                            (record_id, self._record_hash(row)))
        return record_id

    def history(self, claim_id):
        if not claim_id:
            raise ValueError("claim required")
        rows = self.db.execute("""SELECT id,source_id,digest,status,value_json,recorded_at
            FROM evidence WHERE claim_id=? ORDER BY recorded_at,id""", (claim_id,)).fetchall()
        return [{"id":r[0], "source_id":r[1], "digest":r[2], "status":r[3],
                 "value":json.loads(r[4]), "recorded_at":r[5]} for r in rows]

    def reconcile(self, claim_id):
        records = self.history(claim_id)
        if not records:
            return {"state": "missing", "records": []}
        distinct = {json.dumps(r["value"], sort_keys=True) for r in records}
        return {"state": "unresolved" if len(distinct) > 1 else "consistent",
                "records": records}

    @staticmethod
    def verify_source(record, content):
        raw = content.encode("utf-8") if isinstance(content, str) else content
        return hashlib.sha256(raw).hexdigest() == record["digest"]

    def close(self):
        self.db.close()
