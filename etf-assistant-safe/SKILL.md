# ETF投资助理 (安全版)

一个安全的ETF投资助手，仅使用Yahoo Finance公开API，无敏感配置。

## 功能

- 📊 ETF列表 - 常用ETF代码速查
- 💰 实时行情 - 查询ETF当前价格和涨跌
- 🔍 搜索ETF - 按名称或代码搜索
- 📈 对比分析 - 对比两只ETF表现
- 🧮 定投计算器 - 计算定投收益

## 使用方法

```bash
# 查看ETF列表
etf-assistant-safe list

# 查询行情
etf-assistant-safe price 510300

# 搜索ETF
etf-assistant-safe search 沪深

# 对比ETF
etf-assistant-safe compare 510300 159915

# 定投计算
etf-assistant-safe calc 510300 1000 10

# 投资摘要
etf-assistant-safe summary
```

## 安全说明

- ✅ 仅使用Yahoo Finance公开API
- ✅ 无需API Key
- ✅ 无敏感配置要求
- ✅ 无外部依赖

## 数据来源

Yahoo Finance
