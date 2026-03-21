**Language:** [한국어](../README.md) | **English**

# Macro Pulse Bot

Macro Pulse Bot collects major macroeconomic indicators, builds an HTML report, and delivers it through Telegram and email. By default it automatically selects either `KR` or `US` mode based on the current UTC time, and it can run on a schedule through GitHub Actions.

## Features

- Combines Yahoo Finance, Frankfurter, and CNBC data sources.
- Generates an HTML report with daily changes and recent trend history.
- Sends KOSPI/KOSDAQ heatmap screenshots in `KR` mode and a Finviz heatmap screenshot in `US` mode.
- Supports Telegram delivery and optional SMTP email delivery.
- Uses typed dataclass models and centralized logging across the pipeline.
- Aligns local and CI runtime with a shared Docker image.
- Can publish the latest report to GitHub Pages after scheduled runs, upload artifacts, and send failure notifications.

## Covered Data

- Domestic indices: `KOSPI`, `KOSDAQ`
- Overseas indices: `S&P 500`, `Nasdaq`, `Euro Stoxx 50`, `Nikkei 225`, `Hang Seng`, `Shanghai Composite`
- Commodities and rates: `Gold`, `Silver`, `Copper`, `US 10Y Treasury`, `Japan 10Y Treasury`, `Korea 10Y Treasury`
- FX: `USD/KRW`, `JPY/KRW`, `EUR/KRW`, `CNY/KRW`
- Crypto: `Bitcoin`, `Ethereum`
- Volatility: `VIX`, `VKOSPI`

## How It Works

1. `src/data_fetcher.py` pulls market data from Yahoo Finance, Frankfurter, and CNBC.
2. The fetched payload is normalized into dataclass models before rendering.
3. `src/report_generator.py` builds the HTML report and Telegram summary text without mutating the original input data.
4. `src/main.py` writes the result to `macro_pulse_report.html`.
5. Unless `--dry-run` is used, it creates temporary screenshots for the active market mode, uses them for delivery, and removes them afterward.

## Requirements

- Telegram bot token and chat ID for Telegram delivery
- GitHub Actions, Secrets, and Pages configuration

## Report Format Rules

Telegram summary formats and screenshot composition are managed in [`../config/report_formats.json`](../config/report_formats.json).

- `KR` close format: shows Korean indices first, followed by Asian indices, volatility, Japan/Korea government bonds, and FX.
- `KR` close screenshots: attaches two heatmaps for `KOSPI` and `KOSDAQ`.
- `US` close format: shows US and European indices first, followed by volatility, US Treasuries and commodities, FX, and crypto.
- `US` close screenshots: attaches one `Finviz` map image.
- How to customize: update `summary_sections` to change section titles, categories, and item ordering, and update `screenshot_targets` to change which screenshots are attached.
- GitHub Actions reference: workflows load the same config file through `REPORT_FORMAT_CONFIG=config/report_formats.json`.

## Screenshot Examples

### US Close Example

![US close report example](../imgs/us.png)

### Korea Close Example

![Korea close report example](../imgs/kr.png)

## Output Files

- `macro_pulse_report.html`: main HTML report
- `public/index.html`: report file for GitHub Pages deployment
- `macro-pulse.log`, `unit-test.log`: workflow logs uploaded as GitHub Actions artifacts
- Screenshot PNGs: created only as temporary files for Telegram delivery and not stored in the repository root

## GitHub Actions

The main workflow is defined in `.github/workflows/daily_report.yml`.

- `.github/workflows/ci.yml`: runs unit tests in Docker for pushes and pull requests
- Tuesday to Saturday, 06:30 KST: run the US close report
- Monday to Friday, 17:00 KST: run the Korea close report
- Manual trigger: `workflow_dispatch`
- Format config path: `REPORT_FORMAT_CONFIG=config/report_formats.json`
- Scheduled/manual workflows build one Docker image and use it for both tests and the actual app run.
- Generated reports and run logs are uploaded as artifacts.
- If Telegram secrets are configured, failures trigger a Telegram alert with the run URL.

The companion workflow `.github/workflows/test_telegram.yml` can manually send a Telegram test run in either `KR` or `US` mode.

## GitHub Secrets

To use GitHub Actions, add the following values in `Settings > Secrets and variables > Actions`.

You can find a short reference in [SECRETS.md](SECRETS.md).

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SMTP_USERNAME` (optional)
- `SMTP_PASSWORD` (optional)
- `RECIPIENT_EMAIL` (optional)

## GitHub Pages

To view the latest report on the web, enable GitHub Pages.

1. Open `Settings > Pages`.
2. Set the deployment branch to `gh-pages`.
3. After deployment, the report is available at `https://<your-username>.github.io/Macro-Pulse/`.

## Local Installation

```bash
# Python 3.12 or newer
python3 -m pip install -r requirements.txt
```

Docker-based setup:

```bash
docker build -t macro-pulse .
```

## Environment Variables

Create a `.env` file in the project root.

```ini
# Telegram Config
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Config (optional)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient_email@example.com
```

- If `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` is missing, Telegram delivery is skipped.
- If `SMTP_USERNAME` or `SMTP_PASSWORD` is missing, email delivery is skipped.
- If `RECIPIENT_EMAIL` is empty, the report is sent to `SMTP_USERNAME`.

## Local Usage

Generate only the report:

```bash
python3 src/main.py --dry-run
```

Run and send notifications:

```bash
python3 src/main.py
```

Force a market mode:

```bash
python3 src/main.py --market KR
python3 src/main.py --market US
```

- `--market KR`: Korean market summary with KOSPI/KOSDAQ screenshots
- `--market US`: US market summary with Finviz screenshot
- `--market Global` or omitting the option: auto-selects `KR` or `US` from the current UTC time

Run the same dry-run flow in Docker:

```bash
docker run --rm \
  --env-file .env \
  -v "$PWD:/app" \
  -w /app \
  macro-pulse \
  python src/main.py --dry-run
```

## Testing

Run the standard test suite:

```bash
python3 -m unittest discover tests
```

Run live smoke tests:

```bash
RUN_LIVE_SMOKE_TESTS=1 python3 -m unittest discover tests
```

Run screenshot smoke tests:

```bash
RUN_SCREENSHOT_SMOKE_TESTS=1 python3 -m unittest tests.test_screenshot
```

`RUN_LIVE_SMOKE_TESTS=1` hits external services directly, so results depend on network and provider availability.

## Troubleshooting

- Screenshot failures: verify Chrome/Chromium availability and outbound access to the target sites.
- Missing Telegram messages: check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Email failures: Gmail SMTP requires an app password.
- Missing market data: Yahoo Finance, Frankfurter, or CNBC failures can leave some fields empty.
- Pages not updating: confirm `gh-pages` is selected as the Pages source branch.

## Project Structure

```text
.
|-- src/
|   |-- main.py
|   |-- data_fetcher.py
|   |-- frankfurter_fetcher.py
|   |-- cnbc_fetcher.py
|   |-- models.py
|   |-- logging_utils.py
|   |-- report_generator.py
|   |-- report_format_config.py
|   |-- artifact_utils.py
|   |-- notifier.py
|   |-- screenshot_utils.py
|   `-- templates/report.html
|-- tests/
|-- config/
|-- docs/
|   |-- README.en.md
|   `-- SECRETS.md
|-- imgs/
|-- .github/workflows/
|-- Dockerfile
|-- .dockerignore
|-- .env-sample
`-- README.md
```
