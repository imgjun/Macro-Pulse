**Language:** **한국어** | [English](LOCAL_RUN.en.md)

# 로컬 실행 가이드

이 문서는 Macro Pulse Bot을 로컬 Windows / WSL 또는 일반 로컬 환경에서 검증하는 방법을 정리합니다.

## 1. 의존성 설치

```bash
uv python install
uv sync --all-groups
```

### Windows 전용 권장 venv

WSL과 Windows가 같은 저장소를 번갈아 사용할 때 `.venv` 충돌이 날 수 있습니다. Windows 실행/스케줄러에는 전용 가상환경을 권장합니다.

```powershell
$env:UV_PROJECT_ENVIRONMENT = '.venv-win'
uv sync --all-groups
```

## 2. `.env` 준비

프로젝트 루트 `.env`에 아래 값을 준비하세요.

```ini
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SESSION_STRING=...
```

설명:
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: 최종 전송용
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION_STRING`: `@yakjangsu` 읽기용

### 세션 생성

```bash
uv run python scripts/generate_session.py
```

출력값은 봇 토큰 형식이 아니라 `StringSession` 긴 문자열이어야 합니다.

## 3. 권장 검증 순서

### US dry-run

```bash
uv run python src/main.py --dry-run --market US
```

### KR dry-run

```bash
uv run python src/main.py --dry-run --market KR
```

### 실제 Telegram 전송 포함 실행

```bash
uv run python src/main.py --market US
uv run python src/main.py --market KR
```

### Windows 스케줄러용 실행 스크립트

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_macro_pulse_windows.ps1 -Market US
powershell -ExecutionPolicy Bypass -File .\scripts\run_macro_pulse_windows.ps1 -Market KR
```

현재 확인된 Windows Task Scheduler 작업:
- `Macro-Pulse-US`: Windows 시간대가 `India Standard Time (IST)`일 때 `Tue-Sat 01:35`, `02:35` 이중 트리거
  - 스크립트가 내부적으로 `America/New_York` 기준 현재 시각을 계산하고, **미국 정규장 마감 16시대(ET)**일 때만 실제 실행합니다.
  - 목적: 뉴욕 DST(EDT/EST) 변경 시 스케줄러 시간을 수동으로 자주 바꾸지 않기 위함
- `Macro-Pulse-KR`: `Mon-Fri 16:30 IST`

로그 위치:
- `logs/windows-scheduler/*.log`

## 4. yakjangsu fetch 단독 점검

```bash
PYTHONPATH=src uv run python - <<'PY'
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))
import asyncio
from macro_pulse.reporting.screenshots import capture_screenshots

async def main():
    paths = await capture_screenshots(['yakjangsu'])
    print({'count': len(paths), 'files': paths})

asyncio.run(main())
PY
```

정상이라면 최신 배치 전체가 다운로드됩니다.

## 5. Docker 실행

### 빌드

```bash
docker build -t macro-pulse .
```

### dry-run

```bash
docker run --rm \
  --env-file .env \
  -v "$PWD:/app" \
  -w /app \
  macro-pulse \
  uv run --frozen python src/main.py --dry-run --market US
```

## 6. 결과 파일

- `macro_pulse_report.html`: HTML 리포트
- Telegram 첨부 이미지: 임시 디렉터리에 생성 후 정리됨

## 7. 문제 해결

- `No recent photo messages found`:
  - 채널 최신 이미지 업로드 시각 확인
  - 시간 필터(`MAX_POST_AGE_HOURS`) 확인
- `BotMethodInvalidError`:
  - 봇 세션으로 채널 히스토리를 읽으려 할 때 발생
- `You must use "async with" if the event loop is running`:
  - sync Telethon client를 async 경로에서 호출할 때 발생
- Windows에서 `.venv/lib64` 접근 오류가 나면 WSL에서 만든 `.venv`가 섞였는지 확인 후 재생성하세요.
