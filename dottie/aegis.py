"""Canonical independent AEGIS identities.

Identity and ownership persist independently of any execution model or worker.
"""
import sqlite3

COMMANDOS = (
    ("dugan", "Timothy Aloysius Cadwallader Dugan"),
    ("jones", "Gabe Jones"),
    ("morita", "Jim Morita"),
    ("falsworth", "James Montgomery Falsworth"),
    ("dernier", "Jacques Dernier"),
)

class AgentRegistry:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_agents (
            id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
            commander TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1)""")
        with self.db:
            for agent_id, name in COMMANDOS:
                self.db.execute("""INSERT OR IGNORE INTO aegis_agents
                    (id,display_name,commander,enabled) VALUES (?,?,?,1)""",
                    (agent_id, name, "dottie"))

    def list_agents(self):
        return [{"id": r[0], "name": r[1], "commander": r[2], "enabled": bool(r[3])}
                for r in self.db.execute(
                    "SELECT id,display_name,commander,enabled FROM aegis_agents ORDER BY id")]

    def get(self, agent_id):
        row = self.db.execute("""SELECT id,display_name,commander,enabled
            FROM aegis_agents WHERE id=?""", (agent_id,)).fetchone()
        return ({"id": row[0], "name": row[1], "commander": row[2],
                 "enabled": bool(row[3])} if row else None)

    def close(self):
        self.db.close()
