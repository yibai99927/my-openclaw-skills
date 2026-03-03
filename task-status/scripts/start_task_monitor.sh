#!/usr/bin/env bash
set -euo pipefail
TASK_NAME=${1:-}
INTERVAL=${2:-600}
TARGET=${3:-${OPENCLAW_STATUS_TARGET:-}}
CHANNEL=${4:-telegram}
if [[ -z "$TASK_NAME" ]]; then
  echo "Usage: $0 <task_name> [interval_seconds] [target] [channel]" >&2
  exit 1
fi
CMD=(python3 "$(dirname "$0")/monitor_task.py" start "$TASK_NAME" --interval "$INTERVAL" --channel "$CHANNEL")
if [[ -n "$TARGET" ]]; then
  CMD+=(--target "$TARGET")
fi
"${CMD[@]}"
