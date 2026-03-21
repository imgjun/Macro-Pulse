**Language:** [한국어](../README.md) | **English**

# Macro Pulse Bot

Macro Pulse Bot is an automation project that collects market data and turns it into a simple daily report.

- It gathers market data.
- It creates an HTML report.
- It can send the result to Telegram or email.
- It can run automatically with GitHub Actions.

If you are not familiar with finance, the easiest way to think about it is: "a bot that collects important market numbers and summarizes them."

## What does it do?

- Builds a report for either the Korean market (`KR`) or US market (`US`)
- Collects indices, FX, bond yields, commodities, and crypto data
- Creates both a short Telegram summary and a full HTML report
- Optionally attaches screenshots for quick visual context
  - `KR`: KOSPI / KOSDAQ heatmaps
  - `US`: Finviz market map

## How does it work?

The flow is simple.

1. Fetch data from Yahoo Finance, Frankfurter, and CNBC.
2. Clean up and organize the data.
3. Create an HTML report and Telegram summary text.
4. Optionally send the result by Telegram or email.

The real entry point is [`src/main.py`](../src/main.py).

## What data is included?

- Korean indices: `KOSPI`, `KOSDAQ`
- Overseas indices: `S&P 500`, `Nasdaq`, `Nikkei 225`, and more
- Rates and commodities: `US 10Y Treasury`, `Gold`, `Silver`, `Copper`
- FX: `USD/KRW`, `JPY/KRW`, `EUR/KRW`, `CNY/KRW`
- Crypto: `Bitcoin`, `Ethereum`
- Volatility: `VIX`, `VKOSPI`

## Quick Start

### 1. Install

```bash
python3 -m pip install -r requirements.txt
```

### 2. Prepare `.env`

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

### 3. Generate only the report

```bash
python3 src/main.py --dry-run
```

This creates `macro_pulse_report.html`.

### 4. Run the full flow

```bash
python3 src/main.py
```

### 5. Choose the market mode manually

```bash
python3 src/main.py --market KR
python3 src/main.py --market US
```

- `KR`: Korean market mode
- `US`: US market mode
- If you omit the option, the app auto-selects based on current UTC time

## Run with Docker

If you want a local environment closer to GitHub Actions, you can use Docker.

```bash
docker build -t macro-pulse .
docker run --rm --env-file .env -v "$PWD:/app" -w /app macro-pulse python src/main.py --dry-run
```

## Run automatically with GitHub Actions

This repository already includes GitHub Actions workflows.

- Run the report on a schedule
- Publish the latest report to GitHub Pages
- Upload logs and outputs as artifacts
- Send a Telegram alert when a workflow fails

If you need the required secrets, see [`SECRETS.md`](SECRETS.md).

## Want to change the report format?

You can edit [`config/report_formats.json`](../config/report_formats.json).

That file controls:

- which sections appear first
- which items are included
- which screenshots are attached

You do not need deep Python knowledge for simple ordering changes.

## Testing

Basic tests:

```bash
python3 -m unittest discover tests
```

Live smoke tests against external services:

```bash
RUN_LIVE_SMOKE_TESTS=1 python3 -m unittest discover tests
```

Screenshot smoke tests:

```bash
RUN_SCREENSHOT_SMOKE_TESTS=1 python3 -m unittest tests.test_screenshot
```

## Screenshot Examples

### US Close Example

![US close report example](../imgs/us.png)

### Korea Close Example

![Korea close report example](../imgs/kr.png)

## Useful Files

- [`src/main.py`](../src/main.py): app entry point
- [`src/data_fetcher.py`](../src/data_fetcher.py): data collection
- [`src/report_generator.py`](../src/report_generator.py): report creation
- [`src/notifier.py`](../src/notifier.py): Telegram/email delivery
- [`config/report_formats.json`](../config/report_formats.json): summary format settings

## Troubleshooting

- If screenshots fail, check your Chrome/Chromium setup first.
- If Telegram messages do not arrive, re-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- If some numbers are missing, an external data source may have failed.
- If GitHub Pages does not update, check the `gh-pages` settings.
