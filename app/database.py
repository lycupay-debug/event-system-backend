"""PostgreSQL connection and verification helpers for the Feishu bridge."""
from __future__ import annotations

import os
from typing import Any

import psycopg


def connect() -> psycopg.Connection[Any]:
    """Connect using DATABASE_URL from the process environment.

    Callers must never log DATABASE_URL or any connection parameters.
    """
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(dsn, connect_timeout=5, application_name="feishu-bridge")


def inspect_connection() -> dict[str, Any]:
    """Return non-secret database and role metadata."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT current_database(),
                   current_user,
                   r.rolsuper,
                   current_setting('server_version')
            FROM pg_roles AS r
            WHERE r.rolname = current_user
            """
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Could not inspect the current PostgreSQL role")
        return {
            "database": row[0],
            "user": row[1],
            "is_superuser": bool(row[2]),
            "server_version": row[3],
        }


def probe_write() -> dict[str, Any]:
    """Verify temporary CREATE, INSERT, and SELECT without persistent schema changes."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TEMPORARY TABLE driver_write_probe (
                id integer PRIMARY KEY,
                marker text NOT NULL
            ) ON COMMIT DROP
            """
        )
        cur.execute(
            "INSERT INTO driver_write_probe (id, marker) VALUES (%s, %s)",
            (1, "psycopg-write-probe"),
        )
        cur.execute("SELECT marker FROM driver_write_probe WHERE id = %s", (1,))
        row = cur.fetchone()
        if row is None or row[0] != "psycopg-write-probe":
            raise RuntimeError("PostgreSQL driver write/read probe returned an unexpected value")
        return {"write_read": "passed", "persistent_objects_created": False}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL driver verification")
    parser.add_argument("action", choices=("check", "probe-write"))
    args = parser.parse_args()
    result = inspect_connection() if args.action == "check" else probe_write()
    print(result)


if __name__ == "__main__":
    main()
