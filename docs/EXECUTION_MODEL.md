# Execution Model
# Updated: 2026-04-30

## Canonical Runtime Owner

`Macro-Pulse` runs on **GitHub Actions**, not on the GCP VM cron.

Production scheduler:

- GitHub Actions workflow: `.github/workflows/daily_report.yml`
- Manual fallback: `workflow_dispatch`

The GCP VM must not be treated as the runtime owner for this repository.

## Schedule Source Of Truth

The workflow schedule should stay aligned with:

- `config/report_formats.json`
- `src/macro_pulse/workflows/schedule_sync.py`

Current intended schedule:

- KR close report: `00 08 * * 1-5`
- US close report: `30 21 * * 1-5`

## Separation From trading-bot-seoul

`imgjun/GCP_trading-bot-seoul` is a separate repository with a different owner:

- runtime owner: GCP VM cron
- host path: `/home/patrick.jang/trading-bot-seoul`

Do not merge the two execution models.

## Token Rotation Rule

When the Telegram bot token is rotated:

1. update `Macro-Pulse` GitHub repository secrets
2. update `trading-bot-seoul` GCP `.env`
3. verify both runtimes independently

## Troubleshooting Checklist

Before saying `Macro-Pulse` is live:

- confirm `.github/workflows/daily_report.yml` has `on.schedule`
- confirm repository secrets are present and current
- confirm the latest workflow run succeeded
- confirm no operator note claims this repo is owned by GCP cron
