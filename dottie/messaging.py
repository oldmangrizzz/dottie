"""Natural-language message transport for independent AEGIS agents.

Messages are addressed, durable, plain-text data. They never invoke tools,
grant capabilities, or carry executable instructions through this transport.
"""
import sqlite3
import time
import uuid
from .transport import NaturalLanguageEnvelope

PRINCIPAL_ID = "dottie"

class AgentMessages:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_messages (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at REAL NOT NULL)""")
        self.db.execute("CREATE INDEX IF NOT EXISTS aegis_messages_recipient ON aegis_messages(recipient,created_at)")
        self.db.commit()

    def send(self, sender, recipient, text):
        envelope = NaturalLanguageEnvelope(sender, recipient, text)
        for agent_id in (sender, recipient):
            row = (1,) if agent_id == PRINCIPAL_ID else self.db.execute("SELECT enabled FROM aegis_agents WHERE id=?",
                                  (agent_id,)).fetchone()
            if not row or not row[0]:
                raise LookupError("unknown or disabled agent")
        message_id = str(uuid.uuid4())
        with self.db:
            self.db.execute("INSERT INTO aegis_messages VALUES (?,?,?,?,?)",
                            (message_id, sender, recipient, text, time.time()))
        return message_id

    def inbox(self, recipient):
        if recipient != PRINCIPAL_ID and not self.db.execute("SELECT 1 FROM aegis_agents WHERE id=?",
                               (recipient,)).fetchone():
            raise LookupError("unknown recipient")
        rows = self.db.execute("""SELECT id,sender,text,created_at
            FROM aegis_messages WHERE recipient=? ORDER BY created_at,id""",
            (recipient,))
        return [{"id": id, "sender": sender, "text": text, "created_at": timestamp}
                for id, sender, text, timestamp in rows]

    def close(self):
        self.db.close()
