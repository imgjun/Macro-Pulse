**Language:** [한국어](../README.md) | **English**

# Macro Pulse Bot

Macro Pulse Bot collects market data after the Korea or US market close and builds:
- a Telegram summary
- an HTML report
- optional visual attachments

## Current operating status

- **US image source:** `@yakjangsu`
- **US fetch method:** Telethon MTProto user session
- **US default behavior:** download the **full latest image batch**
- **KR image source:** Selenium captures for KOSPI / KOSDAQ heatmaps
- **GitHub Actions:** **CI only**
- **GitHub Pages / manual report workflows:** removed during cleanup
- **GCP crontab:** last verified state showed **no active Macro-Pulse entries**
- **Active scheduler:** Windows Task Scheduler (`Macro-Pulse-US`, `Macro-Pulse-KR`)
- **Windows host timezone:** last verified as `India Standard Time (IST)`
- **US scheduler mode:** dual triggers at `Tue-Sat 01:35` and `02:35` IST, with an in-script guard that only runs during the actual US regular-close hour (`16:00 ET`)
- **KR scheduler mode:** `Mon-Fri 16:30 IST`
- **Preferred validation environment right now:** local Windows / WSL

This means the repository is currently operated through the local Windows scheduler, with GitHub Actions kept only for CI.

## Features

- `KR` and `US` market modes
- Yahoo Finance / CNBC market data collection
- HTML report generation
- Telegram summary generation and delivery
- Visual attachments
  - `KR`: KOSPI / KOSDAQ heatmaps
  - `US`: latest full `@yakjangsu` image batch

## Execution flow

```text
src/main.py
  -> market_data.fetch_all_data()
  -> reporting.generator
  -> reporting.screenshots.capture_screenshots()
     - KR: Selenium heatmaps
     - US: Telethon fetch from @yakjangsu
  -> delivery.notifier.send_telegram_report()
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for more detail.

## US image fetch behavior

For US close reports, the bot reads the latest photo batch from `@yakjangsu`.

Current behavior:
- authenticate with a Telethon **user** session
- inspect recent channel history
- find the latest photo batch within `BATCH_WINDOW_SECONDS = 300`
- preserve the original posting order
- download the **entire latest batch** by default
- use a default age filter of **24 hours**

## Environment variables

### Telegram sending
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Telegram reading via MTProto
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

Generate the session with:

```bash
uv run python scripts/generate_session.py
```

`TELEGRAM_SESSION_STRING` must be a Telethon StringSession, not a bot token.

## Local run

See [`LOCAL_RUN.en.md`](LOCAL_RUN.en.md) for the full guide.

Quick examples:

```bash
uv sync --all-groups
uv run python src/main.py --dry-run --market US
uv run python src/main.py --market KR
```

## Testing

Basic tests:

```bash
uv run python -m unittest discover tests
```

Important regression tests:

```bash
uv run python -m unittest tests.test_main -v
uv run python -m unittest tests.test_report_format_config -v
```

Smoke tests:

```bash
RUN_SCREENSHOT_SMOKE_TESTS=1 uv run python -m unittest tests.test_screenshot
RUN_LIVE_SMOKE_TESTS=1 uv run python -m unittest discover tests
```

## GitHub Actions

The repository now keeps only **CI** in GitHub Actions.

Kept:
- test runs on `push` and `pull_request`
- CI log artifact upload

Removed:
- GitHub report workflows
- GitHub Pages deployment workflow
- keepalive workflow

## Useful files

- [`../src/main.py`](../src/main.py): asyncio entry point
- [`../src/macro_pulse/app/cli.py`](../src/macro_pulse/app/cli.py): main orchestration
- [`../src/macro_pulse/data/providers/telegram_channel.py`](../src/macro_pulse/data/providers/telegram_channel.py): yakjangsu fetcher
- [`../src/macro_pulse/reporting/screenshots.py`](../src/macro_pulse/reporting/screenshots.py): screenshot handlers
- [`../src/macro_pulse/delivery/notifier.py`](../src/macro_pulse/delivery/notifier.py): Telegram delivery
- [`../config/report_formats.json`](../config/report_formats.json): report format metadata

## Troubleshooting

- `No recent photo messages found` usually means the age filter and the channel post time do not match.
- `TELEGRAM_SESSION_STRING` must resolve to a user session, not a bot session.
- `async with` Telethon errors usually mean a sync client path was reintroduced into the async flow.
