**Language:** **한국어** | [English](docs/README.en.md)

# Macro Pulse Bot

Macro Pulse Bot은 주요 거시경제 지표를 수집해 HTML 리포트를 만들고, 텔레그램 및 이메일로 전달하는 자동화 봇입니다. 기본 실행 시 현재 UTC 시간을 기준으로 국장(`KR`) 또는 미장(`US`) 모드를 자동 선택하며, GitHub Actions를 통해 정기 실행할 수 있습니다.

## 주요 기능

- Yahoo Finance, Frankfurter, CNBC 데이터를 결합해 시장 데이터를 수집합니다.
- 일간 변동률과 최근 7개 구간 추이를 포함한 HTML 리포트를 생성합니다.
- `KR` 모드에서는 KOSPI/KOSDAQ 히트맵, `US` 모드에서는 Finviz 맵 스크린샷을 함께 전송합니다.
- 텔레그램 메시지 전송을 지원하며, SMTP 설정 시 이메일 발송도 가능합니다.
- GitHub Actions에서 스케줄 실행 후 최신 리포트를 GitHub Pages에 배포할 수 있습니다.

## 수집 항목

- 국내 지수: `KOSPI`, `KOSDAQ`
- 해외 지수: `S&P 500`, `Nasdaq`, `Euro Stoxx 50`, `Nikkei 225`, `Hang Seng`, `Shanghai Composite`
- 원자재/금리: `Gold`, `Silver`, `Copper`, `US 10Y Treasury`, `Japan 10Y Treasury`, `Korea 10Y Treasury`
- 환율: `USD/KRW`, `JPY/KRW`, `EUR/KRW`, `CNY/KRW`
- 가상자산: `Bitcoin`, `Ethereum`
- 변동성: `VIX`, `VKOSPI`

## 동작 방식

1. `src/data_fetcher.py`가 Yahoo Finance, Frankfurter, CNBC에서 데이터를 수집합니다.
2. `src/report_generator.py`가 HTML 리포트와 텔레그램 요약 메시지를 생성합니다.
3. `src/main.py`가 리포트를 `macro_pulse_report.html`로 저장합니다.
4. `--dry-run`이 아니면 시장 모드에 맞는 스크린샷을 임시 파일로 생성해 전송에 사용하고, 작업이 끝나면 정리합니다.

## 요구 사항

- 텔레그램 전송용 Bot Token 및 Chat ID
- GitHub Actions, Secrets 및 Pages 설정

## 리포트 포맷 구성

텔레그램 요약 포맷과 스크린샷 구성은 [`config/report_formats.json`](config/report_formats.json)에서 관리합니다.

- 국장 마감(`KR`) 포맷: 국내 증시를 먼저 보여주고, 이어서 아시아 증시, 변동성, 한일 국채, 환율 순으로 배치합니다.
- 국장 마감(`KR`) 스크린샷: `KOSPI`, `KOSDAQ` 히트맵 2장을 첨부합니다.
- 미장 마감(`US`) 포맷: 미국/유럽 증시를 먼저 보여주고, 이어서 변동성, 미국채와 원자재, 환율, 암호화폐 순으로 배치합니다.
- 미장 마감(`US`) 스크린샷: `Finviz` 맵 1장을 첨부합니다.
- 포맷 변경 방법: `summary_sections`에서 섹션 제목, 카테고리, 항목 순서를 수정하고 `screenshot_targets`에서 첨부할 스크린샷 종류를 바꾸면 됩니다.
- GitHub Actions 참조 방식: 워크플로는 `REPORT_FORMAT_CONFIG=config/report_formats.json` 환경 변수로 같은 설정 파일을 읽습니다.

## 스크린샷 예시

### 미장 마감 예시

![미장 마감 보고서 예시](imgs/us.png)

### 국장 마감 예시

![국장 마감 보고서 예시](imgs/kr.png)

## 생성 산출물

- `macro_pulse_report.html`: 메인 HTML 리포트
- `public/index.html`: GitHub Pages 배포용 리포트 파일
- 스크린샷 PNG: 텔레그램 전송에만 생성되며 저장소에는 기록하지 않음

## GitHub Actions

기본 워크플로는 `.github/workflows/daily_report.yml`에 정의되어 있습니다.

