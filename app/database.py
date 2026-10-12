"""PostgreSQL connection and database operation helpers.

Connection secrets are read only from DATABASE_URL in the process environment.
Never log the DSN, connection parameters, or database credentials.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterable, Iterator, Mapping, Sequence

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


Params = Sequence[Any] | Mapping[str, Any] | None


def connect() -> psycopg.Connection[Any]:
    """Open a connection using DATABASE_URL; never expose its value in errors."""
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(
        dsn,
        connect_timeout=5,
        application_name="feishu-bridge",
        row_factory=dict_row,
    )


@contextmanager
def using_connection(connection: psycopg.Connection[Any] | None = None) -> Iterator[psycopg.Connection[Any]]:
    """Reuse a caller-owned connection, or own/close a connection for one operation."""
    if connection is not None:
        yield connection
    else:
        with connect() as owned:
            yield owned


@contextmanager
def transaction() -> Iterator[psycopg.Connection[Any]]:
    """Run multiple operations atomically; commit on success and roll back on error."""
    with connect() as conn:
        with conn.transaction():
            yield conn


def fetch_one(query: str | sql.Composable, params: Params = None, *, connection: psycopg.Connection[Any] | None = None) -> dict[str, Any] | None:
    """Execute a parameterized query and return one row as a dictionary."""
    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return cur.fetchone()


def fetch_all(query: str | sql.Composable, params: Params = None, *, connection: psycopg.Connection[Any] | None = None) -> list[dict[str, Any]]:
    """Execute a parameterized query and return all rows as dictionaries."""
    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return list(cur.fetchall())


def execute(query: str | sql.Composable, params: Params = None, *, connection: psycopg.Connection[Any] | None = None) -> int:
    """Execute one statement and return its affected-row count, if provided by the driver."""
    with using_connection(connection) as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.rowcount


def execute_many(query: str | sql.Composable, params_seq: Iterable[Sequence[Any] | Mapping[str, Any]], *, connection: psycopg.Connection[Any] | None = None) -> int:
    """Execute a parameterized statement for multiple parameter sets."""
    with using_connection(connection) as conn, conn.cursor() as cur:
        cur.executemany(query, params_seq)
        return cur.rowcount


def insert_one(
    table: str,
    values: Mapping[str, Any],
    *,
    schema: str = "public",
    returning: Sequence[str] = ("*",),
    connection: psycopg.Connection[Any] | None = None,
) -> dict[str, Any] | None:
    """Insert one row with safely composed identifiers and bound values."""
    if not values:
        raise ValueError("values must not be empty")
    columns = list(values.keys())
    returning_sql = sql.SQL("*") if tuple(returning) == ("*",) else sql.SQL(", ").join(map(sql.Identifier, returning))
    statement = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({}) RETURNING {}").format(
        sql.Identifier(schema),
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns),
        returning_sql,
    )
    with using_connection(connection) as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(statement, [values[column] for column in columns])
        return cur.fetchone()


def get_by_id(
    table: str,
    id_column: str,
    id_value: Any,
    *,
    schema: str = "public",
    connection: psycopg.Connection[Any] | None = None,
) -> dict[str, Any] | None:
    """Fetch one row by a caller-specified key column."""
    statement = sql.SQL("SELECT * FROM {}.{} WHERE {} = %s LIMIT 1").format(
        sql.Identifier(schema), sql.Identifier(table), sql.Identifier(id_column)
    )
    return fetch_one(statement, (id_value,), connection=connection)


def update_by_id(
    table: str,
    id_column: str,
    id_value: Any,
    values: Mapping[str, Any],
    *,
    schema: str = "public",
    connection: psycopg.Connection[Any] | None = None,
) -> dict[str, Any] | None:
    """Update one row by key and return the updated row; returns None if absent."""
    if not values:
        raise ValueError("values must not be empty")
    columns = list(values.keys())
    statement = sql.SQL("UPDATE {}.{} SET {} WHERE {} = %s RETURNING *").format(
        sql.Identifier(schema),
        sql.Identifier(table),
        sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(column)) for column in columns
        ),
        sql.Identifier(id_column),
    )
    return fetch_one(statement, [values[column] for column in columns] + [id_value], connection=connection)


def delete_by_id(
    table: str,
    id_column: str,
    id_value: Any,
    *,
    schema: str = "public",
    connection: psycopg.Connection[Any] | None = None,
) -> dict[str, Any] | None:
    """Delete one row by key and return the deleted row; returns None if absent."""
    statement = sql.SQL("DELETE FROM {}.{} WHERE {} = %s RETURNING *").format(
        sql.Identifier(schema), sql.Identifier(table), sql.Identifier(id_column)
    )
    return fetch_one(statement, (id_value,), connection=connection)


def list_tables(*, schema: str = "public", connection: psycopg.Connection[Any] | None = None) -> list[dict[str, Any]]:
    """List ordinary and partitioned tables visible in a schema."""
    return fetch_all(
        """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
        (schema,),
        connection=connection,
    )


def describe_table(table: str, *, schema: str = "public", connection: psycopg.Connection[Any] | None = None) -> list[dict[str, Any]]:
    """Return column metadata for an existing table without reading row data."""
    return fetch_all(
        """
        SELECT column_name, data_type, is_nullable, column_default, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema, table),
        connection=connection,
    )


def inspect_connection() -> dict[str, Any]:
    """Return non-secret database and role metadata."""
    row = fetch_one(
        """
        SELECT current_database() AS database,
               current_user AS user,
               r.rolsuper AS is_superuser,
               current_setting('server_version') AS server_version
        FROM pg_roles AS r
        WHERE r.rolname = current_user
        """
    )
    if row is None:
        raise RuntimeError("Could not inspect the current PostgreSQL role")
    return row


def probe_write() -> dict[str, Any]:
    """Verify temporary CREATE, INSERT, SELECT, UPDATE, and DELETE operations."""
    with transaction() as conn:
        execute(
            """
            CREATE TEMPORARY TABLE driver_write_probe (
                id integer PRIMARY KEY,
                marker text NOT NULL
            ) ON COMMIT DROP
            """,
            connection=conn,
        )
        inserted = insert_one(
            "driver_write_probe",
            {"id": 1, "marker": "psycopg-write-probe"},
            schema="pg_temp",
            connection=conn,
        )
        updated = update_by_id(
            "driver_write_probe", "id", 1, {"marker": "psycopg-update-probe"},
            schema="pg_temp", connection=conn,
        )
        fetched = get_by_id("driver_write_probe", "id", 1, schema="pg_temp", connection=conn)
        deleted = delete_by_id("driver_write_probe", "id", 1, schema="pg_temp", connection=conn)
        if not inserted or inserted["marker"] != "psycopg-write-probe":
            raise RuntimeError("PostgreSQL insert probe failed")
        if not updated or updated["marker"] != "psycopg-update-probe":
            raise RuntimeError("PostgreSQL update probe failed")
        if not fetched or fetched["marker"] != "psycopg-update-probe":
            raise RuntimeError("PostgreSQL select probe failed")
        if not deleted or deleted["id"] != 1:
            raise RuntimeError("PostgreSQL delete probe failed")
    return {"insert": "passed", "select": "passed", "update": "passed", "delete": "passed", "persistent_objects_created": False}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL operation interface verification")
    parser.add_argument("action", choices=("check", "probe-write", "list-tables"))
    args = parser.parse_args()
    if args.action == "check":
        result = inspect_connection()
    elif args.action == "probe-write":
        result = probe_write()
    else:
        result = {"tables": list_tables()}
    print(result)


if __name__ == "__main__":
    main()
