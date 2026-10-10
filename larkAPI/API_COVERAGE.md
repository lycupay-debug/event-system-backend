# Bitable API Coverage Ledger

This ledger tracks the first-stage `larkAPI` wrapper surface against the official Lark Node.js SDK generated Bitable API definitions.

## Status meanings

- `WRAPPED_NOT_TESTED`: named wrapper exists, but local wrapper tests have not passed.
- `WRAPPER_TESTED`: offline tests confirm the named wrapper forwards payloads and normalizes errors; this is not a remote endpoint contract test.
- `CONTRACT_TESTED`: compile-time request path/query/body types and specific contract assertions are checked locally.
- `INTEGRATION_VERIFIED`: successful live request tested against an explicitly permitted test Base.
- `GAP`: documented public endpoint is not yet wrapped.
- `BLOCKED`: cannot be implemented or verified; reason documented.

## SDK-generated endpoint inventory

The pinned SDK generated Bitable client exposes 49 unique operation/version combinations in its `bitable` client surface, and all 49 are exposed as named methods. Offline tests verify payload forwarding for all 49 and SDK error normalization. Compile-time contracts cover representative Base, table, record-list, record-create, query, and attachment-upload payloads. Six supporting Drive media methods are separately exposed for Bitable attachment upload/download; they are not counted as Bitable endpoints. All validation runs against a disposable clone. No live API calls are made in this phase.

