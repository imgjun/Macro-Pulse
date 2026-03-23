import os
from asyncio import sleep

from telegram import Bot

from ..core.logging import get_logger


logger = get_logger(__name__)


async def send_telegram_report(
    token,
    chat_id,
    message_text="Daily Macro Pulse Report",
    image_path=None,
    image_paths=None,
    attempts=2,
):
    if not token or not chat_id:
        logger.info("Telegram token or chat_id missing. Skipping Telegram.")
        return False

    photo_paths = list(image_paths or [])
    if image_path and not photo_paths:
        photo_paths.append(image_path)

    for attempt in range(1, attempts + 1):
        try:
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=message_text)

            for photo_path in photo_paths:
                if photo_path and os.path.exists(photo_path):
                    with open(photo_path, "rb") as image_handle:
                        await bot.send_photo(chat_id=chat_id, photo=image_handle)
                    logger.info("Telegram photo sent: %s", photo_path)

            return True
        except Exception as exc:
            logger.warning(
                "Failed to send Telegram message (attempt %s/%s): %s",
                attempt,
                attempts,
                exc,
            )
            if attempt == attempts:
                logger.exception("Telegram delivery failed after retries")
                return False
            await sleep(1)
