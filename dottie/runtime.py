"""Integrated local runtime for Dottie and independent agent handlers."""
from .identity import IdentityStore
from .jobs import JobQueue
from .evidence import EvidenceLedger
from .memory import ScopedMemory

class DottieRuntime:
    def __init__(self, database_path):
        self.identity = IdentityStore(database_path)
        self.jobs = JobQueue(database_path)
        self.evidence = EvidenceLedger(database_path)
        self.memory = ScopedMemory(database_path)
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
        return self.jobs.submit(agent_id, {"submitted_by": user_id, "input": payload}, idempotency_key)

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
        self.memory.close()
        self.evidence.close()
        self.jobs.close()
        self.identity.close()
