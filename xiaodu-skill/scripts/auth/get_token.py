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
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../common/config.env")
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
        json.dump(creds, f)
    os.chmod(CREDS_FILE, 0o600)


def is_token_valid(creds):
    if not creds:
        return False
    expires_at = creds.get("expires_at", 0)
    return time.time() < expires_at - 300


def refresh_access_token(worker_url, refresh_token):
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             f"{worker_url}/api/refresh",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"refresh_token": refresh_token})],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "access_token" in data:
                new_creds = {
                    "access_token": data["access_token"],
                    "refresh_token": data.get("refresh_token", refresh_token),
                    "expires_at": int(time.time()) + data.get("expires_in", 2592000),
                }
                save_credentials(new_creds)
                return new_creds
    except Exception:
        pass
    return None


def get_token():
    creds = load_credentials()
    
    if is_token_valid(creds):
        return creds
    
    config = load_config()
    worker_url = config.get("XIAODU_WORKER_URL", "")
    refresh_token = creds.get("refresh_token") if creds else None
    
    if not worker_url:
        return {"error": "未配置 XIAODU_WORKER_URL"}
    
    if refresh_token:
        new_creds = refresh_access_token(worker_url, refresh_token)
        if new_creds:
            return new_creds
    
    return {"error": "Token 无效且无法刷新，请重新授权"}
