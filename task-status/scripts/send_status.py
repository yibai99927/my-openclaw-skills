#!/usr/bin/env python3
"""Send short task status messages through OpenClaw.

Usage:
    python send_status.py "<message>" "<status_type>" "<step_name>" [options]

Examples:
    python send_status.py "开始执行" progress demo --target YOUR_CHAT_ID
    python send_status.py "处理完成" success demo --target YOUR_CHAT_ID --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

STATUS_ICONS = {
    "progress": "🔄",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
}

STATE_DIR = Path(__file__).resolve().parent / ".task-status"
CONFIG_FILE = STATE_DIR / "config.json"


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_config(config: dict[str, Any]) -> None:
    ensure_state_dir()
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_target(cli_target: str | None, config: dict[str, Any] | None = None) -> str | None:
    cfg = config or load_config()
    for value in (
        cli_target,
        os.environ.get("OPENCLAW_STATUS_TARGET"),
        os.environ.get("TASK_STATUS_TARGET"),
        os.environ.get("TELEGRAM_TARGET"),
        cfg.get("target"),
    ):
        if value and str(value).strip():
            return str(value).strip()
    return None


def resolve_channel(cli_channel: str | None, config: dict[str, Any] | None = None) -> str:
    cfg = config or load_config()
    for value in (
        cli_channel,
        os.environ.get("OPENCLAW_STATUS_CHANNEL"),
        cfg.get("channel"),
        "telegram",
    ):
        if value and str(value).strip():
            return str(value).strip()
    return "telegram"


def format_status(message: str, status_type: str, step_name: str, details: str | None = None) -> str:
    if status_type not in STATUS_ICONS:
        raise ValueError(f"Invalid status_type: {status_type}")

    text = f"{STATUS_ICONS[status_type]} [{step_name}] {message.strip()}"
    if details:
        text = f"{text} ({details.strip()})"

    if len(text) > 500:
        return f"{text[:497]}..."
    return text


def send_status(
    message: str,
    status_type: str,
    step_name: str,
    details: str | None = None,
    *,
    target: str | None = None,
    channel: str | None = None,
    reply_to: str | None = None,
    silent: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    formatted = format_status(message, status_type, step_name, details)
    cfg = load_config()
    resolved_target = resolve_target(target, cfg)
    resolved_channel = resolve_channel(channel, cfg)

    if not resolved_target:
        raise RuntimeError(
            "Missing target. Pass --target, run configure_status.py, or set OPENCLAW_STATUS_TARGET/TASK_STATUS_TARGET env."
        )

    cmd = [
        "openclaw",
        "message",
        "send",
        "--target",
        resolved_target,
        "--message",
        formatted,
        "--channel",
        resolved_channel,
        "--json",
    ]

    if reply_to:
        cmd.extend(["--reply-to", reply_to])
    if silent:
        cmd.append("--silent")
    if dry_run:
        cmd.append("--dry-run")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "openclaw message send failed")

    payload: dict[str, Any]
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw": proc.stdout.strip()}

    payload.update(
        {
            "formatted": formatted,
            "target": resolved_target,
            "channel": resolved_channel,
            "dryRun": dry_run,
        }
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send short task status messages")
    parser.add_argument("message", help="Status message text")
    parser.add_argument("status_type", choices=["progress", "success", "error", "warning"])
    parser.add_argument("step_name", help="Task step label")
    parser.add_argument("--details", help="Optional detail suffix", default=None)
    parser.add_argument("--target", help="Chat target id (e.g. Telegram chat id)")
    parser.add_argument("--channel", help="Channel name (defaults to config/env/telegram)")
    parser.add_argument("--reply-to", help="Reply to message id")
    parser.add_argument("--silent", action="store_true", help="Send silently")
    parser.add_argument("--dry-run", action="store_true", help="Dry run send")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = send_status(
            args.message,
            args.status_type,
            args.step_name,
            details=args.details,
            target=args.target,
            channel=args.channel,
            reply_to=args.reply_to,
            silent=args.silent,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"Error sending status: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
