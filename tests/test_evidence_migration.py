import os
import sqlite3
import tempfile
import unittest
from dottie.evidence import EvidenceLedger

class EvidenceMigrationTests(unittest.TestCase):
    def test_legacy_rows_require_explicit_seal_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "state.db")
            ledger = EvidenceLedger(path)
            entry = ledger.append("claim", "source", "text", "verified", {"value": 1})
            ledger.db.execute("DELETE FROM evidence_integrity WHERE evidence_id=?", (entry,))
            ledger.db.commit()
            self.assertFalse(ledger.verify_integrity())
            with self.assertRaises(PermissionError):
                ledger.migrate_legacy_seals()
            self.assertEqual(ledger.migrate_legacy_seals(allow_unverified_baseline=True), 1)
            self.assertTrue(ledger.verify_integrity())
            ledger.close()

    def test_missing_seal_on_new_record_cannot_be_silently_repaired(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, "state.db"))
            entry = ledger.append("claim", "source", "text", "verified", {"value": 1})
            ledger.db.execute("DELETE FROM evidence_integrity WHERE evidence_id=?", (entry,))
            ledger.db.commit()
            self.assertFalse(ledger.verify_integrity())
            ledger.close()
