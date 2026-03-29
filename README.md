# xiaodu-skill

小度智能设备控制技能。通过 OAuth 2.0 授权连接百度小度智能设备，支持设备列表查询、语音控制、文字播报、拍照等功能。

详细说明请查看 [SKILL.md](xiaodu-skill/SKILL.md)。

## 支持范围

### ✅ 支持
- 小度智能终端（有屏幕音箱、无屏音箱等）
- `list_user_devices` - 获取设备列表
- `control_xiaodu` - 开放式控制（发送语音指令）
- `xiaodu_speak` - 文字播报（朗读文本）
- `xiaodu_take_photo` - 触发设备拍照

### ❌ 不支持
- IoT 智能家居设备（灯光、空调等）

## 架构设计

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Worker API  │────▶│  百度 OAuth │
│ (Python CLI)│     │  (Vercel)    │     │   服务      │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                        │
       │              ┌──────────────┐           │
       └─────────────▶│  设备控制     │◀──────────┘
                      │  (DuerOS MCP)│
                      └──────────────┘
```

- **Worker API**: 提供 `/api/auth-url`、`/api/exchange`、`/api/refresh` 端点
- **Token 存储**: 本地 `~/.xiaodu/credentials.json`，客户端自动刷新
- **客户端**: Python CLI，通过 subprocess 调用 curl 与 Worker 交互

## Auth 服务

Auth 服务已内置（部署于 Vercel），开箱即用，**无需自行部署**。

如需自建，可参考 `vercel/` 目录代码自行部署。

### Vercel 部署（如需自建）

```bash
cd vercel && vercel deploy
```

**环境变量**: `XIAODU_APP_KEY`, `XIAODU_SECRET_KEY`

**本地配置**: 修改 `xiaodu-skill/scripts/common/config.env` 中的 `XIAODU_WORKER_URL` 为你的部署地址。

## 鸣谢

- 本项目在[LINUX DO](https://linux.do/) 社区 进行分享与交流，感谢社区的支持与反馈
