**Language:** [한국어](README.md) | **English**

# Macro Pulse Bot

Macro Pulse Bot collects key macro market indicators, builds an HTML report, and delivers it through Telegram and email. By default it chooses the market context automatically based on the current UTC time and can be scheduled with GitHub Actions.

## Features

- Combines Yahoo Finance, Frankfurter, and CNBC data sources.
- Generates an HTML report with daily changes and recent trend history.
- Sends KOSPI/KOSDAQ heatmap screenshots in `KR` mode and a Finviz heatmap screenshot in `US` mode.
- Supports Telegram delivery and optional SMTP email delivery.
- Can publish the latest report to GitHub Pages after scheduled runs.

## Covered Data

- Domestic indices: `KOSPI`, `KOSDAQ`
- Overseas indices: `S&P 500`, `Nasdaq`, `Euro Stoxx 50`, `Nikkei 225`, `Hang Seng`, `Shanghai Composite`
- Commodities and rates: `Gold`, `Silver`, `Copper`, `US 10Y Treasury`, `Japan 10Y Treasury`, `Korea 10Y Treasury`
- FX: `USD/KRW`, `JPY/KRW`, `EUR/KRW`, `CNY/KRW`
- Crypto: `Bitcoin`, `Ethereum`
- Volatility: `VIX`, `VKOSPI`

## How It Works

1. `src/data_fetcher.py` pulls market data from Yahoo Finance, Frankfurter, and CNBC.
2. `src/report_generator.py` builds the HTML report and Telegram summary text.
3. `src/main.py` writes the result to `macro_pulse_report.html`.
4. Unless `--dry-run` is used, it captures screenshots for the active market mode and sends notifications.

## Requirements

- Python 3.12+
- Internet access
- Telegram bot token and chat ID
- Chrome or Chromium runtime for screenshots
- A GitHub repository with Actions/Pages enabled if you want automation

## Installation

```bash
pip install -r requirements.txt
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
python src/main.py --dry-run
```

Run and send notifications:

```bash
python src/main.py
```

Force a market mode:

```bash
python src/main.py --market KR
python src/main.py --market US
```

- `--market KR`: Korean market summary with KOSPI/KOSDAQ screenshots
- `--market US`: US market summary with Finviz screenshot
- `--market Global` or omitting the option: auto-selects `KR` or `US` from the current UTC time

## Report Format Rules

Telegram summary layout and screenshot composition are now managed in [config/report_formats.json](/home/lys74/DEV/Macro-Pulse/config/report_formats.json) instead of being hardcoded in the workflow or summary code.

- `KR` close format: domestic Korean indices first, then Asia indices, volatility, Japan/Korea government bonds, and FX.
- `KR` close screenshots: two heatmaps for `KOSPI` and `KOSDAQ`.
- `US` close format: US and European indices first, then volatility, US Treasury plus commodities, FX, and crypto.
- `US` close screenshots: one `Finviz` map image.
- How to customize: edit `summary_sections` to change section titles, categories, and item order, and edit `screenshot_targets` to change which images are attached.
- GitHub Actions reference: workflows load the same file through `REPORT_FORMAT_CONFIG=config/report_formats.json`.

## Output Files

- `macro_pulse_report.html`
- `finviz_map.png`
- `kospi_map.png`
- `kosdaq_map.png`
- `public/index.html`

## GitHub Actions

The main workflow is defined in `.github/workflows/daily_report.yml`.

- Tuesday to Saturday, 06:30 KST: run for the US close cycle
- Monday to Friday, 17:00 KST: run for the Korea close cycle
- Manual trigger is also enabled with `workflow_dispatch`
- Format config path: `REPORT_FORMAT_CONFIG=config/report_formats.json`

The companion workflow `.github/workflows/test_telegram.yml` can manually send a test run for either `KR` or `US`.

## GitHub Secrets

Add these repository secrets in `Settings > Secrets and variables > Actions`.

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SMTP_USERNAME` (optional)
- `SMTP_PASSWORD` (optional)
- `RECIPIENT_EMAIL` (optional)

## GitHub Pages

To publish the latest report on the web:

1. Open `Settings > Pages`.
2. Set the deployment branch to `gh-pages`.
3. After deployment, the report will be available at `https://<your-username>.github.io/Macro-Pulse/`.

## Testing

Run the standard test suite:

```bash
python -m unittest discover tests
```

Run live smoke tests:

```bash
RUN_LIVE_SMOKE_TESTS=1 python -m unittest discover tests
```

Run screenshot checks individually:

```bash
python tests/test_screenshot.py --target finviz
python tests/test_screenshot.py --target kospi
python tests/test_screenshot.py --target kosdaq
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
|   |-- report_generator.py
|   |-- notifier.py
|   `-- screenshot_utils.py
|-- tests/
|-- config/
|-- .github/workflows/
|-- .env-sample
|-- SECRETS.md
`-- README.md
```
