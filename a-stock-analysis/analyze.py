#!/usr/bin/env python3
"""A股统一入口：morning / night。"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
PIPELINE = os.path.join(WORKSPACE, "ashare_ai", "pipeline.py")


def run_command(command: list) -> int:
    process = subprocess.run(command, cwd=WORKSPACE)
    return process.returncode


def run_morning() -> int:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调用盘前推演流程")
    code = run_command([sys.executable, PIPELINE, "morning"])
    if code != 0:
        print("morning 推演失败")
        return code
    print("morning 推演完成")
    return 0


def run_night() -> int:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 调用盘后复盘流程")
    code = run_command([sys.executable, PIPELINE, "night"])
    if code != 0:
        print("night 复盘失败")
        return code
    print("night 复盘完成")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="A股分析统一入口")
    parser.add_argument("mode", choices=["morning", "night", "full"], nargs="?", default="full")
    args = parser.parse_args()

    if args.mode == "morning":
        return run_morning()
    if args.mode == "night":
        return run_night()

    code = run_morning()
    if code != 0:
        return code
    return run_night()


if __name__ == "__main__":
    raise SystemExit(main())
