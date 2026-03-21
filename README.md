**Language:** **한국어** | [English](docs/README.en.md)

# Macro Pulse Bot

Macro Pulse Bot은 시장 데이터를 모아서 한 장의 리포트로 만들어 주는 자동화 프로젝트입니다.

- 주요 지표를 수집합니다.
- HTML 리포트를 만듭니다.
- 텔레그램과 이메일로 보낼 수 있습니다.
- GitHub Actions로 정해진 시간에 자동 실행할 수 있습니다.

복잡한 금융 지식을 몰라도, "데이터를 모아서 보기 좋게 정리해 주는 봇"이라고 생각하면 됩니다.

## 무엇을 해주나요?

- 한국장(`KR`) 또는 미국장(`US`) 기준으로 리포트를 만듭니다.
- 주가지수, 환율, 금리, 원자재, 비트코인 같은 지표를 모읍니다.
- 텔레그램용 짧은 요약과 HTML 리포트를 함께 만듭니다.
- 시장 분위기를 보기 위한 스크린샷도 붙일 수 있습니다.
  - `KR`: KOSPI / KOSDAQ 히트맵
  - `US`: Finviz 맵

## 어떻게 동작하나요?

흐름은 단순합니다.

1. Yahoo Finance, Frankfurter, CNBC에서 데이터를 가져옵니다.
2. 가져온 데이터를 정리합니다.
3. HTML 리포트와 텔레그램 요약 문구를 만듭니다.
4. 필요하면 텔레그램/이메일로 전송합니다.

실제 실행 파일은 [`src/main.py`](src/main.py)입니다.

## 어떤 데이터가 들어가나요?

- 국내 지수: `KOSPI`, `KOSDAQ`
- 해외 지수: `S&P 500`, `Nasdaq`, `Nikkei 225` 등
- 금리/원자재: `US 10Y Treasury`, `Gold`, `Silver`, `Copper`
- 환율: `USD/KRW`, `JPY/KRW`, `EUR/KRW`, `CNY/KRW`
- 가상자산: `Bitcoin`, `Ethereum`
- 변동성: `VIX`, `VKOSPI`

## GitHub Actions로 자동 실행하기

이 저장소는 GitHub Actions를 사용합니다.

- 정해진 시간에 자동으로 리포트를 만듭니다.
- 최신 리포트를 GitHub Pages에 올릴 수 있습니다.
- 실행 로그와 결과 파일을 artifact로 저장합니다.
- 실패하면 Telegram으로 알림을 보내도록 설정할 수 있습니다.

설정이 필요하면 [`docs/SECRETS.md`](docs/SECRETS.md)를 같이 보면 됩니다.

## 포맷을 바꾸고 싶다면

텔레그램 요약 순서나 스크린샷 종류는 [`config/report_formats.json`](config/report_formats.json)에서 바꿀 수 있습니다.

- 어떤 섹션을 먼저 보여줄지
- 어떤 항목을 포함할지
- 어떤 스크린샷을 붙일지

코드를 몰라도 JSON만 조금 수정하면 순서를 바꿀 수 있습니다.

## 로컬 / Docker 실행

자세한 실행 방법은 [`docs/LOCAL_RUN.md`](docs/LOCAL_RUN.md)에서 볼 수 있습니다.

> 빠른 미리보기
>
> - 설치: `python3 -m pip install -r requirements.txt`
> - Python dry-run: `python3 src/main.py --dry-run`
> - Docker build: `docker build -t macro-pulse .`
> - Docker dry-run: `docker run --rm --env-file .env -v "$PWD:/app" -w /app macro-pulse python src/main.py --dry-run`

## 테스트

기본 테스트:

```bash
python3 -m unittest discover tests
```

실제 외부 서비스까지 확인하는 스모크 테스트:

```bash
RUN_LIVE_SMOKE_TESTS=1 python3 -m unittest discover tests
```

스크린샷 스모크 테스트:

```bash
RUN_SCREENSHOT_SMOKE_TESTS=1 python3 -m unittest tests.test_screenshot
```

## 스크린샷 예시

### 미장 마감 예시

![미장 마감 보고서 예시](imgs/us.png)

### 국장 마감 예시

![국장 마감 보고서 예시](imgs/kr.png)

## 자주 보는 파일

- [`src/main.py`](src/main.py): 전체 실행 시작점
- [`src/data_fetcher.py`](src/data_fetcher.py): 데이터 수집
- [`src/report_generator.py`](src/report_generator.py): 리포트 생성
- [`src/notifier.py`](src/notifier.py): 텔레그램/이메일 전송
- [`config/report_formats.json`](config/report_formats.json): 요약 포맷 설정

## 문제 해결

- 스크린샷이 실패하면 Chrome/Chromium 실행 환경을 먼저 확인하세요.
- 텔레그램 메시지가 안 오면 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`를 확인하세요.
- 일부 데이터가 비어 있으면 외부 사이트 응답 문제일 수 있습니다.
- GitHub Pages가 안 보이면 `gh-pages` 설정을 확인하세요.
