"""Multi-user AEGIS assignments with per-agent membership and scoped access."""
import sqlite3

MEMBER_ROLES = frozenset({"operator", "collaborator", "observer"})
PERMISSIONS = {
    "operator": frozenset({"dispatch", "read", "write", "manage"}),
    "collaborator": frozenset({"dispatch", "read", "write"}),
    "observer": frozenset({"read"}),
}

class AgentMemberships:
    def __init__(self, database_path):
        self.db = sqlite3.connect(database_path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS aegis_memberships (
            agent_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            PRIMARY KEY(agent_id, user_id),
            FOREIGN KEY(agent_id) REFERENCES aegis_agents(id),
            FOREIGN KEY(user_id) REFERENCES users(id))""")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.commit()

    def grant(self, agent_id, user_id, role, granted_by):
        if role not in MEMBER_ROLES:
            raise ValueError("invalid membership role")
        self._require_agent(agent_id)
        self._require_user(user_id)
        if not self._can_manage(granted_by, agent_id):
            raise PermissionError("agent membership management denied")
        with self.db:
            self.db.execute("""INSERT INTO aegis_memberships VALUES (?,?,?)
                ON CONFLICT(agent_id,user_id) DO UPDATE SET role=excluded.role""",
                (agent_id, user_id, role))

    def bootstrap_owner(self, agent_id, owner_id):
        self._require_agent(agent_id)
        row = self.db.execute(
            "SELECT role FROM users WHERE id=? AND active=1", (owner_id,)).fetchone()
        if not row or row[0] != "owner":
            raise PermissionError("only the system owner can bootstrap")
        with self.db:
            self.db.execute("""INSERT OR IGNORE INTO aegis_memberships
                VALUES (?,?,?)""", (agent_id, owner_id, "operator"))

    def revoke(self, agent_id, user_id, revoked_by):
        if not self._can_manage(revoked_by, agent_id):
            raise PermissionError("agent membership management denied")
        with self.db:
            self.db.execute("DELETE FROM aegis_memberships WHERE agent_id=? AND user_id=?",
                            (agent_id, user_id))

    def allowed(self, agent_id, user_id, action):
        row = self.db.execute("""SELECT m.role FROM aegis_memberships m
            JOIN users u ON u.id=m.user_id
            JOIN aegis_agents a ON a.id=m.agent_id
            WHERE m.agent_id=? AND m.user_id=? AND u.active=1 AND a.enabled=1""",
            (agent_id, user_id)).fetchone()
        return bool(row and action in PERMISSIONS[row[0]])

    def members(self, agent_id, requested_by):
        if not self.allowed(agent_id, requested_by, "read"):
            raise PermissionError("membership visibility denied")
        return [{"user_id": uid, "role": role} for uid, role in
                self.db.execute("""SELECT user_id,role FROM aegis_memberships
                    WHERE agent_id=? ORDER BY user_id""", (agent_id,))]

    def _can_manage(self, user_id, agent_id):
        row = self.db.execute("SELECT role FROM users WHERE id=? AND active=1",
                              (user_id,)).fetchone()
        return bool(row and (row[0] == "owner" or
                            self.allowed(agent_id, user_id, "manage")))

    def _require_agent(self, agent_id):
        if not self.db.execute("SELECT 1 FROM aegis_agents WHERE id=?", (agent_id,)).fetchone():
            raise LookupError("unknown agent")

    def _require_user(self, user_id):
        if not self.db.execute("SELECT 1 FROM users WHERE id=? AND active=1", (user_id,)).fetchone():
            raise LookupError("unknown active user")

    def close(self):
        self.db.close()
