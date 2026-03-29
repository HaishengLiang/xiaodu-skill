#!/usr/bin/env python3
"""获取 Access Token - 客户端本地管理，自动刷新"""

import json
import os
import subprocess
import sys
import time
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_FILE = os.path.expanduser("~/.xiaodu/credentials.json")

sys.path.insert(0, os.path.join(SCRIPT_DIR, "../common"))
from config import load_config


def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()
    return config


def load_credentials():
    if os.path.exists(CREDS_FILE):
        try:
            with open(CREDS_FILE) as f:
                return json.load(f)
        except:
            pass
    return None


def save_credentials(creds):
    os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    # 设置文件权限为 600，保护密钥文件
    os.chmod(CREDS_FILE, 0o600)


def is_token_valid(creds):
    """检查 token 是否有效（提前 60 秒视为过期）"""
    if not creds or "expires_at" not in creds:
        return False
    return time.time() < (creds["expires_at"] - 60)


def refresh_access_token(refresh_token, client_id, client_secret):
    """刷新 Access Token"""
    try:
        params = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        })
        result = subprocess.run(
            ["curl", "-s", "-G", f"https://openapi.baidu.com/oauth/2.0/token?{params}"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None, result.stderr

        data = json.loads(result.stdout)
        if "error" in data:
            return None, data.get("error_description", data["error"])

        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_at": int(time.time()) + data.get("expires_in", 0),
        }, None
    except Exception as e:
        return None, str(e)


def get_token():
    """获取 Access Token - 返回字典格式"""
    config = load_config()
    client_id = config.get("XIAODU_APP_KEY", "")
    client_secret = config.get("XIAODU_SECRET_KEY", "")

    creds = load_credentials()

    # 如果 token 有效，直接返回
    if is_token_valid(creds):
        return {"access_token": creds["access_token"], "error": None}

    # Token 无效或不存在，需要刷新
    if not creds or "refresh_token" not in creds:
        return {"access_token": None, "error": "not_authorized"}

    print("Token 已过期，正在刷新...", file=sys.stderr)
    new_creds, err = refresh_access_token(creds["refresh_token"], client_id, client_secret)
    if err:
        return {"access_token": None, "error": err}

    # 保存新凭证
    save_credentials(new_creds)
    print("Token 刷新成功", file=sys.stderr)
    return {"access_token": new_creds["access_token"], "error": None}


def main():
    config = load_config()
    worker_url = config.get("XIAODU_WORKER_URL", "")

    if not worker_url:
        print("错误: 未设置 XIAODU_WORKER_URL", file=sys.stderr)
        print(f"请在 {CONFIG_FILE} 中配置", file=sys.stderr)
        sys.exit(1)

    result = get_token()

    if result["error"]:
        if result["error"] == "not_authorized":
            print("错误: 未授权，请先完成 OAuth 授权", file=sys.stderr)
            print(f"运行: python3 {os.path.join(SCRIPT_DIR, 'init_auth.py')}", file=sys.stderr)
        else:
            print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(result["access_token"])


if __name__ == "__main__":
    main()
