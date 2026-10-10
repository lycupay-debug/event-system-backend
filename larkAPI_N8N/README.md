# n8n-nodes-lark-bitable

Initial custom n8n community-node package for Feishu/Lark Bitable. The node calls the sibling `larkAPI/` typed method library; it does not implement HTTP calls or duplicate authentication logic itself.

## Included in this first iteration

- A Feishu/Lark credential containing App ID, App Secret, and platform selection.
- One resource-style node with the Bitable resources currently exposed by `larkAPI/`: Base, Table, Record, Field, View, Form, Field Group, Dashboard, Custom Role, Workflow, and Block Workflow.
- Operation selectors for the 49 Bitable SDK wrapper operations.
- A JSON Payload field passed to the selected typed wrapper without reshaping it.
- Normal output handling, item pairing, and n8n's Continue On Fail behavior.
- No live API calls during unit tests.

## Payload format

The Payload is the complete request object expected by the selected official SDK method. It is deliberately passed through unchanged so endpoint-specific `path`, `query`, and `data` shapes remain under the SDK contract rather than being guessed by the node.

Example for listing records (verify any optional fields against the selected API's official reference):

```json
{
  "path": {
    "app_token": "YOUR_BASE_TOKEN",
    "table_id": "YOUR_TABLE_ID"
  },
  "query": {
    "page_size": 100
  }
}
```

In n8n, the Payload field can use an expression to build the object from upstream data. Do not place App Secret or tenant access tokens in this payload; credentials are managed by n8n.

## Development

This repository layout keeps the API and node packages separate:

- `../larkAPI/`: reusable typed API methods and normalized errors.
- `larkAPI_N8N/`: n8n node UI, credential definition, and execution adapter.

Run:

```bash
npm install --ignore-scripts --no-audit --no-fund
npm run typecheck
npm run build
npm test
```

The package currently references `../larkAPI` as a local dependency for in-repository development. A publishable distribution workflow and installation into the live n8n instance are intentionally not part of this phase. Do not restart or modify the running n8n container while developing.
