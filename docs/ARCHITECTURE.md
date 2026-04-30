# Macro Pulse - Architecture

## System Overview

```text
GitHub Actions schedule
  -> docker run macro-pulse:daily
  -> src/main.py
  -> market data + screenshots
  -> reporting/generator.py
  -> delivery/notifier.py
  -> GitHub Pages + Telegram delivery
```

Current schedule:

- KR mode: weekdays 08:00 UTC (= 17:00 KST)
- US mode: weekdays 21:30 UTC (= 06:30 KST next day)

## Main modules

| Path | Role |
|---|---|
| `src/macro_pulse/app/cli.py` | Entry point, mode resolution, pipeline orchestration |
| `data/market_data.py` | Yahoo Finance + CNBC collection |
| `data/providers/telegram_channel.py` | Telethon image fetcher for `@yakjangsu` |
| `reporting/generator.py` | HTML report and Telegram text generation |
| `reporting/screenshots.py` | Screenshot handlers |
| `delivery/notifier.py` | Telegram Bot API delivery |
| `config/report_formats.py` | Loads `config/report_formats.json` |
| `src/macro_pulse/workflows/schedule_sync.py` | Keeps workflow schedule aligned with config |

## Schedule ownership

This repository is owned by **GitHub Actions** for scheduled execution.

Source of truth:

- `config/report_formats.json`
- `.github/workflows/daily_report.yml`
- `src/macro_pulse/workflows/schedule_sync.py`

## Separation from trading-bot-seoul

`imgjun/GCP_trading-bot-seoul` is a separate repo with a different execution
owner:

- runtime owner: GCP VM cron
- host path: `/home/patrick.jang/trading-bot-seoul`

Do not merge the two execution models.

## Runtime secrets

Scheduled runs require these GitHub repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

If the shared Telegram token is rotated, update both:

- `Macro-Pulse` GitHub repository secrets
- `trading-bot-seoul` GCP `.env`
