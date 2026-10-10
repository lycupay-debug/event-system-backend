# Bitable API Coverage Ledger

This ledger tracks endpoint coverage for the first-stage `larkAPI` method library.

**Status meanings**
- `NOT_STARTED`: not yet inventoried or implemented.
- `INVENTORIED`: official endpoint has been identified; method not yet implemented.
- `IMPLEMENTED`: wrapper exists and has a local test.
- `INTEGRATION_VERIFIED`: successful live request was tested against a permitted test resource.
- `BLOCKED`: cannot be implemented or verified yet; reason must be documented.

Do not mark a resource family complete until its official endpoint list has been compared with the current official API reference and SDK generated definitions.

## Scope

Include the Bitable Open API resource families, including (but not limited to):

| Resource family | Expected coverage | Status |
|---|---|---|
| App/Base metadata and management | Create, retrieve, update, copy, list/search where supported, delete where supported | NOT_STARTED |
| Tables | Create, list, retrieve, update, delete | NOT_STARTED |
| Fields | Create, list, retrieve, update, delete | NOT_STARTED |
| Records | Create, retrieve, list, update, delete, batch operations, search/filter, field-value operations where supported | NOT_STARTED |
| Views | Create, list, retrieve, update, delete, query view records where supported | NOT_STARTED |
| Forms | Form metadata, configuration, response/record operations where supported by public API | NOT_STARTED |
| Dashboards | Dashboard metadata and management where exposed by the public API | NOT_STARTED |
| Automation/workflows | Automation metadata and operations where exposed by the public API | NOT_STARTED |
| Roles and permissions | Role definitions, member assignment, resource permission operations where exposed by the public API | NOT_STARTED |
| Advanced data operations | Batch operations, field formatting, lookup/link/association support, attachment handling, formulas and field-type payloads | NOT_STARTED |
| Subscriptions/events | Bitable/Drive subscription endpoints relevant to Base changes where exposed by the public API | NOT_STARTED |
| Import/export and other Bitable-adjacent endpoints | Include only if documented as Bitable APIs; record API family and permissions | NOT_STARTED |

The table above is a planning taxonomy, not a final endpoint count. Some capabilities may belong to a different API product or may not be available as a public server API. Verify each entry before implementation.

## Endpoint inventory format

For every endpoint, record:

- Official endpoint name and documentation URL
- HTTP method and path
- SDK semantic method (or documented raw-request fallback)
- Required identifiers and parameters
- Required scopes and supported token types
- Pagination behavior and limits
- Request/response types
- Wrapper method name
- Unit-test status
- Live integration-test status
- Notes on destructive effects or idempotency

## Completion rules

- A resource-level generic pass-through is not a substitute for named methods.
- Do not silently drop unknown request or response fields.
- Do not auto-retry non-idempotent writes unless the retry behavior is explicitly safe.
- Pagination helpers must stop safely and preserve platform continuation tokens.
- Errors must preserve the platform code/message and the operation context without logging secrets.
- Live integration tests must use an explicitly designated test Base. Do not mutate a production Base to test write operations.
- Mark endpoints unavailable in the SDK separately from endpoints unavailable in the public API. Use a typed raw-request fallback only when official documentation supports the endpoint.
