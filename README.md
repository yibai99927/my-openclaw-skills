# 🐼 my-openclaw-skills

OpenClaw 自定义技能仓库（已做个人敏感信息清理）。

## 📦 Skills 列表

- `a-stock-analysis`：A股综合分析（盘前/盘后）
- `codex-deep-search`：Codex 深度检索 + 可选通知 + JSON sidecar
- `task-status`：长任务开始/完成/失败状态回报
- `scholar-push`：Google Scholar/Gmail 文献推送与粗读
- `model-switch`：模型切换工具
- `minimax-vl`：MiniMax VL 相关能力

## 🔒 脱敏说明

本次已移除/替换以下内容：

- 固定 Telegram chat id（改为占位符或运行时参数）
- 本地状态缓存（如 `task-status/scripts/.task-status`）
- 硬编码个人路径（改为相对命令或环境变量）

## 🧩 使用建议

每个 skill 目录内均含 `SKILL.md`，按其中示例执行即可。

## 📁 目录结构

```text
my-openclaw-skills/
├── a-stock-analysis/
├── codex-deep-search/
├── scholar-push/
├── task-status/
├── model-switch/
├── minimax-vl/
├── templates/
└── A股观察清单模板.md
```
