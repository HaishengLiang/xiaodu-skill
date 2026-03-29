#!/usr/bin/env python3
"""OAuth 授权流程 - 客户端本地保存 Token"""

import json
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.expanduser("~/.xiaodu/credentials.json")

sys.path.insert(0, os.path.join(SCRIPT_DIR, "../common"))
from config import load_config


def get_worker_url(config):
    return config.get("XIAODU_WORKER_URL", "")


def save_credentials(access_token, refresh_token, expires_in):
    """保存凭证到本地"""
    creds = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": int(time.time()) + expires_in,
    }
    os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    print(f"凭证已保存到: {CREDS_FILE}")


def get_auth_url(worker_url):
    try:
        result = subprocess.run(
            ["curl", "-s",
             f"{worker_url}/auth-url"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"获取授权链接失败: {result.stderr}")
            return ""
        data = json.loads(result.stdout)
        return data.get("auth_url", "")
    except Exception as e:
        print(f"获取授权链接失败: {e}")
        return ""


def exchange_code(worker_url, code):
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             f"{worker_url}/exchange",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"code": code})],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        return json.loads(result.stdout)
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    config = load_config()
    worker_url = get_worker_url(config)

    if not worker_url:
        print("错误: 未设置 XIAODU_WORKER_URL")
        print(f"请在 {CONFIG_FILE} 中配置")
        sys.exit(1)

    print("=== 小度 OAuth 授权 ===\n")

    auth_url = get_auth_url(worker_url)
    if not auth_url:
        sys.exit(1)

    print("请访问以下链接完成授权:\n")
    print(auth_url)
    print("\n授权成功后，页面会显示授权码\n")

    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(f"=== 换取 Token ===")
        print(f"授权码: {code}\n")

        result = exchange_code(worker_url, code)
        if result.get("success"):
            access_token = result.get("access_token", "")
            refresh_token = result.get("refresh_token", "")
            expires_in = result.get("expires_in", 0)

            if access_token and refresh_token:
                save_credentials(access_token, refresh_token, expires_in)
                print("✅ 授权成功!")
                print(f"\nAccess Token: {access_token[:30]}...")
                print(f"有效期: {expires_in}秒 (约{expires_in // 86400}天)")
                print("\n现在可以运行其他命令了:")
                print("  python3 xiaodu.py list")
            else:
                print("❌ 授权失败: 返回数据不完整")
                print(result)
                sys.exit(1)
        else:
            print(f"❌ 授权失败: {result.get('error_description', result.get('error', '未知错误'))}")
            sys.exit(1)
    else:
        print("获得授权码后，运行:")
        print(f"  python3 {os.path.join(SCRIPT_DIR, 'init_auth.py')} <授权码>")


if __name__ == "__main__":
    main()
