param(
    [ValidateSet('KR', 'US', 'Global')]
    [string]$Market = 'Global',

    [switch]$DryRun,

    [switch]$RequireUsCloseWindow
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:UV_PROJECT_ENVIRONMENT = '.venv-win'
$env:UV_LINK_MODE = 'copy'

$logDir = Join-Path $repoRoot 'logs\windows-scheduler'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$logPath = Join-Path $logDir ("macro-pulse-$Market-$timestamp.log")

function Write-Log {
    param([string]$Text)
    Write-Output $Text
    Add-Content -Path $logPath -Value $Text -Encoding utf8
}

function Invoke-NativeLogged {
    param(
        [string]$Message,
        [string]$FilePath,
        [string[]]$Arguments
    )

    Write-Log $Message

    $stdoutPath = Join-Path $env:TEMP ("macro-pulse-stdout-$timestamp-$([guid]::NewGuid()).log")
    $stderrPath = Join-Path $env:TEMP ("macro-pulse-stderr-$timestamp-$([guid]::NewGuid()).log")

    try {
        $proc = Start-Process -FilePath $FilePath -ArgumentList $Arguments -WorkingDirectory $repoRoot -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath

        if (Test-Path $stdoutPath) {
            Get-Content $stdoutPath -Encoding UTF8 | ForEach-Object { Write-Log $_ }
        }
        if (Test-Path $stderrPath) {
            Get-Content $stderrPath -Encoding UTF8 | ForEach-Object { Write-Log $_ }
        }

        if ($proc.ExitCode -ne 0) {
            throw "Command failed with exit code $($proc.ExitCode)"
        }
    }
    finally {
        Remove-Item $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Test-UsMarketCloseWindow {
    $etZone = [System.TimeZoneInfo]::FindSystemTimeZoneById('Eastern Standard Time')
    $utcNow = [DateTimeOffset]::UtcNow
    $etOffset = $etZone.GetUtcOffset($utcNow.UtcDateTime)
    $etNow = $utcNow.ToOffset($etOffset)
    $isWeekday = $etNow.DayOfWeek -in @(
        [System.DayOfWeek]::Monday,
        [System.DayOfWeek]::Tuesday,
        [System.DayOfWeek]::Wednesday,
        [System.DayOfWeek]::Thursday,
        [System.DayOfWeek]::Friday
    )

    return [PSCustomObject]@{
        EtNow = $etNow
        EtNowText = ('{0} ET' -f $etNow.ToString('yyyy-MM-dd HH:mm:ss zzz'))
        IsWeekday = $isWeekday
        IsCloseWindow = $isWeekday -and $etNow.Hour -eq 16
    }
}

Write-Log "[$(Get-Date -Format o)] repo=$repoRoot market=$Market dryRun=$DryRun"

if ($RequireUsCloseWindow -and $Market -eq 'US') {
    $window = Test-UsMarketCloseWindow
    Write-Log "US close-window gate: etNow=$($window.EtNowText) isWeekday=$($window.IsWeekday) isCloseWindow=$($window.IsCloseWindow)"
    if (-not $window.IsCloseWindow) {
        Write-Log 'Outside US market-close window; exiting without running Macro-Pulse.'
        exit 0
    }
}

if (-not (Test-Path '.venv-win\Scripts\python.exe')) {
    Invoke-NativeLogged 'Bootstrapping Windows virtualenv (.venv-win) via uv sync --all-groups' 'uv' @('sync', '--all-groups')
}

$runArgs = @('run', 'python', 'src/main.py', '--market', $Market)
if ($DryRun) {
    $runArgs += '--dry-run'
}

Invoke-NativeLogged "Running Macro-Pulse (market=$Market)" 'uv' $runArgs

Write-Log "[$(Get-Date -Format o)] completed successfully"
Write-Log "Log written to $logPath"