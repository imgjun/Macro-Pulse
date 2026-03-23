**Language:** [한국어](SECRETS.md) | **English**

# GitHub Secrets

To run Macro Pulse Bot correctly through GitHub Actions, add the following repository secrets.

The workflows run inside a runtime image built from `uv.lock`.

Path:
`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`

## Required

### Telegram

- `TELEGRAM_BOT_TOKEN`: the token from BotFather for your Telegram bot
- `TELEGRAM_CHAT_ID`: the chat or channel ID that should receive the report

## Notes

- Secret names must match exactly.
