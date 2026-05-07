**Language:** **한국어** | [English](docs/README.en.md)

# Macro Pulse Bot

Macro Pulse Bot은 미국장/한국장 마감 후 주요 매크로 지표를 수집하고, 텔레그램 요약과 HTML 리포트를 생성하는 봇입니다.

## 현재 운영 상태

- **US 모드 이미지 소스:** `@yakjangsu` 텔레그램 채널
- **US 이미지 수집 방식:** Telethon MTProto 유저 세션으로 최신 앨범 **전체 이미지** 다운로드
- **KR 이미지 수집 방식:** Selenium으로 KOSPI/KOSDAQ 히트맵 캡처
- **GitHub Actions:** 현재는 **CI 전용**
- **GitHub Pages / GitHub Actions 수동 리포트 워크플로:** 정리 대상이었고 현재 저장소에서 제거
- **GCP crontab:** 마지막 점검 기준 **활성 Macro-Pulse 엔트리 없음**
- **현재 활성 스케줄러:** Windows Task Scheduler (`Macro-Pulse-US`, `Macro-Pulse-KR`)
- **Windows 시스템 시간대:** 마지막 검증 기준 `India Standard Time (IST)`
- **US 스케줄 방식:** IST 기준 `Tue-Sat 01:35` + `02:35` 이중 트리거, 스크립트 내부에서 **미국장 마감(16:00 ET) 윈도우**일 때만 실제 실행
- **KR 스케줄 방식:** IST 기준 `Mon-Fri 16:30`
- **현재 검증 우선 환경:** 로컬 Windows / WSL

즉, 이 저장소는 지금 **데이터 수집 + 리포트 생성 + Telegram 전송 코드**를 Windows 로컬 스케줄러와 함께 운영하는 상태입니다.

## 주요 기능

- `KR` / `US` 모드 지원
- Yahoo Finance / CNBC 기반 지표 수집
- HTML 리포트 생성
- Telegram 요약 메시지 생성 및 전송
- 시각 자료 첨부
  - `KR`: KOSPI / KOSDAQ 히트맵
  - `US`: `@yakjangsu` 최신 앨범 전체 이미지

## 실행 흐름

```text
src/main.py
  -> market_data.fetch_all_data()
  -> reporting.generator
  -> reporting.screenshots.capture_screenshots()
     - KR: Selenium heatmaps
     - US: Telethon fetch from @yakjangsu
  -> delivery.notifier.send_telegram_report()
```

자세한 구조는 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)를 참고하세요.

## US 이미지 수집 방식

US 마감 보고서에서는 `@yakjangsu` 채널의 최신 사진 배치를 사용합니다.

현재 동작:
- Telethon 유저 세션(`TELEGRAM_SESSION_STRING`)으로 채널 히스토리 조회
- 최근 게시물 중 최신 사진 배치를 선택
- 배치 윈도우(`BATCH_WINDOW_SECONDS = 300`) 안의 이미지를 게시 순서대로 유지
- 기본 제한 없이 **최신 배치 전체** 다운로드
- 현재 기본 시간 필터는 **24시간**

> 과거에는 Finviz 직접 캡처 또는 5장 제한 로직이 있었지만, 현재 기본값은 yakjangsu 전체 배치 다운로드입니다.

## 환경 변수

### Telegram Bot API 전송용
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Telegram MTProto 읽기용
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_SESSION_STRING`

`TELEGRAM_SESSION_STRING`은 **봇 토큰이 아니라** Telethon StringSession이어야 합니다.
생성 방법:

```bash
uv run python scripts/generate_session.py
```

## 로컬 실행

자세한 실행 방법은 [`docs/LOCAL_RUN.md`](docs/LOCAL_RUN.md)를 보세요.

빠른 예시:

```bash
uv sync --all-groups
uv run python src/main.py --dry-run --market US
uv run python src/main.py --market KR
```

## 테스트

기본 테스트:

```bash
uv run python -m unittest discover tests
```

핵심 회귀 테스트:

```bash
uv run python -m unittest tests.test_main -v
uv run python -m unittest tests.test_report_format_config -v
```

실제 스크린샷/외부 서비스 스모크 테스트:

```bash
RUN_SCREENSHOT_SMOKE_TESTS=1 uv run python -m unittest tests.test_screenshot
RUN_LIVE_SMOKE_TESTS=1 uv run python -m unittest discover tests
```

## GitHub Actions

현재 저장소의 GitHub Actions는 **CI (`.github/workflows/ci.yml`)만 유지**합니다.

포함 범위:
- `push` / `pull_request` 시 테스트
- 로그 artifact 업로드

제거된 항목:
- GitHub Actions 기반 수동 리포트 발송 workflow
- GitHub Pages 배포 workflow
- keepalive workflow

## 자주 보는 파일

- [`src/main.py`](src/main.py): asyncio 진입점
- [`src/macro_pulse/app/cli.py`](src/macro_pulse/app/cli.py): 전체 파이프라인 조율
- [`src/macro_pulse/data/providers/telegram_channel.py`](src/macro_pulse/data/providers/telegram_channel.py): yakjangsu 이미지 fetch
- [`src/macro_pulse/reporting/screenshots.py`](src/macro_pulse/reporting/screenshots.py): screenshot handler
- [`src/macro_pulse/delivery/notifier.py`](src/macro_pulse/delivery/notifier.py): Telegram 전송
- [`config/report_formats.json`](config/report_formats.json): KR/US 리포트 형식 메타데이터

## 문제 해결

- `No recent photo messages found`가 뜨면 시간 필터와 채널 최신 게시 시각을 같이 보세요.
- `TELEGRAM_SESSION_STRING`은 유저 세션이어야 합니다. 봇 계정이면 히스토리 조회가 제한됩니다.
- `async with` 관련 Telethon 에러가 보이면 sync client 경로가 다시 들어온 것인지 확인하세요.
- 일부 데이터가 비면 외부 데이터 소스 응답 문제일 수 있습니다.
