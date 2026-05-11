"""
database/db.py — SQLite connection and schema initialization.

Provides get_connection() which:
  1. Opens (or creates) the SQLite database at DB_PATH.
  2. Initializes the schema from schema.sql if tables do not yet exist.
  3. Returns the connection with Row factory enabled for dict-like access.
"""

import sqlite3
import os

# Allow override via .env (e.g. DB_PATH=database/market_analyzer.db)
_path = os.getenv("DB_PATH", "market_data.db")
# If relative, make it relative to the PROJECT ROOT, not the database folder
if not os.path.isabs(_path):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(PROJECT_ROOT, _path)
else:
    DB_PATH = _path

def get_connection() -> sqlite3.Connection:
    """Open the SQLite database, initialize schema, and return the connection."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # Rows accessible by column name
    _initialize_schema(conn)
    return conn


def _initialize_schema(conn: sqlite3.Connection) -> None:
    """Run schema.sql once to create tables and indexes if they don't exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.commit()


if __name__ == "__main__":
    # Quick smoke-test: initialize DB and confirm tables exist
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    tables = [row["name"] for row in cursor.fetchall()]
    print(f"[OK] Database initialized at: {os.path.abspath(DB_PATH)}")
    print(f"     Tables found: {tables}")
    conn.close()
