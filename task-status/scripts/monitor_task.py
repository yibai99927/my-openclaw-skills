#!/usr/bin/env python3
"""Monitor long-running tasks and send periodic status updates.

Usage:
    python monitor_task.py start <task_name> [--interval 300] [--target <id>]
    python monitor_task.py stop <task_name> [--final-status success] [--final-message "Done"]
    python monitor_task.py status
    python monitor_task.py cancel_all

Notes:
- `start` forks a detached background runner and returns immediately.
- `stop` always sends one final status update.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from send_status import resolve_target, send_status

STATE_DIR = Path(__file__).resolve().parent / ".task-status"
STATE_FILE = STATE_DIR / "monitors.json"


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    ensure_state_dir()
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict[str, Any]) -> None:
    ensure_state_dir()
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_name(task_name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_name)[:80]


def control_file(task_name: str) -> Path:
    return STATE_DIR / f"{safe_name(task_name)}.running"


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_monitor(args: argparse.Namespace) -> int:
    state = load_state()
    existing = state.get(args.task_name)
    if existing and pid_alive(existing.get("pid", -1)):
        print(f"Already monitoring: {args.task_name} (pid={existing['pid']})")
        return 1

    target = resolve_target(args.target)
    if not target and not args.dry_run:
        print(
            "Missing target. Pass --target or set OPENCLAW_STATUS_TARGET/TASK_STATUS_TARGET.",
            file=sys.stderr,
        )
        return 1

    ctrl = control_file(args.task_name)
    ctrl.write_text("running", encoding="utf-8")

    send_status(
        f"Monitoring started (interval={args.interval}s)",
        "progress",
        args.task_name,
        target=target,
        channel=args.channel,
        dry_run=args.dry_run,
    )

    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "run",
        args.task_name,
        "--interval",
        str(args.interval),
        "--channel",
        args.channel,
    ]
    if target:
        cmd.extend(["--target", target])
    if args.dry_run:
        cmd.append("--dry-run")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    state[args.task_name] = {
        "pid": proc.pid,
        "interval": args.interval,
        "channel": args.channel,
        "target": target,
        "dry_run": args.dry_run,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    save_state(state)

    print(f"Monitor started: {args.task_name} (pid={proc.pid}, interval={args.interval}s)")
    return 0


def run_monitor(args: argparse.Namespace) -> int:
    ctrl = control_file(args.task_name)
    while ctrl.exists():
        try:
            send_status(
                "Still working...",
                "progress",
                args.task_name,
                target=args.target,
                channel=args.channel,
                dry_run=args.dry_run,
            )
        except Exception:
            pass
        time.sleep(max(args.interval, 1))
    return 0


def stop_monitor(args: argparse.Namespace) -> int:
    state = load_state()
    info = state.get(args.task_name)

    target = args.target or (info or {}).get("target")
    channel = args.channel or (info or {}).get("channel") or "telegram"
    dry_run = args.dry_run or bool((info or {}).get("dry_run", False))

    ctrl = control_file(args.task_name)
    if ctrl.exists():
        ctrl.unlink(missing_ok=True)

    if info and pid_alive(info.get("pid", -1)):
        try:
            os.kill(info["pid"], signal.SIGTERM)
        except OSError:
            pass

    if args.task_name in state:
        del state[args.task_name]
        save_state(state)

    send_status(
        args.final_message,
        args.final_status,
        args.task_name,
        target=target,
        channel=channel,
        dry_run=dry_run,
    )

    print(f"Monitor stopped: {args.task_name}")
    return 0


def show_status() -> int:
    state = load_state()
    if not state:
        print("No active monitors")
        return 0

    print("Active monitors:")
    for task_name, info in state.items():
        pid = info.get("pid", -1)
        alive = pid_alive(pid)
        print(
            f"- {task_name}: pid={pid} alive={alive} interval={info.get('interval')}s "
            f"channel={info.get('channel')}"
        )
    return 0


def cancel_all() -> int:
    state = load_state()
    for task_name, info in state.items():
        ctrl = control_file(task_name)
        ctrl.unlink(missing_ok=True)
        pid = info.get("pid", -1)
        if pid_alive(pid):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
    save_state({})
    print("Cancelled all monitors")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task status monitor")
    sub = parser.add_subparsers(dest="action", required=True)

    start = sub.add_parser("start", help="Start background monitor")
    start.add_argument("task_name")
    start.add_argument("--interval", type=int, default=300)
    start.add_argument("--target")
    start.add_argument("--channel", default="telegram")
    start.add_argument("--dry-run", action="store_true")

    run = sub.add_parser("run", help="Internal monitor loop")
    run.add_argument("task_name")
    run.add_argument("--interval", type=int, default=300)
    run.add_argument("--target")
    run.add_argument("--channel", default="telegram")
    run.add_argument("--dry-run", action="store_true")

    stop = sub.add_parser("stop", help="Stop monitor and send final status")
    stop.add_argument("task_name")
    stop.add_argument("--final-status", choices=["success", "error", "warning", "progress"], default="success")
    stop.add_argument("--final-message", default="Task completed")
    stop.add_argument("--target")
    stop.add_argument("--channel")
    stop.add_argument("--dry-run", action="store_true")

    sub.add_parser("status", help="List active monitors")
    sub.add_parser("cancel_all", help="Cancel all monitors")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "start":
        return start_monitor(args)
    if args.action == "run":
        return run_monitor(args)
    if args.action == "stop":
        return stop_monitor(args)
    if args.action == "status":
        return show_status()
    if args.action == "cancel_all":
        return cancel_all()
    print(f"Unknown action: {args.action}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
