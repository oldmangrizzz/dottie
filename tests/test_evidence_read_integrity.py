"""Never expose compromised evidence as verified history."""
import os
import tempfile
import unittest
from dottie.evidence import EvidenceLedger

class EvidenceReadIntegrityTests(unittest.TestCase):
    def test_modified_record_blocks_history_and_reconcile(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, 'evidence.db'))
            record = ledger.append('claim', 'source', 'original', 'verified', {'v': 1})
            ledger.db.execute('UPDATE evidence SET value_json=? WHERE id=?', ('{"v":99}', record))
            ledger.db.commit()
            with self.assertRaises(ValueError):
                ledger.history('claim')
            with self.assertRaises(ValueError):
                ledger.reconcile('claim')
            ledger.close()

    def test_deleted_record_blocks_history_and_reconcile(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = EvidenceLedger(os.path.join(folder, 'evidence.db'))
            record = ledger.append('claim', 'source', 'original', 'verified', {'v': 1})
            ledger.db.execute('DELETE FROM evidence WHERE id=?', (record,))
            ledger.db.commit()
            with self.assertRaises(ValueError):
                ledger.history('claim')
            with self.assertRaises(ValueError):
                ledger.reconcile('claim')
            ledger.close()

if __name__ == '__main__':
    unittest.main()
