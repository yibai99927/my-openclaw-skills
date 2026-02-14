# MiniMax VL - 图片理解

通过 MiniMax MCP 调用视觉模型进行图片理解。

## 功能

- 🖼️ **图片理解**：分析图片内容，描述图像中的物体、场景等

## 使用方法

```bash
# 分析图片
python3 skill.py /path/to/image.jpg "请描述这张图片"
```

## 依赖

- uvx (已安装)
- mcporter
- MiniMax Coding Plan API Key

## 环境变量

需要在调用时设置：
- `MINIMAX_API_KEY`: 你的 MiniMax Coding Plan API Key
- `MINIMAX_API_HOST`: https://api.minimaxi.com
