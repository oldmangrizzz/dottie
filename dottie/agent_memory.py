"""Authenticated access boundary for agent-specific memory.

Agent identity is bound to the accessor at construction; callers cannot
supply a different owner to retrieve another agent's private memories.
Shared mission records remain distinct from private autobiographical data.
"""
from .memory import ScopedMemory

class AgentMemory:
    def __init__(self, store: ScopedMemory, agent_id: str):
        if not isinstance(agent_id, str) or not agent_id.strip() or agent_id == "*":
            raise ValueError("valid agent identity required")
        self._store = store
        self.agent_id = agent_id

    def remember(self, key, value):
        self._store.put("agent-private", self.agent_id, key, value)

    def recall(self, key):
        return self._store.get("agent-private", self.agent_id, key)

    def write_shared(self, key, value):
        self._store.put("aegis-shared", "aegis", key, value)

    def read_shared(self, key):
        return self._store.get("aegis-shared", "aegis", key)
