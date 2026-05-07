# Macro Pulse - Architecture

## Current system overview

```text
Local / WSL execution (currently preferred for validation)
    |
    +-- src/main.py (asyncio entry point)
          |
          +-- market_data.fetch_all_data()
          |     +-- Yahoo Finance
          |     +-- CNBC
          |
          +-- reporting.generator
          |     +-- HTML report
          |     +-- Telegram text summary
          |
          +-- reporting.screenshots.capture_screenshots()
          |     +-- KR -> Selenium heatmaps
          |     +-- US -> Telethon fetch from @yakjangsu
          |
          +-- delivery.notifier.send_telegram_report()
                +-- Telegram Bot API: sendMessage + sendPhoto
```

## Scheduler status

Scheduler truth must be verified separately from repository docs.

Current known status:
- GitHub Actions scheduled/report workflows were removed
- Only CI remains in `.github/workflows/ci.yml`
- Last verified GCP state had no active Macro-Pulse crontab entries
- Windows Task Scheduler is the active production scheduler
- Windows host timezone was last verified as `India Standard Time (IST)`
- `Macro-Pulse-US` uses dual `Tue-Sat 01:35` / `02:35` IST triggers plus an in-script ET close-window guard
- `Macro-Pulse-KR` uses `Mon-Fri 12:05 IST`

## Main modules

| Path | Role |
|------|------|
| `src/main.py` | asyncio entry point |
| `src/macro_pulse/app/cli.py` | orchestrates mode resolution, data fetch, screenshots, report generation, delivery |
| `src/macro_pulse/data/market_data.py` | bulk market data collection |
| `src/macro_pulse/data/providers/telegram_channel.py` | async Telethon fetcher for `@yakjangsu` |
| `src/macro_pulse/reporting/screenshots.py` | screenshot handlers for KR and US modes |
| `src/macro_pulse/reporting/generator.py` | HTML report + Telegram summary generation |
| `src/macro_pulse/delivery/notifier.py` | Telegram Bot API sender |
| `config/report_formats.json` | report format metadata per mode |

## `@yakjangsu` image fetch flow

```text
Telethon (MTProto user session)
    |
    +-- authenticate via StringSession
    +-- iterate recent channel history
    +-- filter photo messages within MAX_POST_AGE_HOURS
    +-- find latest photo batch within BATCH_WINDOW_SECONDS
    +-- preserve original posting order
    +-- download full latest batch to a temp directory
    +-- pass downloaded files to Telegram Bot API sender
    +-- cleanup temp files
```

### Important runtime settings

- `IMAGE_LIMIT = None` -> download the full latest batch
- `MAX_POST_AGE_HOURS = 24`
- `BATCH_WINDOW_SECONDS = 300`

## Telegram credentials split

### Sending
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Reading from `@yakjangsu`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

The read path requires a **user** MTProto session. A bot session is not sufficient for channel history reads used here.

## GitHub Actions

Only one workflow remains:
- `.github/workflows/ci.yml`

Its purpose is limited to:
- running tests on `push` / `pull_request`
- uploading CI logs as artifacts

## Notes for future changes

- If a scheduler is reintroduced, update docs and tests in the same commit.
- If GitHub Pages or Telegram-enabled workflows return, document required secrets again.
- Do not reintroduce `telethon.sync` into the async main path.
