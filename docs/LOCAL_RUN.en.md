**Language:** [한국어](LOCAL_RUN.md) | **English**

# Local Run Guide

This document explains how to validate Macro Pulse Bot locally.

## 1. Install dependencies

```bash
uv python install
uv sync --all-groups
```

## 2. Prepare `.env`

Create `.env` in the project root:

```ini
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SESSION_STRING=...
```

Meaning:
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: final delivery
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION_STRING`: reading `@yakjangsu`

Generate the Telethon session with:

```bash
uv run python scripts/generate_session.py
```

## 3. Recommended validation order

### US dry run

```bash
uv run python src/main.py --dry-run --market US
```

### KR dry run

```bash
uv run python src/main.py --dry-run --market KR
```

### Full run including Telegram send

```bash
uv run python src/main.py --market US
uv run python src/main.py --market KR
```

### Windows scheduler wrapper script

```powershell
powershell -ExecutionPolicy Bypass -File .\\scripts\\run_macro_pulse_windows.ps1 -Market US
powershell -ExecutionPolicy Bypass -File .\\scripts\\run_macro_pulse_windows.ps1 -Market KR
```

Currently verified Windows Task Scheduler jobs:
- `Macro-Pulse-US`: when the Windows host timezone is `India Standard Time (IST)`, the task uses two triggers at `Tue-Sat 01:35` and `02:35`
  - the script itself checks the current `America/New_York` time and only proceeds during the regular US market-close hour (`16:00 ET`)
  - this avoids seasonal breakage across EDT/EST transitions
- `Macro-Pulse-KR`: `Mon-Fri 16:30 IST`

Logs:
- `logs/windows-scheduler/*.log`

## 4. Standalone yakjangsu fetch check

```bash
PYTHONPATH=src uv run python - <<'PY'
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))
import asyncio
from macro_pulse.reporting.screenshots import capture_screenshots

async def main():
    paths = await capture_screenshots(['yakjangsu'])
    print({'count': len(paths), 'files': paths})

asyncio.run(main())
PY
```

A healthy run should download the latest full batch.

## 5. Docker

### Build

```bash
docker build -t macro-pulse .
```

### Dry run

```bash
docker run --rm \
  --env-file .env \
  -v "$PWD:/app" \
  -w /app \
  macro-pulse \
  uv run --frozen python src/main.py --dry-run --market US
```

## 6. Output files

- `macro_pulse_report.html`: generated HTML report
- Telegram attachment images: created in a temp directory and then cleaned up

## 7. Troubleshooting

- `No recent photo messages found`:
  - check the latest channel post time
  - check `MAX_POST_AGE_HOURS`
- `BotMethodInvalidError`:
  - happens when trying to read channel history with a bot session
- `You must use "async with" if the event loop is running`:
  - happens when a sync Telethon client is used in the async path
- On Windows, `.venv/lib64` access issues usually mean a WSL-created virtualenv was reused accidentally.
