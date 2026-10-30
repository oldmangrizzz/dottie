import os
import tempfile
import unittest
from dottie.runtime import DottieRuntime

class DelegationPermissionScopeTests(unittest.TestCase):
    def test_unrecognized_permission_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "correct horse battery staple", "owner")
            principal = runtime.identity.create_user("principal", "correct horse battery staple", "viewer", owner)
            helper = runtime.identity.create_user("helper", "correct horse battery staple", "researcher", owner)
            with self.assertRaises(ValueError):
                runtime.delegations.grant(principal, helper, "dugan",
                                          ["users:manage"], principal, 3600)
            with self.assertRaises(ValueError):
                runtime.delegations.grant(principal, helper, "dugan",
                                          ["agents:dispatch", "evidence:write"], principal, 3600)
            runtime.close()

    def test_dispatch_permission_is_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = DottieRuntime(os.path.join(folder, "state.db"))
            owner = runtime.identity.create_user("owner", "correct horse battery staple", "owner")
            principal = runtime.identity.create_user("principal", "correct horse battery staple", "viewer", owner)
            helper = runtime.identity.create_user("helper", "correct horse battery staple", "researcher", owner)
            grant = runtime.delegations.grant(principal, helper, "dugan",
                                              ["agents:dispatch"], principal, 3600)
            self.assertTrue(runtime.delegations.allowed(principal, helper, "dugan", "agents:dispatch"))
            runtime.delegations.revoke(grant, principal)
            runtime.close()
