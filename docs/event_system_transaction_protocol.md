# Event System Transaction Protocol (Review Draft)

Status: protocol specification draft; this document changes no production behavior or database schema.
Scope: define transaction boundaries and failure semantics before implementing PostgreSQL-backed ingress, parsing, and scheduling.
Authority: follows the confirmed invariants in the Notion page "事件系统总后端：PostgreSQL DDL 初稿与事务并发协议". Any change to global ordering, per-resource ordering, UNKNOWN blocking, retry semantics, or transaction boundaries requires user review first.

## 1. Invariants

1. PostgreSQL is the authoritative store for runtime state; in-memory queues only wake workers.
2. Events receive a strict global ingress order before parsing and resource routing.
3. The earliest unresolved event cannot be bypassed by a later event during parsing.
4. Tasks for one resource execute strictly in resource sequence; different resources may execute concurrently.
5. A task state change and its corresponding Outbox intent commit in the same transaction.
6. External API calls happen outside database transactions.
7. An uncertain external result is UNKNOWN, not an assumed failure. UNKNOWN blocks subsequent tasks for that resource until verified or explicitly handled by an authorized operator.
8. Expired leases mean ownership must be recovered; they do not prove an external operation failed.
9. Core state mutations go through a repository/transaction protocol; business modules must not write core tables ad hoc.

## 2. Event identity and ingress transaction

### Stable identity

- Prefer the source platform's stable event ID.
- If absent, compute a deterministic digest from canonicalized source and event payload.
- Store source identity and a source-scoped dedupe key. A unique constraint remains the final race-safety guard.
- Re-delivery of the same logical event returns the existing receipt; it must not create a second logical event or task.
- A duplicate ID with materially different content should be surfaced as an identity conflict for audit; do not silently overwrite the first payload.

### Global order / linearization point

A normal PostgreSQL sequence guarantees unique allocation, not transaction commit order. The intended strict-order protocol uses the singleton ingress_clock row as the serialization point:

1. Begin a short transaction.
2. Lock the singleton clock row with SELECT FOR UPDATE.
3. Check for an existing (source, dedupe_key) and, when supplied, (source, source_event_id). If found, return the existing event as a duplicate without allocating a new sequence.
4. Increment last_ingest_seq and obtain the new value.
5. Insert the Inbox event with that sequence and its immutable source payload.
6. Commit. The clock-row lock is held through commit, so a later ingress transaction cannot allocate the next sequence before this transaction commits or rolls back.
7. Only after commit, acknowledge the source and/or signal the worker.

If the transaction rolls back, both clock increment and event insert roll back. If the commit response is lost, a retry resolves through the dedupe key. Unique constraints remain necessary even though ingress is serialized.

Trade-off: this deliberately serializes the short ingress transaction and can cap intake throughput. Measure contention before optimizing; do not replace it with an ordinary sequence without changing the ordering guarantee and obtaining review.

## 3. Global ordered parser lease

Parser ownership is coordinated by a durable singleton control row, not a process-local mutex.

1. Acquire or recover the parser lease in a short transaction. A new ownership epoch increments the fencing token; renewal preserves the token.
2. The parser may work only with the token it acquired. Every state-changing commit checks that the token is still current.
3. Select the lowest ingest_seq whose parsing/resource assignment is unresolved. Do not skip an earlier event because a later event is easier to parse.
4. Claim the event with owner and expiry, then commit the claim before doing non-database work.
5. After parsing and resource resolution, begin a new short transaction and revalidate parser token and event claim.
6. In that transaction, create any missing resource cursors, allocate resource sequence numbers in stable order, create jobs, and mark the Inbox event parsed/processed. Commit all of these together.
7. If a claim expires, recovery may reclaim it only after checking durable state. A stale parser's token must not permit writes after a newer owner takes over.

A retryable parse failure remains the earliest unresolved event and is retried according to policy; later events do not pass it. A permanently unprocessable event blocks the global parser until repaired or explicitly resolved through an audited, authorized decision. The system must not silently mark it processed merely to unblock throughput.

## 4. Resource sequence allocation

For each resolved resource, lock its resource_cursors row inside the job-creation transaction.

1. Process jobs generated by one event in a deterministic order (job_ordinal or an equivalent stable ordering key).
2. Allocate one unique resource_seq per logical job from the cursor's next_seq.
3. Insert each job with its assigned sequence and advance next_seq in the same transaction.
4. Enforce uniqueness on (resource_key, resource_seq); the constraint detects duplicates but does not itself guarantee continuity or correct order.
5. Never renumber already committed jobs to repair a gap. Investigate the transaction and durable records instead.

