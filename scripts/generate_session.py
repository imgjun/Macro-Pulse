"""
Generate a Telethon StringSession for use with Macro-Pulse.

Run this ONCE on any machine where you can receive an SMS/Telegram code:

    uv run python scripts/generate_session.py

Then paste the printed SESSION_STRING into your .env file as:

    TELEGRAM_SESSION_STRING=<the string>

The session string encodes a persistent login so the bot can run
headlessly on GCP without needing to re-authenticate.

Prerequisites:
  - Go to https://my.telegram.org and create an application
  - Set TELEGRAM_API_ID and TELEGRAM_API_HASH in your environment or .env
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


async def main():
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError:
        print("ERROR: telethon is not installed. Run: uv add telethon")
        return

    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        print(
            "ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set.\n"
            "Get them at https://my.telegram.org > API development tools"
        )
        return

    print("Generating Telethon session string...")
    print("You will be asked for your phone number and a login code.\n")

    async with TelegramClient(StringSession(), int(api_id), api_hash) as client:
        session_string = client.session.save()

    print("\n" + "=" * 60)
    print("SESSION STRING (copy this entire value into your .env):")
    print("=" * 60)
    print(f"TELEGRAM_SESSION_STRING={session_string}")
    print("=" * 60)
    print("\nKeep this secret — it provides full access to your Telegram account.")


if __name__ == "__main__":
    asyncio.run(main())
