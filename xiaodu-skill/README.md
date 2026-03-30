# 小度技能

小度智能设备控制技能，支持 Claude Code、OpenClaw、Copaw 等 AI 编码工具。

## 安装适配

不同 AI 编码工具的技能安装目录：

| 工具 | 安装目录 |
|------|----------|
| Claude Code | `~/.claude/skills/xiaodu-skill/` |
| OpenClaw | `~/.openclaw/skills/xiaodu-skill/` |
| Copaw | `~/.copaw/skills/xiaodu-skill/` |

脚本路径对应调整，例如：
```bash
# Claude Code
python3 ~/.claude/skills/xiaodu-skill/scripts/auth/init_auth.py

# OpenClaw
python3 ~/.openclaw/skills/xiaodu-skill/scripts/auth/init_auth.py

# Copaw
python3 ~/.copaw/skills/xiaodu-skill/scripts/auth/init_auth.py
```
