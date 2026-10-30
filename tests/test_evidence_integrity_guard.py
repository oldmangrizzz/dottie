import os
import tempfile
import unittest
from dottie.evidence import EvidenceLedger

class EvidenceIntegrityGuardTests(unittest.TestCase):
    def test_append_refuses_corrupt_existing_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, "state.db"))
            record = ledger.append("claim", "source", "content", "verified", {"v": 1})
            ledger.db.execute("UPDATE evidence SET value_json=? WHERE id=?", ('{"v":99}', record))
            ledger.db.commit()
            with self.assertRaises(ValueError):
                ledger.append("other", "source", "content", "verified", {"v": 2})
            ledger.close()

    def test_migration_does_not_hide_corrupt_sealed_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, "state.db"))
            record = ledger.append("claim", "source", "content", "verified", {"v": 1})
            ledger.db.execute("UPDATE evidence SET value_json=? WHERE id=?", ('{"v":99}', record))
            ledger.db.commit()
            with self.assertRaises(ValueError):
                ledger.migrate_legacy_seals(allow_unverified_baseline=True)
            ledger.close()
