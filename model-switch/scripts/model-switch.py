#!/usr/bin/env python3
"""
Model Switch - OpenClaw Model Management Skill
管理 OpenClaw 模型切换的 Python 脚本
"""

import json
import subprocess
import sys
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
BACKUP_DIR = Path.home() / ".openclaw" / "backups"


def load_config() -> Optional[dict]:
    """加载配置文件"""
    try:
        if not CONFIG_PATH.exists():
            print(f"❌ 配置文件不存在: {CONFIG_PATH}", file=sys.stderr)
            return None
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                print(f"❌ 配置文件格式错误: 期望 object, 得到 {type(config).__name__}", file=sys.stderr)
                return None
            return config
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"❌ 文件读取错误: {e}", file=sys.stderr)
        return None


def save_config(config: dict) -> Optional[Path]:
    """保存配置文件（原子写入 + 备份）"""
    if not isinstance(config, dict):
        print("❌ 无效的配置数据", file=sys.stderr)
        return None
    
    # 创建备份
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"openclaw.json.backup_{timestamp}"
    
    try:
        # 先备份当前配置
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                old_config = json.load(f)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(old_config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 备份失败: {e}", file=sys.stderr)
        # 继续尝试写入
    
    # 原子写入：先写临时文件，再 rename
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as tmp:
            json.dump(config, tmp, indent=2, ensure_ascii=False)
            tmp_path = tmp.name
        
        # 确保写入磁盘
        tmp_path = Path(tmp_path)
        tmp_path.chmod(0o644)
        
        # 原子替换
        shutil.move(str(tmp_path), str(CONFIG_PATH))
        return backup_path
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}", file=sys.stderr)
        # 清理临时文件
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except:
            pass
        return None


def mask_api_key(key: str) -> str:
    """安全显示 API Key，只显示前8位"""
    if not key:
        return "未设置"
    if len(key) <= 8:
        return key[:4] + "..."
    return key[:8] + "..."


def check_openclaw_cmd() -> bool:
    """检查 openclaw 命令是否可用"""
    return shutil.which("openclaw") is not None


def get_all_models(config: dict) -> list:
    """获取所有已配置的模型"""
    models = []
    
    # 主模型
    primary = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    if primary:
        models.append({"id": primary, "type": "primary"})
    
    # Fallback 链
    fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
    for i, fb in enumerate(fallbacks):
        models.append({"id": fb, "type": "fallback", "order": i + 1})
    
    return models


def format_model_list(models: list) -> str:
    """格式化模型列表"""
    if not models:
        return "没有配置任何模型"
    
    lines = ["📋 **模型配置**", ""]
    
    for m in models:
        if m["type"] == "primary":
            lines.append(f"🔹 **主模型**: `{m['id']}`")
        else:
            lines.append(f"  {m['order']}. `{m['id']}` (fallback)")
    
    return "\n".join(lines)


