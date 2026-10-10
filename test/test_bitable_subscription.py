"""One-shot test for subscribing a Bitable to file-level change events.

This test makes a real Feishu API request using the app's tenant_access_token.
The endpoint accepts file_token in the path and file_type as a query parameter;
event types are configured in the Open Platform event settings, not this body.
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

    # Official endpoint: POST /open-apis/drive/v1/files/{file_token}/subscribe
    # Required query parameter: file_type=bitable
    request = (
        lark.BaseRequest.builder()
        .http_method(lark.HttpMethod.POST)
        .uri(f"/open-apis/drive/v1/files/{FILE_TOKEN}/subscribe?file_type={FILE_TYPE}")
        .token_types({lark.AccessTokenType.TENANT})
        .build()
    )

    try:
        response = client.request(request)
    except Exception as exc:
        print(f"失败：调用飞书 API 时发生异常：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    raw_content = getattr(getattr(response, "raw", None), "content", b"")
    try:
        body = json.loads(
            raw_content.decode("utf-8")
            if isinstance(raw_content, bytes)
            else raw_content
        )
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
        "event_types_configured_in_open_platform": EVENT_TYPES,
        "response": body,
    }, ensure_ascii=False, indent=2))

    if response.success() and code == 0:
        print("成功：飞书已接受该多维表格的文件级事件订阅请求。")
        return 0

    if code in (1069603, 1069604):
        print(
            "提示：接口已返回业务错误。请核对文件访问权限；"
            "应用身份通常只能订阅由应用拥有或管理的文档。"
            "如果文档由当前用户拥有，需要评估使用该用户授权的 user_access_token。",
            file=sys.stderr,
        )
    else:
        print(
            "失败：请根据 api_code、api_message 和 log_id 继续排查。",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
