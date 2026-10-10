# feishu-bridge

Python service for receiving Feishu/Lark events over the official SDK WebSocket long connection. The official `lark-cli` is installed in the same container for auxiliary API operations; it is not the event listener.

## Current scope

- Register `p2.drive.file.bitable_record_changed_v1` with the official `lark-oapi` Python SDK.
- Log a minimal event summary without dumping the full payload.
- Run as an isolated Docker Compose service; it does not modify the existing n8n container.
- Keep credentials in an untracked `.env` file.

This is a starter implementation. A successful connection and real record-change delivery must be verified against the configured Feishu app before treating the integration as operational.

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

## Event payload

The handler logs the event name, file token, table ID, revision, action count and update time. It deliberately does not print the full event payload. The event is not yet forwarded to n8n or a business-processing queue.

## Repository policy

- Formal runtime code: `app/`
- Test code: `test/`
- No credentials or runtime data in Git.
- Do not modify the existing n8n container as part of this project.
