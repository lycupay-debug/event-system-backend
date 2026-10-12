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


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL driver verification")
    parser.add_argument("action", choices=("check",))
    args = parser.parse_args()
    if args.action == "check":
        print(inspect_connection())


if __name__ == "__main__":
    main()
