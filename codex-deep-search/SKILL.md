---
name: codex-deep-search
description: 使用 Codex CLI 进行深度网页搜索和研究。支持后台执行 + Telegram 回调。
allowed-tools:
  - Bash
  - Read
---

# Codex Deep Search - 深度搜索 skill

使用 OpenAI Codex CLI 进行深度搜索和研究。

## 功能

- 🔍 深度网页检索
- 📝 自动整理搜索结果
- 🔔 Telegram 回调通知

## 使用方法

### 基本搜索

```bash
bash ~/.openclaw/workspace/skills/codex-deep-search/scripts/search.sh \
  --prompt "你的搜索问题" \
  --task-name "my-research"
```

### 带 Telegram 通知

```bash
bash ~/.openclaw/workspace/skills/codex-deep-search/scripts/search.sh \
  --prompt "搜索关于存算一体芯片的最新研究" \
  --task-name "存算一体调研" \
  --telegram-group "YOUR_CHAT_ID" \
  --timeout 120
```

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--prompt` | ✅ | - | 搜索提示词 |
| `--task-name` | ❌ | search-YYYYMMDD-HHMMSS | 任务名称 |
| `--telegram-group` | ❌ | (未设置) | Telegram 聊天 ID |
| `--timeout` | ❌ | 120 | 超时时间（秒） |

## 示例

### 学术研究搜索

```bash
bash scripts/search.sh \
  --prompt "搜索最近一年关于 FeFET 存算一体的最新论文和研究进展" \
  --task-name "FeFET-研究" \
  --timeout 180
```

### 技术调研

```bash
bash scripts/search.sh \
  --prompt "调研 OpenClaw 的最佳部署实践和性能优化方法" \
  --task-name "OpenClaw-调研"
```

## 结果输出

- 搜索结果保存到: `/tmp/codex-search/<task-name>.txt`
- Telegram 通知: 仅在提供 `--telegram-group` 且设置 `TELEGRAM_BOT_TOKEN`（或本机 token 文件）时发送
