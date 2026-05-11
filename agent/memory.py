import sqlite3
import json
from datetime import datetime
from database.db import get_db_connection

class AgentMemory:
    """
    SQLite-backed memory for the ReAct Agent to maintain session context.
    """
    def __init__(self, session_id="default"):
        self.session_id = session_id
        self._init_db()

    def _init_db(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add_message(self, role, content):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agent_memory (session_id, role, content) VALUES (?, ?, ?)",
            (self.session_id, role, content)
        )
        conn.commit()
        conn.close()

    def get_history(self, limit=10):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM agent_memory WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (self.session_id, limit)
        )
        history = cursor.fetchall()
        conn.close()
        # Reverse to get chronological order
        return history[::-1]

    def clear_memory(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agent_memory WHERE session_id = ?", (self.session_id,))
        conn.commit()
        conn.close()
