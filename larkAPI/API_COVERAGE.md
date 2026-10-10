# Bitable API Coverage Ledger

This ledger tracks endpoint coverage for the first-stage `larkAPI` method library.

## Status meanings

- `NOT_STARTED`: not yet inventoried or implemented.
- `INVENTORIED`: identified in the official API reference or SDK generated definitions.
- `WRAPPED_NOT_TESTED`: a named wrapper exists, but local type-check/tests have not yet passed.
- `IMPLEMENTED`: wrapper and local tests pass.
- `INTEGRATION_VERIFIED`: successful live request tested against an explicitly permitted test resource.
- `BLOCKED`: cannot be implemented or verified; reason documented.

## Current SDK-backed wrapper inventory

The first wrapper pass follows the official `@larksuiteoapi/node-sdk` generated Bitable client. Each entry below is a named method exported through `createBitableMethods(client)`. The wrappers preserve SDK arguments/results and normalize thrown errors. The package has **not yet been type-checked or integration-tested**.

| Resource | Wrapper methods | Status |
|---|---|---|
| App/Base | `apps.create`, `apps.get`, `apps.update`, `apps.copy` | WRAPPED_NOT_TESTED |
| Tables | `tables.create`, `tables.list`, `tables.update`, `tables.delete`, `tables.batchCreate`, `tables.batchDelete` | WRAPPED_NOT_TESTED |
| Records | `records.create`, `records.get`, `records.list`, `records.search`, `records.update`, `records.delete`, `records.batchCreate`, `records.batchGet`, `records.batchUpdate`, `records.batchDelete` | WRAPPED_NOT_TESTED |
| Fields | `fields.create`, `fields.list`, `fields.update`, `fields.delete` | WRAPPED_NOT_TESTED |
| Views | `views.create`, `views.get`, `views.list`, `views.update`, `views.delete` | WRAPPED_NOT_TESTED |
| Forms | `forms.get`, `forms.update`, `forms.upgrade`, `forms.listFields`, `forms.updateField` | WRAPPED_NOT_TESTED |
| Field groups | `fieldGroups.create` | WRAPPED_NOT_TESTED |
| Dashboards | `dashboards.list`, `dashboards.copy` | WRAPPED_NOT_TESTED |
| Roles and members | `roles.create`, `roles.list`, `roles.update`, `roles.delete`, `roles.listMembers`, `roles.createMember`, `roles.batchCreateMembers`, `roles.deleteMember`, `roles.batchDeleteMembers` | WRAPPED_NOT_TESTED |
| Workflows | `workflows.list`, `workflows.update`, `blockWorkflows.list` | WRAPPED_NOT_TESTED |

## Remaining full-coverage work

This initial wrapper list is **not yet proof of full Bitable API coverage**. Complete these tasks before declaring phase one complete:

1. Compare the SDK's generated Bitable API definitions with the current official Bitable server API reference, endpoint by endpoint.
2. Identify public endpoints missing from the pinned SDK version. Add a typed raw-request fallback only when the official API documents the endpoint.
3. Include all supported methods for resource families such as records, fields, views, forms, dashboards, automations/workflows, roles/permissions, advanced field types, and any additional Bitable APIs actually documented by the platform.
4. Record exact HTTP method, path, SDK semantic method, scopes, supported token types, pagination behavior, limits, and destructive/idempotency characteristics for each endpoint.
5. Type-check the package and add offline unit tests for wrapper routing, error normalization, and pagination.
6. Run live integration tests only against a designated test Base, after credentials and permissions are explicitly configured.
7. Update this ledger with tested status and a generated endpoint count. Do not claim completeness until all documented endpoints are accounted for.

## Endpoint inventory format

For every official endpoint, record:

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
- Do not auto-retry non-idempotent writes unless retry behavior is explicitly safe.
- Pagination helpers must stop safely and preserve platform continuation tokens.
- Errors must preserve the platform code/message and operation context without logging secrets.
- Live integration tests must use an explicitly designated test Base. Do not mutate a production Base to test write operations.
- Mark endpoints unavailable in the SDK separately from endpoints unavailable in the public API. Use a typed raw-request fallback only when official documentation supports the endpoint.

## Official references

- [Lark Open Platform](https://open.larksuite.com/)
- [Official Lark Node.js SDK](https://github.com/larksuite/node-sdk)
- [Official SDK package](https://www.npmjs.com/package/@larksuiteoapi/node-sdk)
- [Bitable API reference](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview)
