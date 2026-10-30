"""In-memory policy demonstration only, NOT OpenViking storage.

Per-actor private memory must not be silently shared. Retrieved mission context
is not autobiographical memory. All durable memory promotion is intentionally
unimplemented/denied at this research stage.
"""
from collections import defaultdict


class MemoryDomains:
    def __init__(self):
        self._private = defaultdict(list)
        self._context = defaultdict(list)

    def add_private(self, owner, value):
        # Test fixture API. Production writes require GrizOS authority and receipts.
        self._private[owner].append(value)

    def read_private(self, requester, owner):
        if requester != owner:
            raise PermissionError("Cross-intelligence autobiographical access denied")
        return list(self._private[owner])

    def provide_context(self, requester, value):
        self._context[requester].append(value)

    def read_context(self, requester):
        return list(self._context[requester])

    def promote_private(self, owner, value, permission_token=None):
        raise PermissionError("Autobiographical memory promotion disabled in prototype")
