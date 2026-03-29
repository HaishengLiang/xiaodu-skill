# xiaodu-skill

小度智能设备控制技能。通过 OAuth 2.0 授权连接百度小度智能设备，支持设备列表查询、语音控制、文字播报、拍照等功能。

详细说明请查看 [SKILL.md](xiaodu-skill/SKILL.md)。

## 限制

- 设备需支持 DuerOS API
- 每个设备有独立的 `client_id`，控制时必须使用设备返回的 `client_id`
- Token 需定期刷新，失败时需重新授权

## 架构设计

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Worker API  │────▶│  百度 OAuth │
│ (Python CLI)│     │(Vercel/CF)   │     │   服务      │
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

## 部署 Auth 服务

### Vercel
```bash
cd vercel && vercel deploy
```

### Cloudflare Workers
```bash
cd worker && npx wrangler deploy
```

**环境变量**: `XIAODU_APP_KEY`, `XIAODU_SECRET_KEY`

**本地配置**: 修改 `xiaodu-skill/scripts/common/config.env` 中的 `XIAODU_WORKER_URL` 为你的部署地址。
