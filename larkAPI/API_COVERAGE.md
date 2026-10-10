# Bitable API Coverage Ledger

This ledger tracks the first-stage `larkAPI` wrapper surface against the official Lark Node.js SDK generated Bitable API definitions.

## Status meanings

- `WRAPPED_NOT_TESTED`: named wrapper exists; package compilation passed, but that endpoint has not been live-tested.
- `IMPLEMENTED`: wrapper and local tests pass.
- `INTEGRATION_VERIFIED`: successful live request tested against an explicitly permitted test resource.
- `GAP`: documented public endpoint is not yet wrapped.
- `BLOCKED`: cannot be implemented or verified; reason documented.

## SDK-generated endpoint inventory

The pinned SDK generated Bitable client exposes 49 unique operation/version combinations in its `bitable` client surface. The wrapper exposes all 49 as named methods. Offline tests now verify the wrapper count, payload forwarding for every exposed method, normalized SDK failure context, pagination safeguards, and error normalization. Type-check, declaration build, and unit tests are run against a disposable clone. These tests do not prove every endpoint's remote contract or live availability. Endpoint-by-endpoint documentation reconciliation and live API tests remain outstanding.

| # | API resource | Operation | HTTP | Path | Wrapper | Status |
|---:|---|---|---|---|---|---|
| 1 | app.table | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id` | `tables.update` | WRAPPED_NOT_TESTED |
| 2 | app.table | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/tables/batch_delete` | `tables.batchDelete` | WRAPPED_NOT_TESTED |
| 3 | app.table | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/batch_create` | `tables.batchCreate` | WRAPPED_NOT_TESTED |
| 4 | app.table | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables` | `tables.create` | WRAPPED_NOT_TESTED |
| 5 | app.table | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id` | `tables.delete` | WRAPPED_NOT_TESTED |
| 6 | app.table | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables` | `tables.list` | WRAPPED_NOT_TESTED |
| 7 | app.dashboard | copy | POST | `/open-apis/bitable/v1/apps/:app_token/dashboards/:block_id/copy` | `dashboards.copy` | WRAPPED_NOT_TESTED |
| 8 | app.dashboard | list | GET | `/open-apis/bitable/v1/apps/:app_token/dashboards` | `dashboards.list` | WRAPPED_NOT_TESTED |
| 9 | app | update | PUT | `/open-apis/bitable/v1/apps/:app_token` | `apps.update` | WRAPPED_NOT_TESTED |
| 10 | app | copy | POST | `/open-apis/bitable/v1/apps/:app_token/copy` | `apps.copy` | WRAPPED_NOT_TESTED |
| 11 | app | create | POST | `/open-apis/bitable/v1/apps` | `apps.create` | WRAPPED_NOT_TESTED |
| 12 | app | get | GET | `/open-apis/bitable/v1/apps/:app_token` | `apps.get` | WRAPPED_NOT_TESTED |
| 13 | app.table.record | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_delete` | `records.batchDelete` | WRAPPED_NOT_TESTED |
| 14 | app.table.record | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_create` | `records.batchCreate` | WRAPPED_NOT_TESTED |
| 15 | app.table.record | batch_update | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_update` | `records.batchUpdate` | WRAPPED_NOT_TESTED |
| 16 | app.table.record | update | PUT | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | `records.update` | WRAPPED_NOT_TESTED |
| 17 | app.table.record | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records` | `records.create` | WRAPPED_NOT_TESTED |
| 18 | app.table.record | search | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/search` | `records.search` | WRAPPED_NOT_TESTED |
| 19 | app.table.record | batch_get | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_get` | `records.batchGet` | WRAPPED_NOT_TESTED |
| 20 | app.table.record | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | `records.delete` | WRAPPED_NOT_TESTED |
| 21 | app.table.record | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | `records.get` | WRAPPED_NOT_TESTED |
| 22 | app.table.record | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records` | `records.list` | WRAPPED_NOT_TESTED |
| 23 | app.role.member | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/batch_delete` | `roles.batchDeleteMembers` | WRAPPED_NOT_TESTED |
| 24 | app.role.member | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/batch_create` | `roles.batchCreateMembers` | WRAPPED_NOT_TESTED |
| 25 | app.role.member | create | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members` | `roles.createMember` | WRAPPED_NOT_TESTED |
| 26 | app.role.member | list | GET | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members` | `roles.listMembers` | WRAPPED_NOT_TESTED |
| 27 | app.role.member | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/:member_id` | `roles.deleteMember` | WRAPPED_NOT_TESTED |
| 28 | app.role | create | POST | `/open-apis/bitable/v1/apps/:app_token/roles` | `roles.create` | WRAPPED_NOT_TESTED |
| 29 | app.role | update | PUT | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id` | `roles.update` | WRAPPED_NOT_TESTED |
| 30 | app.role | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id` | `roles.delete` | WRAPPED_NOT_TESTED |
| 31 | app.role | list | GET | `/open-apis/bitable/v1/apps/:app_token/roles` | `roles.list` | WRAPPED_NOT_TESTED |
| 32 | app.table.view | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views` | `views.create` | WRAPPED_NOT_TESTED |
| 33 | app.table.view | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | `views.update` | WRAPPED_NOT_TESTED |
| 34 | app.table.view | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | `views.delete` | WRAPPED_NOT_TESTED |
| 35 | app.table.view | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | `views.get` | WRAPPED_NOT_TESTED |
| 36 | app.table.view | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views` | `views.list` | WRAPPED_NOT_TESTED |
| 37 | app.table.form | upgrade | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/upgrade` | `forms.upgrade` | WRAPPED_NOT_TESTED |
| 38 | app.table.form | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id` | `forms.get` | WRAPPED_NOT_TESTED |
| 39 | app.table.form | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id` | `forms.update` | WRAPPED_NOT_TESTED |
| 40 | app.table.field_group | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/field_groups` | `fieldGroups.create` | WRAPPED_NOT_TESTED |
| 41 | app.table.form.field | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/fields/:field_id` | `forms.updateField` | WRAPPED_NOT_TESTED |
| 42 | app.table.form.field | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/fields` | `forms.listFields` | WRAPPED_NOT_TESTED |
| 43 | app.workflow | update | PUT | `/open-apis/bitable/v1/apps/:app_token/workflows/:workflow_id` | `workflows.update` | WRAPPED_NOT_TESTED |
| 44 | app.workflow | list | GET | `/open-apis/bitable/v1/apps/:app_token/workflows` | `workflows.list` | WRAPPED_NOT_TESTED |
| 45 | app.table.field | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields/:field_id` | `fields.delete` | WRAPPED_NOT_TESTED |
| 46 | app.table.field | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields` | `fields.list` | WRAPPED_NOT_TESTED |
| 47 | app.table.field | update | PUT | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields/:field_id` | `fields.update` | WRAPPED_NOT_TESTED |
| 48 | app.table.field | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields` | `fields.create` | WRAPPED_NOT_TESTED |
| 49 | app.block_workflow | list | GET | `/open-apis/bitable/v1/apps/:app_token/block_workflows` | `blockWorkflows.list` | WRAPPED_NOT_TESTED |

