-- First mainline persistence segment: event intake and resource scheduler foundation.
-- PostgreSQL 17. Safe to re-run; this file creates no business-domain tables.
-- Apply only through the dedicated SSH operations workflow.
BEGIN;

CREATE SCHEMA IF NOT EXISTS bridge AUTHORIZATION app_runtime;
ALTER SCHEMA bridge OWNER TO app_runtime;

CREATE TABLE IF NOT EXISTS bridge.events (
    event_id text PRIMARY KEY,
    source_app text NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL,
    status text NOT NULL DEFAULT 'received'
        CHECK (status IN ('received', 'processing', 'processed', 'failed', 'dead_letter')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    last_error text,
    received_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    processed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (length(event_id) BETWEEN 1 AND 180),
    CHECK (length(source_app) BETWEEN 1 AND 80),
    CHECK (length(event_type) BETWEEN 1 AND 200)
);

CREATE INDEX IF NOT EXISTS events_status_received_idx
    ON bridge.events (status, received_at);
CREATE INDEX IF NOT EXISTS events_type_received_idx
    ON bridge.events (event_type, received_at DESC);

CREATE TABLE IF NOT EXISTS bridge.tasks (
    task_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id text NOT NULL REFERENCES bridge.events(event_id) ON DELETE RESTRICT,
    task_type text NOT NULL,
    resource_key text,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'retry_wait', 'succeeded', 'failed', 'cancelled')),
    priority integer NOT NULL DEFAULT 100,
    attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    max_attempts integer NOT NULL DEFAULT 5 CHECK (max_attempts >= 1),
    available_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    started_at timestamptz,
    finished_at timestamptz,
    last_error text,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (length(task_type) BETWEEN 1 AND 160),
    CHECK (resource_key IS NULL OR length(resource_key) BETWEEN 1 AND 500),
    UNIQUE (event_id, task_type)
);

CREATE INDEX IF NOT EXISTS tasks_ready_idx
    ON bridge.tasks (status, available_at, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS tasks_event_idx
    ON bridge.tasks (event_id);
CREATE INDEX IF NOT EXISTS tasks_resource_status_idx
    ON bridge.tasks (resource_key, status);

CREATE TABLE IF NOT EXISTS bridge.idempotency_keys (
    scope text NOT NULL,
    idempotency_key text NOT NULL,
    request_hash text NOT NULL,
    status text NOT NULL DEFAULT 'processing'
        CHECK (status IN ('processing', 'completed', 'failed')),
    owner_task_id uuid REFERENCES bridge.tasks(task_id) ON DELETE SET NULL,
    result jsonb,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    expires_at timestamptz,
    PRIMARY KEY (scope, idempotency_key),
    CHECK (length(scope) BETWEEN 1 AND 160),
    CHECK (length(idempotency_key) BETWEEN 1 AND 500),
    CHECK (length(request_hash) BETWEEN 1 AND 256)
);

CREATE INDEX IF NOT EXISTS idempotency_expiry_idx
    ON bridge.idempotency_keys (expires_at)
    WHERE expires_at IS NOT NULL;

CREATE TABLE IF NOT EXISTS bridge.resource_locks (
    resource_key text PRIMARY KEY,
    owner_task_id uuid REFERENCES bridge.tasks(task_id) ON DELETE RESTRICT,
    acquired_at timestamptz,
    lease_until timestamptz,
    fencing_token bigint NOT NULL DEFAULT 0 CHECK (fencing_token >= 0),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK (length(resource_key) BETWEEN 1 AND 500),
    CHECK (
        (owner_task_id IS NULL AND acquired_at IS NULL AND lease_until IS NULL)
        OR
        (owner_task_id IS NOT NULL AND acquired_at IS NOT NULL AND lease_until IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS resource_locks_lease_idx
    ON bridge.resource_locks (lease_until)
    WHERE owner_task_id IS NOT NULL;

ALTER TABLE bridge.events OWNER TO app_runtime;
ALTER TABLE bridge.tasks OWNER TO app_runtime;
ALTER TABLE bridge.idempotency_keys OWNER TO app_runtime;
ALTER TABLE bridge.resource_locks OWNER TO app_runtime;

COMMIT;
