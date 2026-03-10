import argparse
import asyncio
import os
import warnings
from datetime import datetime, timezone

from data_fetcher import fetch_all_data
from dotenv import load_dotenv
from notifier import send_email_report, send_telegram_report
from report_format_config import get_screenshot_targets, load_report_format_config
from report_generator import generate_html_report, generate_telegram_summary
from screenshot_utils import (
    take_finviz_screenshot,
    take_kosdaq_screenshot,
    take_kospi_screenshot,
)

# Load .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")


SCREENSHOT_HANDLERS = {
    "finviz": take_finviz_screenshot,
    "kospi": take_kospi_screenshot,
    "kosdaq": take_kosdaq_screenshot,
}


def resolve_mode(market_arg, now_utc=None):
    normalized = (market_arg or "").strip().upper()
    if normalized in {"KR", "US"}:
        return normalized

    current_time = now_utc or datetime.now(timezone.utc)
    hour = current_time.hour
    return "KR" if 7 <= hour < 20 else "US"


async def main():
    parser = argparse.ArgumentParser(description="Macro Pulse Bot")
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate report but do not send"
    )
    parser.add_argument(
        "--market",
        type=str,
        default="Global",
        help="Market context override (KR/US). Global uses time-based auto mode.",
    )
    args = parser.parse_args()

    mode = resolve_mode(args.market)
    report_format_config = load_report_format_config()

    print(f"Starting Macro Pulse Bot (Mode: {mode})...")

    print("Fetching data...")
    data = fetch_all_data()

    print("Generating report...")
    html_report = generate_html_report(data)

    telegram_summary = generate_telegram_summary(data, mode, report_format_config)
    print(f"Telegram Summary ({mode}):\n{telegram_summary}\n")

    output_path = "macro_pulse_report.html"
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(html_report)
    print(f"Report saved to {output_path}")

    if args.dry_run:
        print("Dry run complete. No notifications sent.")
        return

    screenshot_paths = []
    screenshot_targets = get_screenshot_targets(mode, report_format_config)
    if screenshot_targets:
        print(f"Taking screenshots for targets: {', '.join(screenshot_targets)}")

    for target in screenshot_targets:
        take_screenshot = SCREENSHOT_HANDLERS.get(target)
        if not take_screenshot:
            print(f"Unknown screenshot target in config: {target}")
            continue

        screenshot_path = take_screenshot()
        if screenshot_path:
            screenshot_paths.append(screenshot_path)

    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient_email = os.environ.get("RECIPIENT_EMAIL")

    if telegram_token and telegram_chat_id:
        await send_telegram_report(
            telegram_token,
            telegram_chat_id,
            telegram_summary,
            image_paths=screenshot_paths,
        )

    if smtp_user and smtp_password:
        target_email = recipient_email if recipient_email else smtp_user
        send_email_report(smtp_user, smtp_password, target_email, html_report)


if __name__ == "__main__":
    asyncio.run(main())