## Full-coverage boundary

The 49-operation list above is the inventory generated from the official SDK's Bitable project source, not yet an independent proof that every currently documented public endpoint is represented. Before phase one is declared complete:

1. Compare this list with the current official Bitable API reference and record any documented endpoint absent from the SDK-generated definitions.
2. Add a typed raw-request wrapper only for documented public endpoints missing from the SDK.
3. Review related Drive APIs separately when they are required for Bitable file subscription, attachment, import/export, or other Base-adjacent capabilities; do not silently mislabel a Drive API as a Bitable endpoint.
4. Add per-endpoint tests for payload mapping, pagination and error handling.
5. Verify live calls only against an explicitly designated test Base and only with the necessary scopes.

## Remaining engineering tasks

- Replace the permissive request payload interface with per-operation typed payloads while keeping SDK internal request options private.
- Add pagination helpers that preserve continuation tokens and stop safely.
- Build a complete endpoint registry with exact official docs, HTTP method/path, scopes, supported token types, limits, and destructive/idempotency notes. The current table records method/path but does not yet enumerate all permission and rate-limit metadata.
- Add an integration-test harness that is opt-in and cannot mutate production Base data accidentally.
- Update each endpoint's status only when its test criteria are met.

## Completion rules

- A resource-level generic pass-through is not a substitute for named methods.
- Do not silently drop unknown request or response fields.
- Do not auto-retry non-idempotent writes unless retry behavior is explicitly safe.
- Errors must preserve the platform code/message and operation context without logging secrets.
- Live integration tests must use an explicitly designated test Base. Do not mutate a production Base to test write operations.
- Mark endpoints unavailable in the SDK separately from endpoints unavailable in the public API.

## Official references

- [Lark Open Platform](https://open.larksuite.com/)
- [Official Lark Node.js SDK](https://github.com/larksuite/node-sdk)
- [Official SDK package](https://www.npmjs.com/package/@larksuiteoapi/node-sdk)
- [Bitable API reference](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview)
