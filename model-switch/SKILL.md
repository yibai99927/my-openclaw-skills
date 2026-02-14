# Model Switch Skill

管理 OpenClaw 模型切换的智能技能。

## 功能 (Features)

- 🚀 **查看当前模型配置** - 显示主模型 + fallback 链
- 🔄 **切换主模型** - 用模型名/编号一键切换
- ➕ **添加 fallback** - 添加模型到备份链
- ➖ **移除 fallback** - 从备份链移除模型
- 💓 **显示 Heartbeat 模型** - 查看心跳任务配置的模型
- 🤖 **显示 Subagents 模型** - 查看子智能体配置
- 🔐 **安全显示 API Key** - 只显示前8位
- 🔌 **重启 Gateway** - 让配置生效

## 触发方式

当用户说：
- "当前用什么模型" / "现在用哪个模型" / "查看模型配置"
- "切换到 xxx" / "用 xxx 模型" / "换成 xxx"
- "添加 xxx 到 fallback" / "加一个备份模型 xxx"
- "移除 xxx" / "删除 xxx fallback"
- "查看 heartbeat 模型" / "心跳用什么模型"
- "查看 subagents 模型"
- "重启" / "重启 gateway"

## 安全特性

- 所有操作本地执行，不联网
- API Key 只显示前8位，如 `sk-78155...`
- 修改前自动备份配置文件
- 修改后自动重启 Gateway

## 配置

无需额外配置，读取 `~/.openclaw/openclaw.json`
