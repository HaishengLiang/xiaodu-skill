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

## 安装适配

本技能支持多种应用接入方式：

### Claude Code

将 `xiaodu-skill` 目录链接或复制到 Claude Code 的 skills 目录：

```bash
ln -s /path/to/skills/xiaodu-skill ~/.claude/skills/xiaodu-skill
```

Claude Code 从 `~/.claude/skills/` 加载技能，每个子目录需包含 `SKILL.md`。

在 `settings.json` 中注册：

```json
{
  "skills": {
    "xiaodu": "~/.claude/skills/xiaodu-skill"
  }
}
```

### OpenClaw

将 `xiaodu-skill` 目录链接或复制到 OpenClaw 的 skills 目录：

```bash
ln -s /path/to/skills/xiaodu-skill ~/.openclaw/skills/xiaodu-skill
```

或通过 CLI 安装：

```bash
npx clawhub install xiaodu-skill
```

OpenClaw 从 `~/.openclaw/skills/` 加载技能，每个子目录需包含 `SKILL.md`。

### Copaw

将 `xiaodu-skill` 目录复制到 Copaw 的自定义技能目录：

```bash
cp -r /path/to/skills/xiaodu-skill ~/.copaw/customized_skills/xiaodu-skill
```

Copaw 从 `~/.copaw/customized_skills/` 加载自定义技能，每个子目录需包含 `SKILL.md`。

也可通过控制台导入：控制台 → 智能体 → 技能 → 导入技能，粘贴 GitHub 仓库 URL。

### 其他应用

根据应用各自的 skill 注册机制，指向 `skills/xiaodu-skill` 目录。

## Auth 服务

Auth 服务已内置（部署于 Vercel），开箱即用，**无需自行部署**。

如需自建，可参考 `vercel/` 目录代码自行部署。

### Self Deploy

`vercel/` 目录用于自托管部署，不参与标准 skill 安装流程。

```bash
cd vercel && vercel deploy
```

**环境变量**: `XIAODU_APP_KEY`, `XIAODU_SECRET_KEY`

**本地配置**: 修改 `xiaodu-skill/scripts/common/config.env` 中的 `XIAODU_WORKER_URL` 为你的部署地址。

## 鸣谢

- 本项目在[LINUX DO](https://linux.do/) 社区 进行分享与交流，感谢社区的支持与反馈
