import os
import sys
import unittest
from unittest.mock import AsyncMock, patch


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from macro_pulse.delivery.notifier import send_telegram_report


class NotifierTests(unittest.IsolatedAsyncioTestCase):
    async def test_send_telegram_report_sends_message_and_images(self):
        with (
            patch("macro_pulse.delivery.notifier.Bot") as bot_cls,
            patch("macro_pulse.delivery.notifier.os.path.exists", return_value=True),
            patch("builtins.open", unittest.mock.mock_open(read_data=b"image")),
        ):
            bot = AsyncMock()
            bot_cls.return_value = bot

            result = await send_telegram_report(
                "token",
                "chat-id",
                "hello",
                image_paths=["sample.png"],
                attempts=1,
            )

        self.assertTrue(result)
        bot.send_message.assert_awaited_once_with(chat_id="chat-id", text="hello")
        bot.send_photo.assert_awaited_once()
