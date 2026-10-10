# Lark Bitable API Method Library

This directory contains the first-stage, reusable TypeScript API method library for Feishu/Lark Bitable. It is kept separate from the existing Python WebSocket event listener.

## Goals

- Wrap the Bitable Open APIs as named, reusable methods.
- Use the official Lark Node.js SDK as the transport and typed API source where the SDK exposes an endpoint.
- Keep authentication, request execution, error normalization, pagination helpers, and resource methods separated.
- Maintain a coverage ledger against the official API reference. An endpoint is not "complete" merely because a generic SDK client exists.
- Make the method library usable by the later `larkAPI_N8N` node library without importing the running bridge application.

## Boundaries

- Existing Python event listener remains in `app/`.
- Existing Python tests remain in `test/`.
- This library is isolated under `larkAPI/`.
- The n8n node package will be a separate root-level directory, `larkAPI_N8N/`, in phase two.
- Never put credentials, tokens, real event payloads, or `.env` files in Git.
- Do not modify or restart the existing n8n container as part of library development.

## Planned structure

```text
larkAPI/
├── src/
│   ├── client.ts
│   ├── errors.ts
│   ├── pagination.ts
│   ├── index.ts
│   └── resources/
│       ├── app.ts
│       ├── table.ts
│       ├── field.ts
│       ├── record.ts
│       ├── view.ts
│       ├── form.ts
│       ├── dashboard.ts
│       ├── automation.ts
│       └── permission.ts
├── test/
├── API_COVERAGE.md
├── package.json
└── tsconfig.json
```

The resource files above are a proposed organization, not a claim that each API group or endpoint has already been implemented. The coverage ledger is authoritative.

## Development

The package is TypeScript-first and uses `@larksuiteoapi/node-sdk`. Keep runtime dependencies explicit and pinned by the lockfile once the package is installed in a development environment.

Expected quality gates:

1. Type-check the package.
2. Unit-test parameter mapping, pagination, and normalized errors without network access.
3. Compare the endpoint inventory with the official Bitable API reference and the SDK's generated API definitions.
4. Run authenticated integration tests only when explicitly configured with valid app credentials and a test Base.
5. Mark each API as implemented and tested separately; never infer successful live operation from compilation alone.

## Official references

- [Lark Open Platform](https://open.larksuite.com/)
- [Official Lark Node.js SDK](https://github.com/larksuite/node-sdk)
- [Official SDK package](https://www.npmjs.com/package/@larksuiteoapi/node-sdk)
- [Bitable API reference](https://open.larksuite.com/document/server-docs/docs/bitable-v1/bitable-overview)

## Current status

Initial SDK-backed named wrappers and the shared client/error layer are in place. Type-check and declaration build have passed in a disposable Node container. Unit-test coverage and the endpoint-by-endpoint comparison against the full current official API reference remain in progress. See [API_COVERAGE.md](./API_COVERAGE.md).
