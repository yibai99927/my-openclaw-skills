#!/usr/bin/env bash
set -euo pipefail
TASK_NAME=${1:-}
FINAL_STATUS=${2:-success}
FINAL_MESSAGE=${3:-任务完成}
TARGET=${4:-${OPENCLAW_STATUS_TARGET:-}}
CHANNEL=${5:-telegram}
if [[ -z "$TASK_NAME" ]]; then
  echo "Usage: $0 <task_name> [success|error|warning|progress] [final_message] [target] [channel]" >&2
  exit 1
fi
CMD=(python3 "$(dirname "$0")/monitor_task.py" stop "$TASK_NAME" --final-status "$FINAL_STATUS" --final-message "$FINAL_MESSAGE" --channel "$CHANNEL")
if [[ -n "$TARGET" ]]; then
  CMD+=(--target "$TARGET")
fi
"${CMD[@]}"
