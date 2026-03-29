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
            ["curl", "-s", f"{worker_url}/api/auth-url"],
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
             f"{worker_url}/api/exchange",
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
    print("=== 小度 OAuth 授权 ===\n")
    
    config = load_config()
    worker_url = get_worker_url(config)
    
    if not worker_url:
        print("错误: 未配置 XIAODU_WORKER_URL")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        auth_url = get_auth_url(worker_url)
        if auth_url:
            print(f"请访问以下链接完成授权:\n")
            print(auth_url)
            print(f"\n授权成功后，页面会显示授权码")
            print(f"\n获得授权码后，运行:")
            print(f"  python3 {sys.argv[0]} <授权码>")
        return
    
    code = sys.argv[1]
    print(f"=== 换取 Token ===")
    print(f"授权码: {code}\n")
    
    result = exchange_code(worker_url, code)
    if result.get("success"):
        save_credentials(
            result["access_token"],
            result["refresh_token"],
            result["expires_in"]
        )
        print(f"✅ 授权成功!")
        print(f"\nAccess Token: {result['access_token'][:20]}...")
        print(f"有效期: {result['expires_in']}秒 (约{result['expires_in']//86400}天)")
    else:
        print(f"❌ 授权失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()
