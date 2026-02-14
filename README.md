# 🐼 OpenClaw 自定义 Skills

OpenClaw 个人定制技能集，包含 A股分析、ETF 行情、财经新闻、模型切换等工具。

---

## 📦 Skills 列表

### 1. etf-assistant-safe
ETF 投资助手 - 查询行情、筛选ETF、对比分析、定投计算

**功能**：
- 📊 ETF列表
- 💰 实时行情
- 🔍 搜索ETF
- 📈 对比分析
- 🧮 定投计算
- 📋 投资摘要

**使用**：
```bash
./skill.sh list
./skill.sh price 510300
./skill.sh hot
./skill.sh compare 510300 159915
./skill.sh calc 510300 1000 10
```

---

### 2. finance-news-safe
财经新闻汇总 - 整合 AKShare + Yahoo Finance

**功能**：
- 📈 A股指数行情
- 📰 热点新闻 (支持关键词搜索)
- 🌍 美股行情
- 📊 港股新闻

**使用**：
```bash
python3 skill.py all       # 全部概览
python3 skill.py a股       # A股指数
python3 skill.py 新闻 半导体  # 热点新闻
python3 skill.py 美股       # 美股行情
```

**依赖**：
```bash
pip3 install akshare --break-system-packages
```

---

### 3. model-switch
模型切换工具 - 快速切换 OpenClaw 默认模型

**功能**：
- 🔄 切换默认模型
- 📋 查看当前模型
- 🔁 模型回退链设置

**使用**：
```bash
# 查看帮助
./bin/model-switch help

# 切换模型
./bin/model-switch mini
./bin.switch codex
./bin/model-switch kimi
./bin/model-switch deepseek

# 查看当前
./bin/model-switch status
```

---

## 📁 目录结构

```
my-openclaw-skills/
├── etf-assistant-safe/    # ETF 投资助手
│   ├── SKILL.md
│   └── skill.sh
├── finance-news-safe/     # 财经新闻
│   ├── SKILL.md
│   └── skill.py
├── model-switch/          # 模型切换
│   ├── SKILL.md
│   ├── bin/
│   └── scripts/
├── A股观察清单模板.md      # A股分析模板
└── templates/             # 模板目录
```

---

## 🔧 安装方法

### 方法1：直接复制
```bash
cp -r etf-assistant-safe ~/.openclaw/workspace/skills/
cp -r finance-news-safe ~/.openclaw/workspace/skills/
cp -r model-switch ~/.openclaw/workspace/skills/
```

### 方法2：克隆仓库
```bash
git clone https://github.com/yibai99927/my-openclaw-skills.git
cp -r my-openclaw-skills/* ~/.openclaw/workspace/skills/
```

---

## 📋 A股分析模板

见 `A股观察清单模板.md`

**早盘分析**：
1. 核心结论（流动性、产业景气、海外扰动、风格）
2. 优先盯的线（主线、辅线、轮动）
3. 执行规则
4. 今日策略

**复盘**：
1. 今日个股实际走势表格
2. 复盘结论

---

## 📝 更新日志

### 2026-02-14
- ✅ 添加 model-switch 技能
- ✅ 添加 A股观察清单模板
- ✅ 优化 finance-news-safe 支持 AKShare

---

## ⚠️ 免责声明

本仓库提供的工具仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

## 🐼 关于

- 作者：Yibai
- OpenClaw：https://docs.openclaw.ai
- ClawHub：https://clawhub.com
