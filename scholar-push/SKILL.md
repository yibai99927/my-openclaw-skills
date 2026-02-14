# Scholar Push - Google Scholar 文献推送

从 Gmail 获取 Google Scholar 推送的文献，按指定格式整理输出。

## 功能

- 📧 获取 Gmail 中 Google Scholar 推送的新文章
- 🎯 通过 DOI/CrossRef API 查询精确期刊/会议信息
- 📋 按统一格式输出：标题、作者、期刊/会议、推送时间

## 使用方法

```bash
# 获取最近24小时的推送
python3 skill.py recent

# 获取所有推送（默认）
python3 skill.py all

# 获取指定天数内的推送
python3 skill.py days 3
```

## 输出格式

```
📬 Google Scholar 文献推送 (共X篇)

---

【1】论文标题
作者：作者名
期刊/会议：精确期刊/会议名
推送时间：YYYY.MM.DD

【2】论文标题
...
```

## 技术细节

- Gmail API: 获取 scholaralerts-noreply@google.com 发送的邮件
- CrossRef API: 通过 DOI 查询精确期刊/会议信息
- 支持 Nature、Science Advances、IEEE IEDM、Advanced Materials 等精确期刊名

## 注意事项

- 需要 Gmail OAuth 认证 (~/.config/gmail/token.json)
- 需要网络访问 CrossRef API
- 首次使用需要配置 Gmail 认证
