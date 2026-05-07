**Language:** **한국어** | [English](SECRETS.en.md)

# Secrets 메모

현재 저장소의 GitHub Actions는 **CI 전용**이라, 기본 테스트만으로는 필수 repository secret이 없습니다.

## 로컬/운영 실행 시 필요한 값

### Telegram 전송
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Telegram 읽기 (yakjangsu / Telethon)
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

## 주의

- `TELEGRAM_SESSION_STRING`은 봇 토큰이 아니라 Telethon StringSession이어야 합니다.
- `.env`는 커밋하지 마세요.
- 향후 GitHub Actions에서 Telegram 연동 workflow를 다시 추가하면, 그때 repository secrets를 다시 정의하면 됩니다.
