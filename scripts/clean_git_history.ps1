# clean_git_history.ps1
# Removes .env from ALL git history and force-pushes to GitHub.
#
# Run this ONCE from the Macro-Pulse project root:
#   cd D:\Models\Claude\Projects\Macro-Pulse
#   .\scripts\clean_git_history.ps1
#
# Prerequisites: Python 313 and git-filter-repo already installed via pip.

Set-Location "D:\Models\Claude\Projects\Macro-Pulse"

Write-Host "[1/4] Removing .env from all git history..." -ForegroundColor Yellow
C:\Python313\python.exe -m git_filter_repo --invert-paths --path .env --force

Write-Host "[2/4] Re-adding origin remote (filter-repo removes it)..." -ForegroundColor Yellow
& "C:\Program Files\Git\cmd\git.exe" remote add origin https://github.com/imgjun/Macro-Pulse.git

Write-Host "[3/4] Force-pushing cleaned history to GitHub..." -ForegroundColor Yellow
& "C:\Program Files\Git\cmd\git.exe" push origin main --force

Write-Host "[4/4] Done. Verify at: https://github.com/imgjun/Macro-Pulse/commits/main" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Also revoke the old bot token via @BotFather on Telegram." -ForegroundColor Red
