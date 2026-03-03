---
name: a-stock-analysis
description: A股综合分析系统，结合专业研报、社交媒体情绪、资金流向进行板块和股票推荐。使用AKShare获取数据，每日定时推送分析报告。
allowed-tools:
  - Bash
  - Read
  - web_search
  - web_fetch
---

# A股综合分析 Skill

## 功能

1. **大盘分析** - 实时行情、涨跌统计
2. **板块轮动** - 概念/行业板块资金流向
3. **涨停追踪** - 今日涨停股分析
4. **综合推荐** - 研报+情绪+资金三维验证
5. **风险提示** - 仓位建议和风险预警

## 数据来源

| 类型 | 来源 |
|------|------|
| 行情数据 | AKShare (东方财富) |
| 专业研报 | Web搜索 (券商观点) |
| 社交媒体 | Web搜索 (微博/雪球) |
| 资金流向 | AKShare (主力资金) |

## 使用方法

```bash
# 运行分析
python3 ~/.openclaw/workspace/skills/a-stock-analysis/analyze.py

# 开盘前分析
python3 ~/.openclaw/workspace/skills/a-stock-analysis/analyze.py morning

# 收盘后分析
python3 ~/.openclaw/workspace/skills/a-stock-analysis/analyze.py night
```

## 定时任务

- 开盘前 (08:00)：分析当日热点
- 收盘后 (15:30)：复盘+明日策略

## 分析维度

1. **研报逻辑** - 券商研报支撑
2. **资金流向** - 主力资金认可
3. **技术面** - 走势强度验证
4. **情绪面** - 社交媒体热度

## 输出格式

```
📊 大盘概况
🔥 热门板块
📈 涨停股
🎯 综合推荐
⚠️ 风险提示
```