| # | API resource | Operation | HTTP | Path | Official API Explorer | Wrapper | Status |
|---:|---|---|---|---|---|---|
| 1 | app.table | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=patch&project=bitable&resource=app.table&version=v1>) | `tables.update` | WRAPPER_TESTED |
| 2 | app.table | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/tables/batch_delete` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_delete&project=bitable&resource=app.table&version=v1>) | `tables.batchDelete` | WRAPPER_TESTED |
| 3 | app.table | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/batch_create` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_create&project=bitable&resource=app.table&version=v1>) | `tables.batchCreate` | WRAPPER_TESTED |
| 4 | app.table | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.table&version=v1>) | `tables.create` | WRAPPER_TESTED |
| 5 | app.table | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.table&version=v1>) | `tables.delete` | WRAPPER_TESTED |
| 6 | app.table | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.table&version=v1>) | `tables.list` | CONTRACT_TESTED |
| 7 | app.dashboard | copy | POST | `/open-apis/bitable/v1/apps/:app_token/dashboards/:block_id/copy` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=copy&project=bitable&resource=app.dashboard&version=v1>) | `dashboards.copy` | WRAPPER_TESTED |
| 8 | app.dashboard | list | GET | `/open-apis/bitable/v1/apps/:app_token/dashboards` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.dashboard&version=v1>) | `dashboards.list` | WRAPPER_TESTED |
| 9 | app | update | PUT | `/open-apis/bitable/v1/apps/:app_token` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=update&project=bitable&resource=app&version=v1>) | `apps.update` | WRAPPER_TESTED |
| 10 | app | copy | POST | `/open-apis/bitable/v1/apps/:app_token/copy` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=copy&project=bitable&resource=app&version=v1>) | `apps.copy` | WRAPPER_TESTED |
| 11 | app | create | POST | `/open-apis/bitable/v1/apps` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app&version=v1>) | `apps.create` | WRAPPER_TESTED |
| 12 | app | get | GET | `/open-apis/bitable/v1/apps/:app_token` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=get&project=bitable&resource=app&version=v1>) | `apps.get` | CONTRACT_TESTED |
| 13 | app.table.record | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_delete` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_delete&project=bitable&resource=app.table.record&version=v1>) | `records.batchDelete` | WRAPPER_TESTED |
| 14 | app.table.record | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_create` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_create&project=bitable&resource=app.table.record&version=v1>) | `records.batchCreate` | WRAPPER_TESTED |
| 15 | app.table.record | batch_update | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_update` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_update&project=bitable&resource=app.table.record&version=v1>) | `records.batchUpdate` | WRAPPER_TESTED |
| 16 | app.table.record | update | PUT | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=update&project=bitable&resource=app.table.record&version=v1>) | `records.update` | WRAPPER_TESTED |
| 17 | app.table.record | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.table.record&version=v1>) | `records.create` | CONTRACT_TESTED |
| 18 | app.table.record | search | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/search` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=search&project=bitable&resource=app.table.record&version=v1>) | `records.search` | WRAPPER_TESTED |
| 19 | app.table.record | batch_get | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/batch_get` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_get&project=bitable&resource=app.table.record&version=v1>) | `records.batchGet` | WRAPPER_TESTED |
| 20 | app.table.record | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.table.record&version=v1>) | `records.delete` | WRAPPER_TESTED |
| 21 | app.table.record | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=get&project=bitable&resource=app.table.record&version=v1>) | `records.get` | WRAPPER_TESTED |
| 22 | app.table.record | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.table.record&version=v1>) | `records.list` | CONTRACT_TESTED |
| 23 | app.role.member | batch_delete | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/batch_delete` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_delete&project=bitable&resource=app.role.member&version=v1>) | `roles.batchDeleteMembers` | WRAPPER_TESTED |
| 24 | app.role.member | batch_create | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/batch_create` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=batch_create&project=bitable&resource=app.role.member&version=v1>) | `roles.batchCreateMembers` | WRAPPER_TESTED |
| 25 | app.role.member | create | POST | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.role.member&version=v1>) | `roles.createMember` | WRAPPER_TESTED |
| 26 | app.role.member | list | GET | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.role.member&version=v1>) | `roles.listMembers` | WRAPPER_TESTED |
| 27 | app.role.member | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id/members/:member_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.role.member&version=v1>) | `roles.deleteMember` | WRAPPER_TESTED |
| 28 | app.role | create | POST | `/open-apis/bitable/v1/apps/:app_token/roles` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.role&version=v1>) | `roles.create` | WRAPPER_TESTED |
| 29 | app.role | update | PUT | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=update&project=bitable&resource=app.role&version=v1>) | `roles.update` | WRAPPER_TESTED |
| 30 | app.role | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/roles/:role_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.role&version=v1>) | `roles.delete` | WRAPPER_TESTED |
| 31 | app.role | list | GET | `/open-apis/bitable/v1/apps/:app_token/roles` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.role&version=v1>) | `roles.list` | WRAPPER_TESTED |
| 32 | app.table.view | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.table.view&version=v1>) | `views.create` | WRAPPER_TESTED |
| 33 | app.table.view | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=patch&project=bitable&resource=app.table.view&version=v1>) | `views.update` | WRAPPER_TESTED |
| 34 | app.table.view | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.table.view&version=v1>) | `views.delete` | WRAPPER_TESTED |
| 35 | app.table.view | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views/:view_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=get&project=bitable&resource=app.table.view&version=v1>) | `views.get` | WRAPPER_TESTED |
| 36 | app.table.view | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/views` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.table.view&version=v1>) | `views.list` | WRAPPER_TESTED |
| 37 | app.table.form | upgrade | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/upgrade` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=upgrade&project=bitable&resource=app.table.form&version=v1>) | `forms.upgrade` | WRAPPER_TESTED |
| 38 | app.table.form | get | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=get&project=bitable&resource=app.table.form&version=v1>) | `forms.get` | WRAPPER_TESTED |
| 39 | app.table.form | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=patch&project=bitable&resource=app.table.form&version=v1>) | `forms.update` | WRAPPER_TESTED |
| 40 | app.table.field_group | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/field_groups` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.table.field_group&version=v1>) | `fieldGroups.create` | WRAPPER_TESTED |
| 41 | app.table.form.field | patch | PATCH | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/fields/:field_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=patch&project=bitable&resource=app.table.form.field&version=v1>) | `forms.updateField` | WRAPPER_TESTED |
| 42 | app.table.form.field | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/forms/:form_id/fields` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.table.form.field&version=v1>) | `forms.listFields` | WRAPPER_TESTED |
| 43 | app.workflow | update | PUT | `/open-apis/bitable/v1/apps/:app_token/workflows/:workflow_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=update&project=bitable&resource=app.workflow&version=v1>) | `workflows.update` | WRAPPER_TESTED |
| 44 | app.workflow | list | GET | `/open-apis/bitable/v1/apps/:app_token/workflows` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.workflow&version=v1>) | `workflows.list` | WRAPPER_TESTED |
| 45 | app.table.field | delete | DELETE | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields/:field_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=delete&project=bitable&resource=app.table.field&version=v1>) | `fields.delete` | WRAPPER_TESTED |
| 46 | app.table.field | list | GET | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.table.field&version=v1>) | `fields.list` | WRAPPER_TESTED |
| 47 | app.table.field | update | PUT | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields/:field_id` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=update&project=bitable&resource=app.table.field&version=v1>) | `fields.update` | WRAPPER_TESTED |
| 48 | app.table.field | create | POST | `/open-apis/bitable/v1/apps/:app_token/tables/:table_id/fields` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=create&project=bitable&resource=app.table.field&version=v1>) | `fields.create` | WRAPPER_TESTED |
| 49 | app.block_workflow | list | GET | `/open-apis/bitable/v1/apps/:app_token/block_workflows` | [Open](<https://open.feishu.cn/api-explorer?from=op_doc_tab&apiName=list&project=bitable&resource=app.block_workflow&version=v1>) | `blockWorkflows.list` | WRAPPER_TESTED |

## Public API reference reconciliation

This is a tracked reconciliation, not a claim that every currently published Bitable endpoint has already been exhaustively checked.

### Official public reference spot-checks

- [Create a record](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create): current public reference confirms `POST /open-apis/bitable/v1/apps/:app_token/tables/:table_id/records`, the record-create scope, query parameters such as `user_id_type` and `client_token`, and that attachment fields require a file token from the upload-material or multipart-upload APIs.
- [Delete a field](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-field/delete): confirms the public field-delete route and the Base read/write/manage scope.
- [Batch create role members](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-role-member/batch_create): confirms the custom-role member endpoint and advanced-permission prerequisites.
- [Bitable overview](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview) and the official platform's [Bitable capability summary](https://open.larksuite.com/document/mcp_open_tools/feishu-cli-let-ai-actually-do-your-work-in-feishu) identify tables, fields, records, views, forms, dashboards, automations, and permission roles as core capability areas.

### Scope decision

- The core Bitable inventory is the 49 SDK-generated methods in the table below.
- The official record API explicitly requires a separate Drive media upload flow for attachment fields. Therefore `createBitableAttachmentMethods()` additionally exposes `upload`, `prepareUpload`, `uploadPart`, `finishUpload`, `download`, and `batchGetTmpDownloadUrl`. These use the SDK's typed Drive media methods and are tracked separately from the Bitable count.
- The remaining reconciliation task is to walk the current official reference page-by-page and record any public endpoint not present in the pinned SDK. A search result or a 49-method SDK inventory alone is not enough to declare zero gaps.
- Real API integration testing is intentionally deferred until `larkAPI_N8N/` is complete, as requested.

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
