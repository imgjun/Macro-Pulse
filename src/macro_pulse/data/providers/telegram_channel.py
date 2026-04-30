"""
Telegram channel image fetcher using Telethon (MTProto client).

Connects to a Telegram channel (default: t.me/yakjangsu) and downloads
the 5 market chart images from the most recent posting batch.

Required environment variables:
    TELEGRAM_API_ID          - Your Telegram App API ID (from my.telegram.org)
    TELEGRAM_API_HASH        - Your Telegram App API Hash
    TELEGRAM_SESSION_STRING  - Base64 StringSession (generate via scripts/generate_session.py)

The yakjangsu channel posts a batch of market images shortly after US market
close (~05:00-05:30 KST). This module finds the most recent photo batch and
selects up to IMAGE_LIMIT images from it.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ...core.logging import get_logger

logger = get_logger(__name__)

# Target channel username (without @)
DEFAULT_CHANNEL = "yakjangsu"

# How many images to select from the latest batch
IMAGE_LIMIT = 5

# Max age of post to consider "today's" batch (hours)
MAX_POST_AGE_HOURS = 12

# How close together messages must be (seconds) to be considered a "batch"
BATCH_WINDOW_SECONDS = 300  # 5 minutes


def fetch_yakjangsu_images(
    output_dir: str | Path | None = None,
    channel: str = DEFAULT_CHANNEL,
    limit: int = IMAGE_LIMIT,
) -> list[str]:
    """
    Fetch the latest batch of market chart images from the target Telegram channel.

    Returns a list of local file paths for the downloaded images.
    Returns an empty list if Telethon is unavailable or credentials are missing.
    """
    try:
        from telethon.sync import TelegramClient  # noqa: PLC0415
        from telethon.sessions import StringSession  # noqa: PLC0415
    except ImportError:
        logger.warning(
            "telethon is not installed. Run: uv add telethon  "
            "or pip install telethon"
        )
        return []

    api_id = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    session_string = os.environ.get("TELEGRAM_SESSION_STRING")

    if not all([api_id, api_hash, session_string]):
        logger.warning(
            "Telegram MTProto credentials not set. "
            "Define TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_SESSION_STRING "
            "in your .env file."
        )
        return []

    out_dir = (
        Path(output_dir)
        if output_dir
        else Path(tempfile.mkdtemp(prefix="macro_pulse_tg_"))
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[str] = []

    try:
        with TelegramClient(
            StringSession(session_string), int(api_id), api_hash
        ) as client:
            logger.info("Fetching images from @%s ...", channel)
            messages = _fetch_recent_photo_messages(client, channel)

            if not messages:
                logger.warning("No recent photo messages found in @%s", channel)
                return []

            batch = _select_latest_batch(messages)
            logger.info(
                "Found batch of %d photo messages; downloading up to %d",
                len(batch),
                limit,
            )

            for i, msg in enumerate(batch[:limit]):
                dest = out_dir / f"yakjangsu_{i + 1:02d}.jpg"
                client.download_media(msg, file=str(dest))
                if dest.exists():
                    downloaded.append(str(dest))
                    logger.info("Downloaded: %s", dest.name)
                else:
                    logger.warning(
                        "Download produced no file for message id=%s", msg.id
                    )

    except Exception as exc:
        logger.exception(
            "Failed to fetch images from Telegram channel @%s: %s", channel, exc
        )
        return []

    logger.info(
        "Fetched %d/%d images from @%s", len(downloaded), limit, channel
    )
    return downloaded


def _fetch_recent_photo_messages(client, channel: str, fetch_count: int = 50):
    """Fetch recent messages that contain photos from the channel."""
    from telethon.tl.types import MessageMediaPhoto  # noqa: PLC0415

    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_POST_AGE_HOURS)
    photo_messages = []

    for msg in client.iter_messages(channel, limit=fetch_count):
        if msg.date.replace(tzinfo=timezone.utc) < cutoff:
            break
        if msg.media and isinstance(msg.media, MessageMediaPhoto):
            photo_messages.append(msg)

    return photo_messages


def _select_latest_batch(messages: list) -> list:
    """
    From a list of photo messages (newest first), select the most recent
    contiguous batch: messages posted within BATCH_WINDOW_SECONDS of
    the newest message.

    Returns messages in chronological order (oldest first = natural posting order).
    """
    if not messages:
        return []

    newest_date = messages[0].date
    batch = []

    for msg in messages:
        age_diff = abs((newest_date - msg.date).total_seconds())
        if age_diff <= BATCH_WINDOW_SECONDS:
            batch.append(msg)
        else:
            # Once outside the window, stop collecting
            break

    # Reverse so images are in original posting order
    return list(reversed(batch))
