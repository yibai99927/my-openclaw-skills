#!/usr/bin/env python3
"""
MiniMax VL - 图片理解工具
通过 MiniMax MCP 调用视觉模型
"""

import os
import sys
import subprocess

API_KEY = "sk-cp-tmBPJ6zO_1ibLb_CU8JZEHewx3hThPFXGodC-pLqmFG3AZ3tahsbOYn27DglcTs4iIG6Bq0LfRNGTdjHMwP1YVNXlkVNA-f6wcdA9M53TcHDVieqSzzP9wc"
API_HOST = "https://api.minimaxi.com"

def understand_image(image_path, prompt="请描述这张图片"):
    """调用 MiniMax MCP 理解图片"""
    
    # 使用 shell 命令
    cmd = f'''export PATH="/home/yibai/.local/bin:$PATH" && export MINIMAX_API_KEY="{API_KEY}" && export MINIMAX_API_HOST="{API_HOST}" && mcporter call --stdio "uvx minimax-coding-plan-mcp" understand_image "prompt:{prompt}" "image_source:{image_path}"'''
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 skill.py <image_path> [prompt]")
        print("Example: python3 skill.py /path/to/image.jpg '请描述这张图片'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "请描述这张图片"
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    result = understand_image(image_path, prompt)
    print(result)

if __name__ == "__main__":
    main()
