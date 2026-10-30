import unittest
from dottie.authority import authorize

class AuthorityTests(unittest.TestCase):
    def test_explicit_grant(self):
        self.assertTrue(authorize('read:evidence', {'read:evidence'}))

    def test_missing_grant(self):
        self.assertFalse(authorize('write:evidence', {'read:evidence'}))

    def test_empty_grants(self):
        self.assertFalse(authorize('read:evidence', set()))

    def test_wildcard_not_implicit(self):
        self.assertFalse(authorize('delete:all', {'*'}))
