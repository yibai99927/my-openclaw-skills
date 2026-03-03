# Task Status Usage

## One-time config (recommended)

```bash
python scripts/configure_status.py --target YOUR_CHAT_ID --channel telegram --test
```

This writes a local config file used by all scripts.

## Recommended: command wrapper

Use `run_with_status.py` to guarantee final callback.

```bash
python scripts/run_with_status.py --task demo -- bash -lc "sleep 1 && echo ok"
python scripts/run_with_status.py --task demo -- bash -lc "exit 2"
```

## Manual status send

```bash
python scripts/send_status.py "正在处理" progress fetch
python scripts/send_status.py "处理成功" success fetch
python scripts/send_status.py "处理失败" error fetch
```

## Periodic monitor

```bash
python scripts/monitor_task.py start nightly-report --interval 300
python scripts/monitor_task.py status
python scripts/monitor_task.py stop nightly-report --final-status success --final-message "报告已生成"
```

## Dry run

```bash
python scripts/send_status.py "测试消息" progress dryrun --dry-run
python scripts/run_with_status.py --task dryrun --dry-run -- bash -lc "echo hi"
```
