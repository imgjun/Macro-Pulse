import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram import Bot


async def send_telegram_report(
    token,
    chat_id,
    message_text="Daily Macro Pulse Report",
    image_path=None,
):
    """
    Sends the report to Telegram.
    Can send a message and/or an image.
    """
    if not token or not chat_id:
        print("Telegram token or chat_id missing. Skipping Telegram.")
        return

    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message_text)

        # Send image if available
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img:
                await bot.send_photo(chat_id=chat_id, photo=img)
                print(f"Telegram photo sent: {image_path}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def send_email_report(smtp_user, smtp_password, recipient_email, html_content):
    """
    Sends the report via Email.
    """
    if not smtp_user or not smtp_password or not recipient_email:
        print("SMTP credentials or recipient email missing. Skipping Email.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Daily Macro Pulse Report"
        msg["From"] = smtp_user
        msg["To"] = recipient_email

        part1 = MIMEText(html_content, "html")
        msg.attach(part1)

        # Standard Gmail SMTP port 587
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()
        print("Email report sent.")
    except Exception as e:
        print(f"Failed to send Email: {e}")
