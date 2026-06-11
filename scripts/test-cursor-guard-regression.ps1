#Requires -Version 5.1
<#
.SYNOPSIS
    Cursor Guard 一键回归：清理干扰状态 → 跑 hook 模拟 → 输出报告

.DESCRIPTION
    - 自动设置 UTF-8，避免 Windows GBK 乱码
    - 测试前清除 compress-pending / tool-counter（测试脚本内也会隔离）
    - 行为断言 + JSON 合法性（见 test-cursor-guard-hooks.py）

.PARAMETER Deploy
    回归前先执行 deploy-cursor-guard.ps1

.PARAMETER OpenReport
    完成后用默认编辑器打开 JSON 报告

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/test-cursor-guard-regression.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/test-cursor-guard-regression.ps1 -Deploy
#>
param(
    [switch]$Deploy,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$CURSOR_DIR = Join-Path $env:USERPROFILE ".cursor"
$TEST_PY = Join-Path $CLAUDE_DIR "scripts\test-cursor-guard-hooks.py"
$REPORT = Join-Path $CLAUDE_DIR "scripts\test-guard-result.json"
$STATE = Join-Path $CURSOR_DIR ".state"

function Write-Ok { param($m) Write-Host "  [OK]  $m" -ForegroundColor Green }
function Write-Fail { param($m) Write-Host "  [XX]  $m" -ForegroundColor Red }
function Write-Info { param($m) Write-Host "  [--]  $m" -ForegroundColor DarkGray }

Write-Host ""
Write-Host "  Cursor Guard regression" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $TEST_PY)) {
    Write-Fail "missing $TEST_PY"
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Fail "python not found"
    exit 1
}
Write-Ok "Python: $(& python --version 2>&1)"

if ($Deploy) {
    $deploy = Join-Path $CLAUDE_DIR "scripts\deploy-cursor-guard.ps1"
    if (-not (Test-Path $deploy)) {
        Write-Fail "missing $deploy"
        exit 1
    }
    Write-Info "deploy-cursor-guard.ps1 ..."
    & powershell -ExecutionPolicy Bypass -File $deploy
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-Path (Join-Path $CURSOR_DIR "hooks.json"))) {
    Write-Fail "~/.cursor/hooks.json not found — run deploy-cursor-guard.ps1 first"
    exit 1
}
Write-Ok "hooks.json present"

# 清除易干扰回归的瞬时状态（测试脚本内仍有 backup/restore）
if (Test-Path $STATE) {
    foreach ($f in @("compress-pending.json", "tool-counter.json")) {
        $p = Join-Path $STATE $f
        if (Test-Path $p) {
            Remove-Item $p -Force
            Write-Info "cleared $f"
        }
    }
}

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Info "running hook simulation ..."
python $TEST_PY --output $REPORT
$code = $LASTEXITCODE

if ($code -ne 0) {
    Write-Fail "regression failed (exit $code)"
    Write-Host "  See: $REPORT" -ForegroundColor DarkGray
    exit $code
}

try {
    $json = Get-Content $REPORT -Raw -Encoding utf8 | ConvertFrom-Json
    $sum = $json.summary
    Write-Host ""
    Write-Ok $sum.json_exit
    Write-Ok $sum.behavior
    if ($json.guard_version) {
        Write-Info "guard_version=$($json.guard_version)"
    }
} catch {
    Write-Info "report written (parse skipped): $REPORT"
}

Write-Host ""
Write-Host "  All regression checks passed." -ForegroundColor Green
Write-Host "  Report: $REPORT" -ForegroundColor DarkGray
Write-Host ""

if ($OpenReport) {
    Start-Process $REPORT
}

exit 0
