"""Durable, reciprocal social relationships between independent AEGIS agents.

Friendship records shared history, not authority or access rights.
"""
import sqlite3
import time

class AgentRelationships:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_friendships (
            agent_a TEXT NOT NULL REFERENCES aegis_agents(id),
            agent_b TEXT NOT NULL REFERENCES aegis_agents(id),
            shared_context TEXT NOT NULL,
            established_at REAL NOT NULL,
            ended_at REAL,
            PRIMARY KEY(agent_a, agent_b),
            CHECK(agent_a < agent_b))""")
        self.db.commit()

    def _pair(self, first, second):
        if first == second:
            raise ValueError("an agent cannot befriend itself")
        for agent_id in (first, second):
            row = self.db.execute(
                "SELECT enabled FROM aegis_agents WHERE id=?", (agent_id,)).fetchone()
            if not row or not row[0]:
                raise LookupError("unknown or disabled agent")
        return tuple(sorted((first, second)))

    def befriend(self, first, second, shared_context):
        a, b = self._pair(first, second)
        if not isinstance(shared_context, str):
            raise ValueError("shared context must be text")
        with self.db:
            self.db.execute("""INSERT INTO aegis_friendships VALUES (?,?,?,?,NULL)
                ON CONFLICT(agent_a,agent_b) DO UPDATE SET
                shared_context=excluded.shared_context,
                established_at=excluded.established_at, ended_at=NULL""",
                (a, b, shared_context, time.time()))

    def are_friends(self, first, second):
        a, b = self._pair(first, second)
        return bool(self.db.execute("""SELECT 1 FROM aegis_friendships
            WHERE agent_a=? AND agent_b=? AND ended_at IS NULL""",
            (a, b)).fetchone())

    def friends(self, agent_id):
        if not self.db.execute("SELECT 1 FROM aegis_agents WHERE id=?", (agent_id,)).fetchone():
            raise LookupError("unknown agent")
        rows = self.db.execute("""SELECT agent_a,agent_b,shared_context,established_at
            FROM aegis_friendships WHERE ended_at IS NULL
            AND (agent_a=? OR agent_b=?) ORDER BY established_at""",
            (agent_id, agent_id))
        return [{"agent_id": b if a == agent_id else a,
                 "shared_context": context, "established_at": created}
                for a, b, context, created in rows]

    def end_friendship(self, first, second):
        a, b = self._pair(first, second)
        with self.db:
            self.db.execute("""UPDATE aegis_friendships SET ended_at=?
                WHERE agent_a=? AND agent_b=? AND ended_at IS NULL""",
                (time.time(), a, b))

    def close(self):
        self.db.close()
