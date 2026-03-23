**Language:** [한국어](LOCAL_RUN.md) | **English**

# Local / Docker Run Guide

This document explains how to run Macro Pulse Bot on your own machine.

## 1. uv

### Install

```bash
uv python install
uv sync --all-groups
```

- This repository manages dependencies with [`pyproject.toml`](../pyproject.toml) and [`uv.lock`](../uv.lock).
- The default Python version is pinned in [`.python-version`](../.python-version).

### Prepare `.env`

Create a `.env` file in the project root.

```ini
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient_email@example.com
```

- If Telegram values are missing, Telegram delivery is skipped.
- If email values are missing, email delivery is skipped.

### Generate only the report

```bash
uv run python src/main.py --dry-run
```

This creates `macro_pulse_report.html`.

### Run the full flow

```bash
uv run python src/main.py
```

### Choose the market mode manually

```bash
uv run python src/main.py --market KR
uv run python src/main.py --market US
```

- `KR`: Korean market mode
- `US`: US market mode
- If you omit the option, the app auto-selects from current UTC time.

## 2. Docker

### Build the image

```bash
docker build -t macro-pulse .
```

### Run a dry run

```bash
docker run --rm \
  --env-file .env \
  -v "$PWD:/app" \
  -w /app \
  macro-pulse \
  uv run --frozen python src/main.py --dry-run
```

### Run the full flow

```bash
docker run --rm \
  --env-file .env \
  -v "$PWD:/app" \
  -w /app \
  macro-pulse \
  uv run --frozen python src/main.py
```

## 3. Output Files

- `macro_pulse_report.html`: generated HTML report
- Screenshot PNGs: temporary files used only for delivery

## 4. Troubleshooting

- If screenshots fail, check your Chrome/Chromium setup.
- If Telegram messages do not arrive, re-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- If some data is missing, an external data source may have failed.
