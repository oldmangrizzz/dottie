"""Integrated local runtime for Dottie and independent agent handlers."""
from .identity import IdentityStore
from .jobs import JobQueue
from .evidence import EvidenceLedger
from .memory import ScopedMemory
from .aegis import AgentRegistry
from .memberships import AgentMemberships
from .delegation import Delegations

class DottieRuntime:
    def __init__(self, database_path):
        self.identity = IdentityStore(database_path)
        self.jobs = JobQueue(database_path)
        self.evidence = EvidenceLedger(database_path)
        self.memory = ScopedMemory(database_path)
        self.agents = AgentRegistry(database_path)
        self.memberships = AgentMemberships(database_path)
        self.delegations = Delegations(database_path)
        self.handlers = {}

    def register_agent(self, agent_id, handler):
        if not isinstance(agent_id, str) or not agent_id.strip() or not callable(handler):
            raise ValueError("agent identity and callable handler required")
        if agent_id in self.handlers:
            raise ValueError("agent already registered")
        self.handlers[agent_id] = handler

    def submit(self, user_id, agent_id, payload, idempotency_key):
        if not self.identity.allowed(user_id, "agents:dispatch"):
            raise PermissionError("dispatch permission denied")
        if agent_id not in self.handlers:
            raise LookupError("agent is not registered")
        if not self.memberships.allowed(agent_id, user_id, "dispatch"):
            raise PermissionError("agent membership dispatch denied")
        return self.jobs.submit(agent_id, {"submitted_by": user_id, "input": payload}, idempotency_key)

    def submit_delegated(self, principal_id, delegate_id, agent_id, payload, idempotency_key):
        if not self.identity.allowed(delegate_id, 'agents:dispatch'):
            raise PermissionError('delegate dispatch permission denied')
        if agent_id not in self.handlers:
            raise LookupError('agent is not registered')
        if not self.memberships.allowed(agent_id, delegate_id, 'dispatch'):
            raise PermissionError('delegate agent membership denied')
        if not self.delegations.allowed(principal_id, delegate_id, agent_id, 'agents:dispatch'):
            raise PermissionError('principal delegation denied')
        return self.jobs.submit(agent_id, {
            'submitted_by': delegate_id, 'on_behalf_of': principal_id,
            'input': payload}, idempotency_key)

    def run_next(self):
        job = self.jobs.claim()
        if job is None:
            return None
        try:
            handler = self.handlers.get(job["agent"])
            if handler is None:
                raise LookupError("agent handler unavailable")
            result = handler(job["payload"]["input"])
            self.jobs.finish(job["id"], result)
            return {"id": job["id"], "state": "completed", "result": result}
        except Exception as exc:
            self.jobs.fail(job["id"], str(exc))
            return {"id": job["id"], "state": "failed", "error": str(exc)}

    def close(self):
        self.delegations.close()
        self.memberships.close()
        self.agents.close()
        self.memory.close()
        self.evidence.close()
        self.jobs.close()
        self.identity.close()
