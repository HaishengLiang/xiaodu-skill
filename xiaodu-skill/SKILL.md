---
name: xiaodu-skill
description: 小度智能设备控制技能。当你需要控制小度智能音箱/设备、执行语音指令、让小度播报文字、获取设备列表、触发设备拍照等操作时，使用此技能。也适用于用户提到"小度"、"DuerOS"、"百度智能家居"、"控制小度设备"、"小度授权"等场景时触发。授权时请发送授权链接给用户，用户返回授权码后完成OAuth授权流程。
compatibility: curl, python3
---

# 小度智能设备控制技能

本技能用于连接百度小度智能设备，通过 OAuth 2.0 授权码模式获取 Access Token，然后通过 MCP 协议控制设备。

## OAuth 授权流程

### 步骤1：生成授权链接

```bash
python3 ~/.claude/skills/xiaodu-skill/scripts/auth/init_auth.py
```

### 步骤2：用授权码换取 Token

```bash
python3 ~/.claude/skills/xiaodu-skill/scripts/auth/init_auth.py <授权码>
```

Token 会自动保存到 `~/.xiaodu/credentials.json`，客户端自动管理刷新。

## CLI 用法

```bash
# 列出设备
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py list
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py list --refresh  # 刷新缓存

# 控制设备
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py control "播放音乐"
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py control "播放音乐" <cuid> [client_id]

# 让小度播报
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py speak "你好"
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py speak "你好" <cuid> [client_id]

# 拍照
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py photo
python3 ~/.claude/skills/xiaodu-skill/scripts/device/xiaodu.py photo <cuid> [client_id]
```

## 重要概念

- `app_id`（即 AppKey）：应用级别的 ClientID，用于 OAuth 认证
- `client_id`：设备返回的 client_id，用于 MCP 控制命令，**与 app_id 不同！**

每个设备有自己独立的 `client_id`。控制设备时必须使用设备列表返回的 `client_id`，而非 `app_id`。

## 多设备处理

当用户有多个设备时：
1. CLI 自动展示设备列表让用户选择
2. **必须记录每个设备的 cuid 和 client_id**
3. 用户指定设备后，后续所有控制命令必须传入该设备的 cuid 和 client_id

## Token 管理

Token 保存在 `~/.xiaodu/credentials.json`，客户端自动处理刷新。

## Worker API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/auth-url` | GET | 获取百度授权链接 |
| `/exchange` | POST | 用授权码换取 Token |

### Vercel 部署

```bash
cd vercel
vercel deploy
```

**环境变量配置（在 Vercel Dashboard 中设置）：**
- `XIAODU_APP_KEY`: 百度 OAuth AppKey
- `XIAODU_SECRET_KEY`: 百度 OAuth SecretKey

## 错误处理

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 110 | Access Token 无效或已过期 | 客户端自动刷新 |
| 120 | 设备不在线 | 确保设备开机且联网 |
| 130 | 刷新 Token 失败 | 重新发起授权流程 |
