"""Participant-scoped durable journal of AEGIS collaborative experiences."""
import json
import sqlite3
import time
import uuid

class CollaborationJournal:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_experiences (
            id TEXT PRIMARY KEY, mission_id TEXT NOT NULL,
            summary TEXT NOT NULL, outcome_json TEXT NOT NULL,
            created_at REAL NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_experience_participants (
            experience_id TEXT NOT NULL REFERENCES aegis_experiences(id),
            agent_id TEXT NOT NULL REFERENCES aegis_agents(id),
            PRIMARY KEY(experience_id,agent_id))""")
        self.db.commit()

    def record(self, mission_id, participants, summary, outcome):
        if not mission_id or not isinstance(summary, str) or not summary.strip():
            raise ValueError("mission and summary required")
        if not isinstance(participants, (list, tuple)) or len(participants) < 2:
            raise ValueError("at least two agents required")
        if len(set(participants)) != len(participants):
            raise ValueError("duplicate participants")
        for agent_id in participants:
            row = self.db.execute("SELECT enabled FROM aegis_agents WHERE id=?",
                                  (agent_id,)).fetchone()
            if not row or not row[0]:
                raise LookupError("unknown or disabled participant")
        event_id = str(uuid.uuid4())
        with self.db:
            self.db.execute("INSERT INTO aegis_experiences VALUES (?,?,?,?,?)",
                            (event_id, mission_id, summary, json.dumps(outcome), time.time()))
            self.db.executemany(
                "INSERT INTO aegis_experience_participants VALUES (?,?)",
                [(event_id, agent_id) for agent_id in participants])
        return event_id

    def history(self, agent_id):
        if not self.db.execute("SELECT 1 FROM aegis_agents WHERE id=?",
                               (agent_id,)).fetchone():
            raise LookupError("unknown agent")
        rows = self.db.execute("""SELECT e.id,e.mission_id,e.summary,e.outcome_json,e.created_at
            FROM aegis_experiences e JOIN aegis_experience_participants p
            ON p.experience_id=e.id WHERE p.agent_id=?
            ORDER BY e.created_at,e.id""", (agent_id,))
        return [{"id": id, "mission_id": mission, "summary": summary,
                 "outcome": json.loads(outcome), "created_at": created}
                for id, mission, summary, outcome, created in rows]

    def close(self):
        self.db.close()
