#!/usr/bin/env python3
"""小度设备控制 CLI"""

import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "devices.json")

sys.path.insert(0, os.path.join(SCRIPT_DIR, "../common"))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "../auth"))
from common.config import load_config
from auth.get_token import get_token


def mcp_call(tool_name, arguments):
    config = load_config()
    worker_url = config.get("XIAODU_WORKER_URL", "")

    token_result = get_token(worker_url)
    if token_result.get("error"):
        return None, token_result["error"]

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
            return None, result.stderr

        response = result.stdout
        for line in response.strip().split("\n"):
            if line.startswith("data:"):
                data = json.loads(line[5:])
                if "result" in data:
                    return data["result"], None
        return None, "无法解析响应"
    except Exception as e:
        return None, str(e)


def fetch_devices():
    result, err = mcp_call("list_user_devices", {})
    if err:
        return None, err

    content = result.get("content", []) if result else []
    if content and isinstance(content, list):
        devices = json.loads(content[0].get("text", "[]"))
        if isinstance(devices, dict):
            devices = [devices]
        return devices, None
    return None, "无法解析设备列表"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except:
            pass
    return None


def save_cache(devices):
    with open(CACHE_FILE, "w") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)


def select_device(devices):
    if not devices:
        return None, None

    if len(devices) == 1:
        d = devices[0]
        return d.get("cuid", ""), d.get("client_id", "")

    print("\n=== 设备列表 ===")
    for i, d in enumerate(devices):
        name = d.get("device_name", "未知")
        cuid = d.get("cuid", "")
        online = "在线" if d.get("online_status") else "离线"
        print(f"  [{i+1}] {name} | cuid: {cuid} | {online}")
    print()

    selection = input("选择设备 [1-{}]: ".format(len(devices))).strip()

    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(devices):
            d = devices[idx]
            return d.get("cuid", ""), d.get("client_id", "")
    else:
        for d in devices:
            if d.get("cuid") == selection:
                return d.get("cuid", ""), d.get("client_id", "")

    return None, None


def cmd_list(refresh=False):
    if not refresh:
        devices = load_cache()
        if devices:
            display_devices(devices)
            return

    print("获取设备列表...")
    devices, err = fetch_devices()
    if err:
        print(f"错误: {err}")
        sys.exit(1)

    save_cache(devices)
    display_devices(devices)


def display_devices(devices):
    for d in devices:
        print()
        print("=== 设备信息 ===")
        print(f"设备名称: {d.get('device_name', '未知')}")
        print(f"设备ID (cuid): {d.get('cuid', '未知')}")
        print(f"在线状态: {'在线' if d.get('online_status') else '离线'}")
        print(f"设备ClientID: {d.get('client_id', '')}")
        loc = d.get("location", {})
        if loc:
            print(f"位置: {loc.get('house', '')} > {loc.get('room', '')}")
        print()
        print("控制设备命令示例:")
        print('  python3 xiaodu.py control "播放音乐"')
        print('  python3 xiaodu.py speak "你好"')
        print("  python3 xiaodu.py photo")


def cmd_control(command, cuid=None, client_id=None):
    devices = load_cache()
    if not devices:
        devices, err = fetch_devices()
        if err:
            print(f"错误: {err}")
            sys.exit(1)

    if not cuid:
        cuid, client_id = select_device(devices)
        if not cuid:
            print("错误: 无法确定设备")
            sys.exit(1)

    if not client_id:
        for d in devices:
            if d.get("cuid") == cuid:
                client_id = d.get("client_id", "")
                break
        if not client_id:
            print(f"错误: 无法找到设备 {cuid} 的 client_id")
            sys.exit(1)

    print(f"=== 控制小度 ===")
    print(f"设备: {cuid}")
    print(f"指令: {command}")
    print()

    result, err = mcp_call("control_xiaodu", {
        "command": command,
        "cuid": cuid,
        "client_id": client_id,
    })

    if err:
        print(f"错误: {err}")
    elif result:
        content = result.get("content", [])
        if content:
            print(content[0].get("text", ""))


def cmd_speak(text, cuid=None, client_id=None):
    devices = load_cache()
    if not devices:
        devices, err = fetch_devices()
        if err:
            print(f"错误: {err}")
            sys.exit(1)

    if not cuid:
        cuid, client_id = select_device(devices)
        if not cuid:
            print("错误: 无法确定设备")
            sys.exit(1)

    if not client_id:
        for d in devices:
            if d.get("cuid") == cuid:
                client_id = d.get("client_id", "")
                break
        if not client_id:
            print(f"错误: 无法找到设备 {cuid} 的 client_id")
            sys.exit(1)

    print(f"=== 让小度播报 ===")
    print(f"设备: {cuid}")
    print(f"文本: {text}")
    print()

    result, err = mcp_call("xiaodu_speak", {
        "text": text,
        "cuid": cuid,
        "client_id": client_id,
    })

    if err:
        print(f"错误: {err}")
    elif result:
        content = result.get("content", [])
        if content:
            print(content[0].get("text", ""))


def cmd_photo(cuid=None, client_id=None):
    devices = load_cache()
    if not devices:
        devices, err = fetch_devices()
        if err:
            print(f"错误: {err}")
            sys.exit(1)

    if not cuid:
        cuid, client_id = select_device(devices)
        if not cuid:
            print("错误: 无法确定设备")
            sys.exit(1)

    if not client_id:
        for d in devices:
            if d.get("cuid") == cuid:
                client_id = d.get("client_id", "")
                break
        if not client_id:
            print(f"错误: 无法找到设备 {cuid} 的 client_id")
            sys.exit(1)

    print(f"=== 小度拍照 ===")
    print(f"设备: {cuid}")
    print()

    result, err = mcp_call("xiaodu_take_photo", {
        "cuid": cuid,
        "client_id": client_id,
    })

    if err:
        print(f"错误: {err}")
    elif result:
        content = result.get("content", [])
        if content:
            print(content[0].get("text", ""))


def usage():
    print("""小度设备控制 CLI

用法:
    python3 xiaodu.py list              # 列出所有设备
    python3 xiaodu.py list --refresh    # 刷新并列出设备
    python3 xiaodu.py control <指令>     # 控制设备
    python3 xiaodu.py speak <文本>       # 让小度播报
    python3 xiaodu.py photo              # 触发拍照

示例:
    python3 xiaodu.py list
    python3 xiaodu.py list --refresh
    python3 xiaodu.py control "播放音乐"
    python3 xiaodu.py speak "你好，今天天气不错"
    python3 xiaodu.py photo
""")


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        refresh = "--refresh" in sys.argv or "-r" in sys.argv
        cmd_list(refresh)
    elif cmd == "control":
        if len(sys.argv) < 3:
            print("错误: 请提供指令")
            usage()
            sys.exit(1)
        command = sys.argv[2]
        cuid = sys.argv[3] if len(sys.argv) > 3 else None
        client_id = sys.argv[4] if len(sys.argv) > 4 else None
        cmd_control(command, cuid, client_id)
    elif cmd == "speak":
        if len(sys.argv) < 3:
            print("错误: 请提供播报文本")
            usage()
            sys.exit(1)
        text = sys.argv[2]
        cuid = sys.argv[3] if len(sys.argv) > 3 else None
        client_id = sys.argv[4] if len(sys.argv) > 4 else None
        cmd_speak(text, cuid, client_id)
    elif cmd == "photo":
        cuid = sys.argv[2] if len(sys.argv) > 2 else None
        client_id = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_photo(cuid, client_id)
    else:
        print(f"未知命令: {cmd}")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
