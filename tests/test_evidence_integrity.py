import os
import tempfile
import unittest
from dottie.evidence import EvidenceLedger

class EvidenceIntegrityTests(unittest.TestCase):
    def test_integrity_detects_row_modification(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, "evidence.db"))
            entry = ledger.append("claim-1", "source-1", "original", "verified", {"amount": 5})
            self.assertTrue(ledger.verify_integrity())
            ledger.db.execute("UPDATE evidence SET value_json=? WHERE id=?",
                              ('{"amount":999}', entry))
            ledger.db.commit()
            self.assertFalse(ledger.verify_integrity())
            ledger.close()

    def test_integrity_detects_row_deletion(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, "evidence.db"))
            entry = ledger.append("claim-1", "source-1", "original", "verified", {"amount": 5})
            ledger.db.execute("DELETE FROM evidence WHERE id=?", (entry,))
            ledger.db.commit()
            self.assertFalse(ledger.verify_integrity())
            ledger.close()
