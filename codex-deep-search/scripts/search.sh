#!/bin/bash
#=====================================
# Codex Deep Search Script
# 深度检索 + Telegram 回调 + JSON sidecar
#=====================================

set -euo pipefail

# 默认配置
RESULT_DIR="/tmp/codex-search"
CODEX_BIN="codex"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
TELEGRAM_TOKEN_FILE="${TELEGRAM_TOKEN_FILE:-$HOME/.openclaw/telegram-bot-token}"
TIMEOUT="${TIMEOUT:-120}"
WORKDIR="${WORKDIR:-$HOME/.openclaw/workspace}"

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --task-name)
            TASK_NAME="$2"
            shift 2
            ;;
        --telegram-group)
            TELEGRAM_CHAT_ID="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --out-json)
            OUT_JSON="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 设置默认值
TASK_NAME=${TASK_NAME:-"search-$(date +%Y%m%d-%H%M%S)"}
PROMPT=${PROMPT:-"请搜索相关信息"}
OUT_JSON=${OUT_JSON:-"$RESULT_DIR/$TASK_NAME.json"}
TXT_PATH="$RESULT_DIR/$TASK_NAME.txt"

# 创建结果目录
mkdir -p "$RESULT_DIR"

# 发送通知
send_message() {
    local message="$1"
    local token
    token="${TELEGRAM_BOT_TOKEN:-}"
    if [ -z "$token" ] && [ -f "$TELEGRAM_TOKEN_FILE" ]; then
        token=$(cat "$TELEGRAM_TOKEN_FILE" 2>/dev/null || true)
    fi
    if [ -n "$token" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" \
            -d "parse_mode=Markdown" >/dev/null || true
    fi
}

echo "========================================="
echo "Codex Deep Search"
echo "任务: $TASK_NAME"
echo "========================================="

send_message "🔍 *Codex 深度搜索开始*\n\n任务: $TASK_NAME\n提示: $PROMPT\n\n请稍候..."

cd "$WORKDIR"
if command -v timeout >/dev/null 2>&1; then
    timeout "$TIMEOUT" "$CODEX_BIN" exec "$PROMPT" > "$TXT_PATH" 2>&1 || EXIT_CODE=$?
else
    "$CODEX_BIN" exec "$PROMPT" > "$TXT_PATH" 2>&1 || EXIT_CODE=$?
fi
EXIT_CODE=${EXIT_CODE:-0}

# 输出 sidecar JSON
export TASK_NAME PROMPT OUT_JSON TXT_PATH
python3 - <<'PY'
import json, re, datetime, os

task = os.environ.get("TASK_NAME", "task")
txt_path = os.environ.get("TXT_PATH", f"/tmp/codex-search/{task}.txt")
out_path = os.environ.get("OUT_JSON", f"/tmp/codex-search/{task}.json")
prompt = os.environ.get("PROMPT", "")

text = ""
if os.path.exists(txt_path):
    text = open(txt_path, "r", encoding="utf-8", errors="ignore").read()

def parse_json_payload(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    candidates = [raw]
    fenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I | re.S).strip()
    if fenced and fenced != raw:
        candidates.append(fenced)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception:
            try:
                obj, _ = decoder.raw_decode(candidate)
                return obj
            except Exception:
                pass
    return None

items = []
begin = text.find("BEGIN_JSON")
if begin != -1:
    end = text.find("END_JSON", begin + len("BEGIN_JSON"))
    if end != -1:
        payload = parse_json_payload(text[begin + len("BEGIN_JSON"):end])
        if isinstance(payload, dict) and "items" in payload:
            items = payload.get("items", []) or []
        elif isinstance(payload, list):
            items = payload

if not items:
    urls = sorted(set(re.findall(r"https?://[^\s\]\)\"'>,]+", text)))
    items = [{"title": "", "url": u, "source": "", "time": "", "snippet": ""} for u in urls[:60]]

normalized = []
for it in items:
    if not isinstance(it, dict):
        continue
    normalized.append(
        {
            "title": str(it.get("title", "") or ""),
            "url": str(it.get("url", "") or ""),
            "source": str(it.get("source", "") or ""),
            "time": str(it.get("time", "") or ""),
            "snippet": str(it.get("snippet", "") or ""),
            "category": str(it.get("category", "") or ""),
        }
    )

out = {
    "task_name": task,
    "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
    "prompt": prompt,
    "items": normalized,
}

os.makedirs(os.path.dirname(out_path), exist_ok=True)
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"[codex-deep-search] wrote json: {out_path} items={len(normalized)}")
PY

if [ "$EXIT_CODE" -eq 0 ]; then
    RESULT=$(cat "$TXT_PATH")
    send_message "✅ *Codex 搜索完成*\n\n任务: $TASK_NAME\n\n---\n\n$RESULT"
    echo "搜索完成，结果已保存到 $TXT_PATH"
else
    send_message "❌ *Codex 搜索失败*\n\n任务: $TASK_NAME\n\n错误码: $EXIT_CODE"
    echo "搜索失败，错误码: $EXIT_CODE"
fi

exit "$EXIT_CODE"