- 화요일-토요일 06:30 KST: 미장 마감 기준 리포트 실행
- 월요일-금요일 17:00 KST: 국장 마감 기준 리포트 실행
- 수동 실행: `workflow_dispatch`
- 포맷 설정 파일: `REPORT_FORMAT_CONFIG=config/report_formats.json`

보조 워크플로 `.github/workflows/test_telegram.yml`에서는 `KR` 또는 `US` 모드를 선택해 텔레그램 전송 테스트를 수동 실행할 수 있습니다.

## GitHub Secrets

GitHub Actions에서 사용하려면 저장소의 `Settings > Secrets and variables > Actions`에 아래 값을 등록합니다.

간단한 설명은 [docs/SECRETS.md](docs/SECRETS.md)에서 확인할 수 있습니다.

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SMTP_USERNAME` (선택)
- `SMTP_PASSWORD` (선택)
- `RECIPIENT_EMAIL` (선택)

## GitHub Pages

최신 리포트를 웹에서 보려면 GitHub Pages를 활성화해야 합니다.

1. 저장소의 `Settings > Pages`로 이동합니다.
2. 배포 브랜치를 `gh-pages`로 설정합니다.
3. 배포 후 리포트는 `https://<your-username>.github.io/Macro-Pulse/` 형태의 주소에서 확인할 수 있습니다.

## 로컬 설치

```bash
# Python 3.12 이상
pip install -r requirements.txt
```

## 환경 변수 설정

루트 디렉터리에 `.env` 파일을 만들고 아래 값을 채워 넣습니다.

```ini
# Telegram Config
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Config (optional)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient_email@example.com
```

- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`가 없으면 텔레그램 전송은 건너뜁니다.
- `SMTP_USERNAME`, `SMTP_PASSWORD`가 없으면 이메일 전송은 건너뜁니다.
- `RECIPIENT_EMAIL`이 비어 있으면 `SMTP_USERNAME` 주소로 전송합니다.


## 로컬 실행

리포트만 생성:

```bash
python src/main.py --dry-run
```

자동 모드로 실행 후 전송:

```bash
python src/main.py
```

시장 모드 강제 지정:

```bash
python src/main.py --market KR
python src/main.py --market US
```

- `--market KR`: 국장 기준 요약 및 KOSPI/KOSDAQ 스크린샷 사용
- `--market US`: 미장 기준 요약 및 Finviz 스크린샷 사용
- `--market Global` 또는 옵션 생략: 현재 UTC 시간 기준으로 `KR`/`US` 자동 선택


## 테스트

기본 테스트 실행:

```bash
python -m unittest discover tests
```

라이브 스모크 테스트 실행:

```bash
RUN_LIVE_SMOKE_TESTS=1 python -m unittest discover tests
```

스크린샷만 개별 확인:

```bash
python tests/test_screenshot.py --target finviz
python tests/test_screenshot.py --target kospi
python tests/test_screenshot.py --target kosdaq
```

`RUN_LIVE_SMOKE_TESTS=1`은 실제 외부 서비스에 요청을 보내므로 네트워크 상태와 외부 사이트 응답에 따라 테스트가 달라질 수 있습니다.

## 디렉터리 구조

```text
.
|-- src/
|   |-- main.py
|   |-- data_fetcher.py
|   |-- frankfurter_fetcher.py
|   |-- cnbc_fetcher.py
|   |-- report_generator.py
|   |-- report_format_config.py
|   |-- artifact_utils.py
|   |-- notifier.py
|   |-- screenshot_utils.py
|   `-- templates/report.html
|-- tests/
|-- config/
|-- docs/
|   |-- README.en.md
|   `-- SECRETS.md
|-- imgs/
|-- .github/workflows/
|-- .env-sample
|-- main.py
`-- README.md
```

## 문제 해결

- 스크린샷 생성 실패: Chrome/Chromium 실행 환경과 외부 사이트 접근 가능 여부를 확인하세요.
- 텔레그램 메시지가 오지 않음: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` 값을 다시 확인하세요.
- 이메일 전송 실패: Gmail SMTP 사용 기준으로 앱 비밀번호가 필요합니다.
- 환율 또는 지수 데이터 누락: Yahoo Finance, Frankfurter, CNBC 응답 실패 시 일부 항목이 비어 있을 수 있습니다.
- GitHub Pages가 갱신되지 않음: `gh-pages` 브랜치가 Pages 배포 대상으로 선택되어 있는지 확인하세요.
