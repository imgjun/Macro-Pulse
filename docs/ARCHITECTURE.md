# Macro Pulse — Architecture

## 시스템 구성 (System Overview)

```
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Actions  (cron scheduler)                               │
│                                                                 │
│  KR mode: weekdays 08:00 UTC  (= 17:00 KST)                   │
│  US mode: weekdays 21:30 UTC  (= 06:30 KST next day)          │
└─────────────────────┬───────────────────────────────────────────┘
                      │  docker run macro-pulse:daily
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  src/main.py  (asyncio entry point)                             │
│                                                                 │
│  ┌──────────────┐    ┌────────────────────┐                    │
│  │ market_data  │    │  screenshots        │                    │
│  │ .fetch_all() │    │  .capture(targets)  │                    │
│  └──────┬───────┘    └────────┬───────────┘                    │
│         │                     │                                 │
│    ┌────┴─────────────────┐   │                                 │
│    │  Yahoo Finance (yf)  │   │  US mode → yakjangsu (Telethon) │
│    │  CNBC quote page     │   │  KR mode → hankyung.com (Selenium)│
│    └──────────────────────┘   │                                 │
│                               │                                 │
│  ┌────────────────────────────▼──────────────────────────────┐  │
│  │  reporting/generator.py                                    │  │
│  │   - generate_html_report()   → macro_pulse_report.html    │  │
│  │   - generate_telegram_summary() → text message            │  │
│  └─────────────────────────────────────────┬─────────────────┘  │
│                                            │                    │
│  ┌─────────────────────────────────────────▼─────────────────┐  │
│  │  delivery/notifier.py                                      │  │
│  │   - send_telegram_report(token, chat_id, text, images)    │  │
│  │     → Bot API: sendMessage + sendPhoto (×N)               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
   GitHub Pages              Telegram Channel
   (HTML report)             (text + 5 images)
```

## 주요 모듈

### `src/macro_pulse/`

| 경로 | 역할 |
|------|------|
| `app/cli.py` | argparse 진입점, 모드 결정, 전체 파이프라인 조율 |
| `data/market_data.py` | Yahoo Finance + CNBC에서 지표 일괄 수집 |
| `data/providers/cnbc.py` | CNBC quote page scraper |
| `data/providers/telegram_channel.py` | **[신규]** Telethon으로 @yakjangsu 이미지 수집 |
| `reporting/generator.py` | HTML 리포트 + Telegram 요약 텍스트 생성 |
| `reporting/screenshots.py` | 스크린샷 핸들러 (finviz / kospi / kosdaq / **yakjangsu**) |
| `delivery/notifier.py` | Telegram Bot API 전송 |
| `config/report_formats.py` | report_formats.json 로더 |
| `domain/models.py` | 데이터 모델 (Snapshot, ReportDataset 등) |

### `config/report_formats.json`

KR/US 모드별 텔레그램 요약 섹션 순서, 포함 항목, 스크린샷 타겟, cron 스케줄을 JSON으로 관리합니다.

```json
"US": {
  "screenshot_targets": ["yakjangsu"],   // Telethon으로 @yakjangsu 이미지 가져오기
  ...
}
"KR": {
  "screenshot_targets": ["kospi", "kosdaq"],  // Selenium으로 한경 히트맵 캡처
  ...
}
```

## @yakjangsu 이미지 수집 흐름

```
Telethon (MTProto)
    │
    ├─ StringSession으로 인증 (재로그인 불필요)
    │
    ├─ client.iter_messages("yakjangsu", limit=50)
    │     └─ MessageMediaPhoto 필터링 (최근 12시간 이내)
    │
    ├─ 가장 최근 배치 선택
    │     (5분 이내에 연속 포스팅된 사진 묶음)
    │
    └─ 최대 5장 다운로드 → 임시 디렉터리
          └─ Telegram Bot API로 전송 후 삭제
```

### 배치 선택 로직

yakjangsu 채널은 미국장 마감 직후 시황 이미지를 한 번에 연속으로 올립니다. `BATCH_WINDOW_SECONDS = 300` (5분) 기준으로 가장 최신 배치를 식별하고, 게시 순서대로 최대 5장을 선택합니다.

## 환경 변수

| 변수명 | 용도 |
|--------|------|
| `TELEGRAM_BOT_TOKEN` | Bot API 전송용 봇 토큰 |
| `TELEGRAM_CHAT_ID` | 리포트 발송 채널/그룹 ID |
| `TELEGRAM_API_ID` | MTProto 앱 ID (my.telegram.org) |
| `TELEGRAM_API_HASH` | MTProto 앱 Hash |
| `TELEGRAM_SESSION_STRING` | Telethon StringSession (최초 1회 `scripts/generate_session.py`로 생성) |

## GitHub Actions 워크플로

`.github/workflows/daily_report.yml`

- Docker 이미지 빌드 후 `uv run python src/main.py` 실행
- HTML 리포트를 artifact로 저장하고 GitHub Pages에 배포
- 실패 시 Telegram 알림 (curl via Bot API)

## GCP 배포

GCP Compute Engine (`trading-bot-seoul`, `us-east1-c`) 인스턴스의 `/home/patrick.jang/Macro-Pulse/`에 배포되어 있습니다.

로컬 → GCP 배포:

```bash
# auto-trading 프로젝트의 deploy 스크립트 참고
# gcloud compute scp --project=tradingbot-korea --zone=us-east1-c
```

> **참고:** GitHub Actions와 GCP cron 두 가지 실행 환경이 존재합니다. GitHub repo는 Actions 기준으로 관리하고, GCP는 별도 환경변수로 운영합니다.
