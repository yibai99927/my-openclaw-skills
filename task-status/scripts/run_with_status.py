#!/usr/bin/env python3
"""Run any command with guaranteed start/end status callbacks.

Usage:
    python run_with_status.py --task mytask --target YOUR_CHAT_ID -- <command> [args...]

Example:
    python run_with_status.py --task demo --target YOUR_CHAT_ID -- bash -lc "sleep 2 && echo ok"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time

from send_status import send_status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run command with status notifications")
    parser.add_argument("--task", required=True, help="Task name used as step label")
    parser.add_argument("--target", help="Chat target id")
    parser.add_argument("--channel", default="telegram", help="Message channel")
    parser.add_argument("--start-message", default="Task started")
    parser.add_argument("--success-message", default="Task completed")
    parser.add_argument("--error-message", default="Task failed")
    parser.add_argument("--dry-run", action="store_true", help="Dry run status send")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute (prefix with --)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("Missing command. Example: -- bash -lc 'echo hello'", file=sys.stderr)
        return 1

    start_at = time.time()

    send_status(
        args.start_message,
        "progress",
        args.task,
        target=args.target,
        channel=args.channel,
        dry_run=args.dry_run,
    )

    try:
        proc = subprocess.run(command)
        cost = round(time.time() - start_at, 1)

        if proc.returncode == 0:
            send_status(
                args.success_message,
                "success",
                args.task,
                details=f"elapsed={cost}s",
                target=args.target,
                channel=args.channel,
                dry_run=args.dry_run,
            )
            return 0

        send_status(
            args.error_message,
            "error",
            args.task,
            details=f"exit={proc.returncode}, elapsed={cost}s",
            target=args.target,
            channel=args.channel,
            dry_run=args.dry_run,
        )
        return proc.returncode
    except Exception as exc:
        cost = round(time.time() - start_at, 1)
        send_status(
            args.error_message,
            "error",
            args.task,
            details=f"exception={exc}, elapsed={cost}s",
            target=args.target,
            channel=args.channel,
            dry_run=args.dry_run,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
