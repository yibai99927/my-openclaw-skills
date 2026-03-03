#!/usr/bin/env python3
"""Configure persistent defaults for task-status scripts.

Usage:
    python configure_status.py --target YOUR_CHAT_ID --channel telegram --test
"""

from __future__ import annotations

import argparse
import json
import sys

from send_status import load_config, save_config, send_status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure task-status defaults")
    parser.add_argument("--target", help="Default chat target id")
    parser.add_argument("--channel", help="Default channel (e.g. telegram)")
    parser.add_argument("--test", action="store_true", help="Send one test status after saving")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run the test message")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    config = load_config()
    changed = False

    if args.target:
        config["target"] = args.target.strip()
        changed = True
    if args.channel:
        config["channel"] = args.channel.strip()
        changed = True

    if changed:
        save_config(config)

    print(json.dumps({"saved": changed, "config": config}, ensure_ascii=False))

    if args.test:
        send_status(
            "task-status 默认通知配置完成",
            "success",
            "status-config",
            target=config.get("target"),
            channel=config.get("channel"),
            dry_run=args.dry_run,
        )
        print(json.dumps({"test": "sent", "dryRun": args.dry_run}, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
