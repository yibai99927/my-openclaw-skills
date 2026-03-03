#!/usr/bin/env python3
import argparse
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path


def fail(msg: str, code: int = 1):
    print(f"❌ {msg}")
    raise SystemExit(code)


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def chmod_600(path: Path):
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IRUSR | stat.S_IWUSR)
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def build_token_payload(creds, scopes):
    return {
        "token": {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes) if creds.scopes else scopes,
            "expiry": creds.expiry.isoformat() if getattr(creds, "expiry", None) else None,
        },
        "meta": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "scholar-push/auth_setup.py",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Gmail OAuth setup for Scholar Push")
    parser.add_argument(
        "--credentials",
        default=os.path.expanduser("~/.config/gmail/credentials.json"),
        help="OAuth client credentials JSON path",
    )
    parser.add_argument(
        "--token",
        default=os.path.expanduser("~/.config/gmail/token.json"),
        help="Output token JSON path",
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=["https://www.googleapis.com/auth/gmail.readonly"],
        help="OAuth scope (repeatable)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Local callback port for OAuth",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open browser",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify token by calling Gmail profile API",
    )
    args = parser.parse_args()

    credentials_path = Path(args.credentials).expanduser().resolve()
    token_path = Path(args.token).expanduser().resolve()
    scopes = list(dict.fromkeys(args.scope))

    if not credentials_path.exists():
        fail(f"credentials 文件不存在: {credentials_path}")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except Exception:
        fail("缺少依赖 google-auth-oauthlib，请先安装: pip3 install google-auth-oauthlib")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), scopes)
        creds = flow.run_local_server(
            host="127.0.0.1",
            port=args.port,
            open_browser=not args.no_browser,
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true",
        )
    except Exception as exc:
        fail(f"OAuth 授权失败: {exc}")

    if not getattr(creds, "refresh_token", None):
        fail("没有拿到 refresh_token。请在 Google 账户权限页移除该应用后重新授权，再重试。")

    payload = build_token_payload(creds, scopes)
    ensure_parent(token_path)
    token_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    chmod_600(token_path)

    print(f"✅ token 已写入: {token_path}")
    print("✅ 权限: 600 (仅当前用户可读写)")

    if args.verify:
        try:
            from googleapiclient.discovery import build

            service = build("gmail", "v1", credentials=creds)
            profile = service.users().getProfile(userId="me").execute()
            email = profile.get("emailAddress", "unknown")
            print(f"✅ Gmail 验证成功: {email}")
        except Exception as exc:
            fail(f"token 写入成功，但验证失败: {exc}")

    print("\n下一步可执行：")
    print("python3 skill.py list days 1")


if __name__ == "__main__":
    main()
