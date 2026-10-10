# feishu-bridge

Python service for receiving Feishu/Lark events over the official SDK WebSocket long connection. The official `lark-cli` is installed in the same container for auxiliary API operations; it is not the event listener.

## Current scope

- Register `p2.drive.file.bitable_record_changed_v1` with the official `lark-oapi` Python SDK.
- Log the original event body and a structured summary of changed fields.
- Decode JSON-encoded `field_value` strings in `before_value` and `after_value`.
- Match before/after entries by `field_id` instead of relying on list order, and omit fields whose decoded values are unchanged.
- Preserve unknown or malformed field values as strings rather than dropping them.
- Run as an isolated Docker Compose service; it does not modify the existing n8n container.
- Keep credentials in an untracked `.env` file.

The event's `field_id` values are not human-readable field names. Mapping them to names requires table-field metadata; this listener does not make an extra API call for every event. The event is not yet forwarded to n8n or a business-processing queue.

## Prerequisites

- Docker Engine and Docker Compose on the Ubuntu host.
- A Feishu/Lark custom app with App ID and App Secret.
- In the Open Platform console, configure event subscription to use persistent connection (WebSocket) and subscribe to the Bitable record-change event `drive.file.bitable_record_changed_v1`.
- Grant the app the required Base/file scopes and ensure the target Base is accessible to the app.
- For per-file cloud-document subscription, follow the requirements of the Drive file subscription API for the target file. This is separate from establishing the application's WebSocket connection.

## Configure

Copy `.env.example` to `.env` and fill in credentials:

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Never commit `.env`, App Secrets, tokens, or real event payloads.

## Build and run

From this directory:

```bash
sudo docker compose build
sudo docker compose up -d
sudo docker compose logs -f feishu-bridge
```

Check the CLI is present:

```bash
sudo docker compose exec feishu-bridge lark-cli --help
```

The CLI may require its own configuration before authenticated commands can run. Do not run its interactive login wizard as part of the container build.

## Test

Run local unit tests. These tests do not connect to Feishu:

```bash
sudo docker compose run --rm --build --entrypoint python feishu-bridge -m unittest discover -s test -v
```

Run the one-shot file-level Bitable subscription test. This makes a real API request using the credentials in `.env`; it does not change the listener's runtime code:

```bash
sudo docker compose run --rm --build --entrypoint python feishu-bridge test/test_bitable_subscription.py
```

The test targets the Bitable whose file token is configured in `test/test_bitable_subscription.py`. A successful API response confirms the subscription request was accepted; then edit a non-formula field in that Bitable and inspect the listener logs:

```bash
sudo docker compose logs --since=5m feishu-bridge
```

## Event log structure

Each `bitable_record_changed` log JSON contains:

- `event`: the original event payload, preserved for troubleshooting.
- `structured`: event metadata and `actions`; each action contains `record_id`, action type, and `changes`.
- Each change contains `field_id`, decoded `before`, and decoded `after`. Empty `field_value` strings are represented as JSON `null`; unchanged decoded values are omitted from `changes`.

For example, a text field changing from empty to a text value appears in `structured.actions[].changes[]`, while fields whose before/after values are identical are not included.

## Repository policy

- Formal runtime code: `app/`
- Test code: `test/`
- No credentials or runtime data in Git.
- Do not modify the existing n8n container as part of this project.
