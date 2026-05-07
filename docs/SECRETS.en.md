**Language:** [한국어](SECRETS.md) | **English**

# Secrets Notes

GitHub Actions in this repository is now **CI only**, so the default test workflow does not require repository secrets.

## Values needed for local or operational runs

### Telegram sending
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Telegram reading (`@yakjangsu` / Telethon)
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

## Notes

- `TELEGRAM_SESSION_STRING` must be a Telethon StringSession, not a bot token.
- Never commit `.env`.
- If Telegram-enabled GitHub workflows are added back later, define repository secrets at that time.
