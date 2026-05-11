# Directive: Database Setup

**Goal:** Create the SQLite database schema and connection utilities.

**Inputs:** Refer to `project_plan.md` Section 10 (Database Layer).
**Outputs:**
1. Create `database/schema.sql` with the `snapshots`, `trend_scores`, and `reports` tables.
2. Create `database/db.py` to handle the SQLite connection and initialize the schema into `market_data.db`.

- Write deterministic, testable Python and SQL code.
- Ensure `db.py` correctly initializes the schema if it doesn't exist.
- Once the files are created, use the SQLite MCP server tool to verify that the 3 tables were successfully created in the database. If not, self-anneal and fix the connection.

**Known edge cases (learned during execution):**
- Windows terminals use cp1252 encoding by default. Avoid Unicode emoji in print statements inside `db.py` — they cause `UnicodeEncodeError`. Use plain ASCII like `[OK]` instead.
- Use `py` (not `python`) to invoke Python on this machine; `python` is not on PATH.
- `sqlite_sequence` is an internal SQLite table that appears alongside user-created tables — this is expected and not a schema error.

**Status: COMPLETE** — `database/schema.sql` and `database/db.py` created and verified via SQLite MCP. Tables confirmed: `snapshots`, `trend_scores`, `reports`.