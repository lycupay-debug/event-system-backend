"""One-shot test for subscribing a Bitable to file-level change events.

Run inside the feishu-bridge container or another environment with LARK_APP_ID
and LARK_APP_SECRET set. This script makes a real Feishu API call.
"""
from __future__ import annotations

import json
import os
import sys

import lark_oapi as lark

FILE_TOKEN = "XiPEbrTdxaYdWqsS1h5cUQC3nBb"
FILE_TYPE = "bitable"
EVENT_TYPES = ["drive.file.bitable_record_changed_v1"]


def main() -> int:
    app_id = os.getenv("LARK_APP_ID", "").strip()
    app_secret = os.getenv("LARK_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        print("失败：缺少 LARK_APP_ID 或 LARK_APP_SECRET 环境变量。", file=sys.stderr)
        return 2

    client = (
        lark.Client.builder()
        .app_id(app_id)
        .app_secret(app_secret)
        .log_level(lark.LogLevel.INFO)
        .build()
    )

    payload = {
        "file_token": FILE_TOKEN,
        "file_type": FILE_TYPE,
        "event_types": EVENT_TYPES,
    }
    request = (
        lark.BaseRequest.builder()
        .http_method(lark.HttpMethod.POST)
        .uri("/open-apis/drive/v1/files/subscribe")
        .token_types({lark.AccessTokenType.TENANT})
        .body(payload)
        .build()
    )

    try:
        response = client.request(request)
    except Exception as exc:
        print(f"失败：调用飞书 API 时发生异常：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    raw_content = getattr(getattr(response, "raw", None), "content", b"")
    try:
        body = json.loads(raw_content.decode("utf-8") if isinstance(raw_content, bytes) else raw_content)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
        body = {"raw_response": str(raw_content)[:2000]}

    code = body.get("code")
    msg = body.get("msg", "")
    log_id = response.get_log_id() if hasattr(response, "get_log_id") else None

    print(json.dumps({
        "http_success": response.success(),
        "api_code": code,
        "api_message": msg,
        "log_id": log_id,
        "file_token": FILE_TOKEN,
        "file_type": FILE_TYPE,
        "event_types": EVENT_TYPES,
        "response": body,
    }, ensure_ascii=False, indent=2))

    if response.success() and code == 0:
        print("成功：文件级事件订阅请求已被飞书接受。")
        return 0

    print("失败：请根据 api_code、api_message 和 log_id 检查权限、文档访问范围及接口参数。", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
