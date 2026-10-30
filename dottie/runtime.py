"""Integrated local runtime for Dottie and independent agent handlers."""
from .identity import IdentityStore
from .jobs import JobQueue
from .evidence import EvidenceLedger
from .memory import ScopedMemory
from .aegis import AgentRegistry
from .memberships import AgentMemberships
from .delegation import Delegations
from .relationships import AgentRelationships
from .collaboration import CollaborationJournal
from .messaging import AgentMessages
from .agent_memory import AgentMemory

class DottieRuntime:
    def __init__(self, database_path):
        self.identity = IdentityStore(database_path)
        self.jobs = JobQueue(database_path)
        self.evidence = EvidenceLedger(database_path)
        self.memory = ScopedMemory(database_path)
        self.agents = AgentRegistry(database_path)
        self.memberships = AgentMemberships(database_path)
        self.delegations = Delegations(database_path)
        self.relationships = AgentRelationships(database_path)
        self.collaboration = CollaborationJournal(database_path)
        self.messages = AgentMessages(database_path)
        self.handlers = {}

    def agent_memory(self, agent_id):
        agent = self.agents.get(agent_id)
        if not agent or not agent['enabled']:
            raise LookupError('unknown or disabled agent')
        return AgentMemory(self.memory, agent_id)

    def register_agent(self, agent_id, handler):
        if not isinstance(agent_id, str) or not agent_id.strip() or not callable(handler):
            raise ValueError("agent identity and callable handler required")
        agent = self.agents.get(agent_id)
        if not agent or not agent["enabled"]:
            raise LookupError("unknown or disabled agent")
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
            payload = job["payload"]
            actor = payload.get("submitted_by")
            if not self.identity.allowed(actor, "agents:dispatch"):
                raise ValueError("dispatch authorization no longer valid")
            if not self.memberships.allowed(job["agent"], actor, "dispatch"):
                raise ValueError("agent membership no longer valid")
            principal = payload.get("on_behalf_of")
            if principal is not None and not self.delegations.allowed(
                principal, actor, job["agent"], "agents:dispatch"
            ):
                raise ValueError("delegation no longer valid")
            handler = self.handlers.get(job["agent"])
            if handler is None:
                raise LookupError("agent handler unavailable")
            result = handler(job["payload"]["input"])
            self.jobs.finish(job["id"], result, job["lease_token"])
            return {"id": job["id"], "state": "completed", "result": result}
        except Exception as exc:
            try:
                self.jobs.fail(job["id"], str(exc), lease_token=job["lease_token"])
            except PermissionError:
                return {"id": job["id"], "state": "lease_lost", "error": str(exc)}
            return {"id": job["id"], "state": "failed", "error": str(exc)}

    def close(self):
        self.messages.close()
        self.collaboration.close()
        self.relationships.close()
        self.delegations.close()
        self.memberships.close()
        self.agents.close()
        self.memory.close()
        self.evidence.close()
        self.jobs.close()
        self.identity.close()