The job-creation transaction also updates the Inbox parse state. If any insert or update fails, all sequence allocations and jobs roll back together.

## 5. Task claim and external execution

Claiming a task is a short transaction:

1. Lock the resource cursor and lease rows in a consistent global lock order.
2. Reject the claim if the resource is blocked, another valid lease exists, or the task sequence is not completed_seq + 1.
3. Increment the resource fencing token and write owner, job, and lease expiry.
4. Set the task to RUNNING and insert an immutable attempt record with worker ID, attempt number, and fencing token.
5. Commit before calling the external API.

The external call must not run while a database transaction is open. A fencing token prevents stale workers from committing database state, but does not by itself prevent an external service from accepting an old request. External idempotency and result verification remain necessary.

## 6. Result commit, failure, and UNKNOWN

### Confirmed success

In one transaction:
- verify task state, current resource lease, and fencing token;
- mark the attempt and job successful;
- advance the contiguous completed_seq only for the expected next sequence;
- insert all follow-up Outbox events with stable idempotency keys;
- release or renew the resource lease according to the scheduler protocol;
- commit.

Any failed check aborts the whole transaction. A stale worker must not overwrite newer state.

### Confirmed failure

Record the attempt result and choose RETRY_WAIT or FAILED according to the task policy. The failed/incomplete sequence continues to block later tasks for that resource. If an external side effect may have occurred, verify it before retrying; an HTTP error or timeout alone is not proof that no side effect occurred.

### UNKNOWN

When the external outcome cannot be established:
- record the attempt as UNKNOWN with verification status and available external request identifiers/evidence;
- set the job to UNKNOWN and the resource's blocked reason in one transaction;
- do not advance completed_seq;
- deny all later claims for this resource, while allowing unrelated resources to continue.

Verification outcomes:
- confirmed success: atomically finalize the job, advance the cursor, create Outbox intents, and clear the block only when the next sequence is safe;
- confirmed no effect: retry only when the operation's retry policy is safe;
- inconclusive: retain UNKNOWN and the resource block;
- manual decision: require actor, reason, evidence, decision, and an audit record; the controlled transaction must explicitly define how the cursor is resolved.

"Not found" is not automatically equivalent to "no effect". If the external system offers neither reliable lookup nor idempotency, keep the resource blocked until evidence or an authorized decision exists.

## 7. Transactional Outbox

1. Insert the Outbox row in the same transaction as the business state change that requires it.
2. A dispatcher claims due rows atomically, recording owner, lease expiry, and an incrementing claim/fencing token.
3. Commit the claim before sending over the network.
4. On an explicit matching acknowledgement, mark SENT only if the claim token still matches.
5. On timeout or process crash, the outcome may be uncertain. Inspect/reconcile when supported; otherwise retry according to policy with the same stable event key.
6. Delivery is at-least-once, not universally exactly-once. Downstream consumers must deduplicate by stable event key.

## 8. Recovery and concurrency rules

- Recovery scans are repeatable and idempotent; database state, not process memory, determines what remains to be done.
- Recover expired Inbox claims, parser ownership, task leases, UNKNOWN verification work, and Outbox claims independently.
- Never infer external failure solely from an expired lease.
- Acquire multiple database locks in a consistent order to reduce deadlocks. Keep transactions short; never wait for an external API inside one.
- Use compare-and-set state transitions and fencing-token checks on all ownership-sensitive writes.
- Tests must include duplicate concurrent ingress, rollback of sequence allocation, parser crash/reclaim, stale-token writes, concurrent same-resource claims, different-resource parallel claims, UNKNOWN blocking, Outbox acknowledgement loss, and restart recovery.

## 9. Implementation boundary and acceptance

This specification does not authorize applying the Notion DDL draft. The current bridge.* schema is an interim implementation foundation; the target event_system.* schema is still a draft. Before production integration, explicitly choose and review a migration path so the application does not maintain two competing runtime truths.

Next implementation stage after this protocol is reviewed:
1. settle the final schema/migration boundary;
2. implement a dedicated ingress repository with transaction-level tests;
3. integrate it behind a controlled feature boundary without removing existing JSON recovery until parity tests pass;
4. only then implement the globally ordered parser lease and resource sequence assignment.

Acceptance for this specification stage: protocol boundaries and failure semantics are written down; no production DDL, runtime code path, environment configuration, or running container is changed.
