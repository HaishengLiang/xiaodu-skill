#!/usr/bin/env python3
"""通用 MCP 调用"""

import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(SCRIPT_DIR, "../common"))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "../auth"))
from common.config import load_config
from get_token import get_token


def mcp_call(tool_name, arguments):
    config = load_config()
    worker_url = config.get("XIAODU_WORKER_URL", "")
    if not worker_url:
        return {"error": "XIAODU_WORKER_URL not set"}

    token_result = get_token()
    if token_result.get("error"):
        return {"error": token_result["error"]}

    access_token = token_result.get("access_token", "")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "https://xiaodu.baidu.com/dueros_mcp_server/mcp/",
             "-H", f"ACCESS_TOKEN: {access_token}",
             "-H", "Content-Type: application/json",
             "-H", "Accept: application/json, text/event-stream",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr}

        response = result.stdout
        # SSE 格式，提取 data: 行
        for line in response.strip().split("\n"):
            if line.startswith("data:"):
                data = json.loads(line[5:])
                if "result" in data:
                    return data["result"]
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: mcp.py <工具名> [参数JSON]")
        print("可用工具: list_user_devices, control_xiaodu, xiaodu_speak, xiaodu_take_photo")
        sys.exit(1)

    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    result = mcp_call(tool_name, args)

    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)

    # 提取 content.text 并格式化输出
    content = result.get("content", [])
    if content and isinstance(content, list):
        text = content[0].get("text", "")
        try:
            parsed = json.loads(text)
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        except:
            print(text)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
