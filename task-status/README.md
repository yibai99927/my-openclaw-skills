# task-status

Reliable progress/finish notifications for OpenClaw tasks.

## What changed

This version is adapted for OpenClaw:
- Uses `openclaw message send` for delivery.
- Supports persisted defaults (`target`/`channel`) in local config.
- Adds `run_with_status.py` to guarantee final callback.
- Fixes monitor logic: `start` now launches a detached worker process.

## Quick start

```bash
python scripts/configure_status.py --target YOUR_CHAT_ID --channel telegram --test
python scripts/run_with_status.py --task demo -- bash -lc "sleep 2 && echo ok"
```

## Scripts

- `scripts/configure_status.py`: set default target/channel.
- `scripts/send_status.py`: send one status message.
- `scripts/run_with_status.py`: wrap a command with start/end status.
- `scripts/monitor_task.py`: periodic monitor (`start`/`stop`/`status`/`cancel_all`).

## Example monitor flow

```bash
python scripts/monitor_task.py start long-task --interval 300
python scripts/monitor_task.py status
python scripts/monitor_task.py stop long-task --final-status success --final-message "任务完成"
```

## Dry run

```bash
python scripts/send_status.py "测试" progress dry --dry-run
python scripts/run_with_status.py --task dry --dry-run -- bash -lc "echo ok"
```
