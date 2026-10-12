"""PostgreSQL connection helper for the Feishu bridge."""
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