def get_model_by_name_or_number(config: dict, name_or_number: str) -> Optional[str]:
    """根据名称或编号查找模型（精确匹配优先）"""
    models = get_all_models(config)
    all_models = [m["id"] for m in models]
    name_lower = name_or_number.lower().strip()
    
    # 1. 尝试解析编号
    try:
        idx = int(name_or_number) - 1
        if 0 <= idx < len(all_models):
            return all_models[idx]
    except ValueError:
        pass
    
    # 2. 精确匹配 model id（全等）
    for model_id in all_models:
        if model_id.lower() == name_lower:
            return model_id
    
    # 3. 匹配 alias
    models_aliases = config.get("agents", {}).get("defaults", {}).get("models", {})
    for model_id, model_info in models_aliases.items():
        alias = model_info.get("alias", "")
        if alias and alias.lower() == name_lower:
            return model_id
    
    # 4. 前缀匹配
    for model_id in all_models:
        if model_id.lower().startswith(name_lower):
            return model_id
    
    # 5. 模糊匹配（包含）
    matches = [m for m in all_models if name_lower in m.lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # 多匹配返回 None，让用户确认
        return None
    
    return None


def switch_model(config: dict, target_model: str) -> tuple:
    """切换主模型"""
    target = get_model_by_name_or_number(config, target_model)
    if not target:
        # 尝试直接使用输入的名称
        target = target_model.strip()
    
    all_models = [m["id"] for m in get_all_models(config)]
    
    # 如果模型不在列表中，添加到 fallback 链
    if target not in all_models:
        fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
        fallbacks.append(target)
        config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["fallbacks"] = fallbacks
    
    # 原主模型加入 fallback 链头部（去重）
    old_primary = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    if old_primary and old_primary != target:
        fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
        # 去重
        fallbacks = [f for f in fallbacks if f != old_primary and f != target]
        # 插入到头部
        fallbacks.insert(0, old_primary)
        config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["fallbacks"] = fallbacks
    
    # 设置为主模型
    config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["primary"] = target
    
    if save_config(config):
        return True, f"已切换主模型为: `{target}`"
    return False, "保存配置失败"


def add_fallback(config: dict, model_name: str) -> tuple:
    """添加 fallback 模型"""
    target = get_model_by_name_or_number(config, model_name)
    if not target:
        target = model_name.strip()
    
    # 检查是否已在主模型
    primary = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
    if target == primary:
        return True, f"`{target}` 已经是主模型"
    
    # 检查是否已在 fallback（去重）
    fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
    if target in fallbacks:
        return True, f"`{target}` 已经在 fallback 链中"
    
    # 添加
    fallbacks.append(target)
    config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["fallbacks"] = fallbacks
    
    if save_config(config):
        return True, f"已添加 `{target}` 到 fallback 链"
    return False, "保存配置失败"


def remove_fallback(config: dict, model_name: str) -> tuple:
    """移除 fallback 模型"""
    target = get_model_by_name_or_number(config, model_name)
    if not target:
        return False, f"找不到模型: {model_name}"
    
    fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
    
    if target not in fallbacks:
        return False, f"`{target}` 不在 fallback 链中"
    
    fallbacks.remove(target)
    config.setdefault("agents", {}).setdefault("defaults", {}).setdefault("model", {})["fallbacks"] = fallbacks
    
    if save_config(config):
        return True, f"已从 fallback 链移除 `{target}`"
    return False, "保存配置失败"


def show_heartbeat_model(config: dict) -> str:
    """显示 Heartbeat 模型配置"""
    heartbeat = config.get("agents", {}).get("defaults", {}).get("heartbeat", {})
    model = heartbeat.get("model", "未配置")
    return f"💓 **Heartbeat 模型**: `{model}`"


def show_subagents_model(config: dict) -> str:
    """显示 Subagents 模型配置"""
    subagents = config.get("agents", {}).get("defaults", {}).get("subagents", {})
    model = subagents.get("model", "未配置")
    
    if isinstance(model, dict):
        primary = model.get("primary", "未配置")
        fallbacks = model.get("fallbacks", [])
        if fallbacks:
            fb_list = ", ".join([f"`{f}`" for f in fallbacks])
            return f"🤖 **Subagents 模型**:\n  主模型: `{primary}`\n  Fallback: {fb_list}"
        return f"🤖 **Subagents 模型**: `{primary}`"
    
    return f"🤖 **Subagents 模型**: `{model}`"


def show_api_keys(config: dict) -> str:
    """显示 API Keys (安全模式)"""
    lines = ["🔐 **API Keys**", ""]
    
    # 从 env.vars 获取
    env_vars = config.get("env", {}).get("vars", {})
    for key, value in env_vars.items():
        if "API_KEY" in key.upper():
            lines.append(f"- `{key}`: `{mask_api_key(value)}`")
    
    # 从 auth.profiles 获取
    auth = config.get("auth", {}).get("profiles", {})
    for profile_id, profile_info in auth.items():
        if profile_info.get("mode") == "api_key":
            provider = profile_info.get("provider", "unknown")
            lines.append(f"- {profile_id}: API Key 已配置")
    
    if len(lines) == 1:
        return "🔐 没有找到 API Key 配置"
    
    return "\n".join(lines)


def restart_gateway() -> tuple:
    """重启 Gateway（后台运行 + 超时检测）"""
    if not check_openclaw_cmd():
        return False, "❌ 找不到 openclaw 命令，请确保已安装"
    
    try:
        # 后台启动重启
        result = subprocess.Popen(
            ["openclaw", "gateway", "restart"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待最多 10 秒
        try:
            stdout, stderr = result.communicate(timeout=10)
            if result.returncode == 0:
                return True, "✅ Gateway 已重启"
            else:
                return False, f"❌ 重启失败: {stderr.strip()}"
        except subprocess.TimeoutExpired:
            # 超时但可能正在重启，视为成功
            result.kill()
            return True, "✅ Gateway 正在重启（后台进行中）"
            
    except Exception as e:
        return False, f"❌ 重启失败: {str(e)}"


def handle_command(command: str, args: str = "") -> str:
    """处理命令"""
    config = load_config()
    if not config:
        return "❌ 无法读取配置文件"
    
    cmd = command.lower().strip()
    
    # 查看当前模型
    if cmd in ["status", "查看", "当前模型", "什么模型"]:
        models = get_all_models(config)
        result = format_model_list(models)
        result += "\n\n" + show_api_keys(config)
        return result
    
    # 切换主模型
    if cmd in ["switch", "切换", "换成", "用"]:
        if not args:
            return "❌ 请指定要切换的模型"
        success, msg = switch_model(config, args)
        if success:
            # 尝试重启
            restart_ok, restart_msg = restart_gateway()
            msg += f"\n{restart_msg}"
        return msg
    
    # 添加 fallback
    if cmd in ["add", "添加", "加"]:
        if not args:
            return "❌ 请指定要添加的模型"
        # 移除 "到 fallback" 等后缀
        clean_args = args.replace("到 fallback", "").replace("fallback", "").strip()
        success, msg = add_fallback(config, clean_args)
        if success:
            restart_ok, restart_msg = restart_gateway()
            msg += f"\n{restart_msg}"
        return msg
    
    # 移除 fallback
    if cmd in ["remove", "移除", "删除", "去掉"]:
        if not args:
            return "❌ 请指定要移除的模型"
        success, msg = remove_fallback(config, args)
        if success:
            restart_ok, restart_msg = restart_gateway()
            msg += f"\n{restart_msg}"
        return msg
    
    # Heartbeat 模型
    if cmd in ["heartbeat", "心跳"]:
        return show_heartbeat_model(config)
    
    # Subagents 模型
    if cmd in ["subagents", "子智能体"]:
        return show_subagents_model(config)
    
    # API Keys
    if cmd in ["keys", "apikey", "密钥"]:
        return show_api_keys(config)
    
    # 重启
    if cmd in ["restart", "重启"]:
        success, msg = restart_gateway()
        return msg
    
    # 帮助
    if cmd in ["help", "帮助", "?"]:
        return """📖 **可用命令**:

- `status` - 查看当前模型配置
- `switch <模型>` - 切换主模型
- `add <模型>` - 添加到 fallback 链
- `remove <模型>` - 从 fallback 链移除
- `heartbeat` - 查看心跳模型
- `subagents` - 查看子智能体模型
- `keys` - 查看 API Keys
- `restart` - 重启 Gateway

示例:
- `switch Codex`
- `add deepseek`
- `remove 2`
"""
    
    return f"❌ 未知命令: {command}\n\n输入 `help` 查看可用命令"


if __name__ == "__main__":
    # 从命令行参数获取命令
    if len(sys.argv) < 2:
        print("Usage: model-switch.py <command> [args]")
        print("Commands: status, switch, add, remove, heartbeat, subagents, keys, restart, help")
        sys.exit(1)
    
    command = sys.argv[1]
    # 合并所有剩余参数，支持多单词
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    result = handle_command(command, args)
    print(result)
