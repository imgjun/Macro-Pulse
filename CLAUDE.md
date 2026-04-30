# Macro-Pulse — Claude Code Context

## What this project does

Daily market report bot. Fetches market data, grabs 5 images from the @yakjangsu Telegram channel (using Telethon MTProto), and sends a formatted summary to Telegram.

Two modes, auto-detected by UTC hour or forced via `--market`:
- **KR mode**: Mon–Fri 17:00 KST (08:00 UTC) — Korean market close summary
- **US mode**: Tue–Sat 06:30 KST (21:30 UTC) — US market close summary

## Execution environment

**Runs on GCP only.** GitHub Actions is CI/test only (`workflow_dispatch`). Do not re-add `schedule:` triggers to the workflow.

GCP instance: `trading-bot-seoul` | project: `tradingbot-korea` | zone: `us-east1-c`  
SSH: `gcloud compute ssh patrick.jang@trading-bot-seoul --project=tradingbot-korea --zone=us-east1-c`  
Code path: `/home/patrick.jang/Macro-Pulse`  
Log: `/home/patrick.jang/macro-pulse.log`

### GCP crontab (Macro-Pulse section)

```cron
# KR | 17:00 KST | 08:00 UTC | Mon-Fri
0 8 * * 1-5 cd /home/patrick.jang/Macro-Pulse && /home/patrick.jang/.local/bin/uv run python src/main.py --market KR >> /home/patrick.jang/macro-pulse.log 2>&1
# US | 06:30 KST | 21:30 UTC | Tue-Sat KST
30 21 * * 1-5 cd /home/patrick.jang/Macro-Pulse && /home/patrick.jang/.local/bin/uv run python src/main.py --market US >> /home/patrick.jang/macro-pulse.log 2>&1
```

To edit: `gcloud compute ssh ... --command="crontab -e"`  
To verify: `gcloud compute ssh ... --command="crontab -l | grep -A5 Macro-Pulse"`

## Environment variables

All 5 must be present in `/home/patrick.jang/Macro-Pulse/.env` on GCP and in GitHub Secrets.

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot API token (from @BotFather). Revoked/reissued 2026-04-30 — both Macro-Pulse and trading-bot-seoul use the same token. |
| `TELEGRAM_CHAT_ID` | Patrick's personal Telegram user ID (bot sends reports here). |
| `TELEGRAM_API_ID` | From my.telegram.org — Telethon MTProto credential. |
| `TELEGRAM_API_HASH` | From my.telegram.org — Telethon MTProto credential. |
| `TELEGRAM_SESSION_STRING` | Telethon StringSession — generated once via `uv run python scripts/generate_session.py`. Re-run if auth errors appear in the log. |

To update `.env` on GCP:
```
gcloud compute scp .env patrick.jang@trading-bot-seoul:/home/patrick.jang/Macro-Pulse/.env --project=tradingbot-korea --zone=us-east1-c
```

## Key source files

| File | Purpose |
|---|---|
| `src/macro_pulse/app/cli.py` | Entry point. `resolve_mode()` auto-detects KR/US by UTC hour. |
| `src/macro_pulse/data/providers/telegram_channel.py` | Telethon fetcher — pulls latest batch of 5 images from @yakjangsu. |
| `src/macro_pulse/reporting/screenshots.py` | Screenshot handlers. `yakjangsu` handler calls the Telethon fetcher. |
| `config/report_formats.json` | Per-mode config. US mode uses `"screenshot_targets": ["yakjangsu"]`. |
| `scripts/generate_session.py` | One-time Telethon StringSession generator. Run locally, paste output to `.env`. |
| `.github/workflows/daily_report.yml` | CI only — no schedule. Manual trigger via `workflow_dispatch`. |

## How yakjangsu image selection works

Telethon reads the last ~20 messages from `@yakjangsu`, groups them by posting time into 5-minute windows (`BATCH_WINDOW_SECONDS = 300`), picks the most recent batch, and returns up to 5 images in chronological order (oldest first = natural posting order).

## GitHub

Repo: `imgjun/Macro-Pulse`  
Push via: `"C:\Program Files\Git\cmd\git.exe"` (git not on default PATH in some shells)  
Note: After push, a stale `.git/refs/remotes/origin/main.lock` sometimes appears — safe to delete.

## Related project

`trading-bot-seoul` (separate repo: `imgjun/GCP_trading-bot-seoul`)  
Same GCP instance, different directory: `/home/patrick.jang/trading-bot-seoul`  
Shares `TELEGRAM_BOT_TOKEN` with Macro-Pulse. If token is rotated, update **both** `.env` files on GCP.

To sync token from Macro-Pulse → trading-bot-seoul:
```
gcloud compute ssh ... --command="python3 /home/patrick.jang/Macro-Pulse/scripts/_update_token.sh"
```
(Script is actually Python despite the `.sh` extension — reads from Macro-Pulse `.env`, patches trading-bot-seoul `.env`.)

## Security notes

- `.env` is gitignored. Never commit it.
- `*.session` and `*.session-journal` are gitignored (Telethon auth files).
- Git history was cleaned of a previously exposed bot token on 2026-04-30 using `git filter-branch` + force push.
- Old token was revoked via @BotFather on the same date.

## Common operations

**Check last run log:**
```
gcloud compute ssh patrick.jang@trading-bot-seoul --project=tradingbot-korea --zone=us-east1-c --command="tail -80 /home/patrick.jang/macro-pulse.log"
```

**Manual test run (dry run — no Telegram send):**
```
gcloud compute ssh ... --command="cd /home/patrick.jang/Macro-Pulse && /home/patrick.jang/.local/bin/uv run python src/main.py --market US --dry-run"
```

**Pull latest code to GCP:**
```
gcloud compute ssh ... --command="git -C /home/patrick.jang/Macro-Pulse pull origin main"
```

**Regenerate Telethon session (if auth expired):**
Run locally: `uv run python scripts/generate_session.py`  
Update `TELEGRAM_SESSION_STRING` in local `.env`, then SCP to GCP.
