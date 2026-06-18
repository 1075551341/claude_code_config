#Requires -Version 5.1
<#
.SYNOPSIS
    sync.ps1 去重回归：注入同类型同名变体 → sync -Force → 断言仅剩单份

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1
#>
$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SYNC = Join-Path $CLAUDE_DIR "scripts\sync.ps1"
$rulesDir = Join-Path $env:USERPROFILE ".cursor\rules"
$L0 = @("00-CLAUDE-ROUTER", "CLAUDE", "CORE", "CURSOR-EDITOR")

function Fail($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red; exit 1 }
function Ok($m) { Write-Host "  [OK]   $m" -ForegroundColor Green }

Write-Host "`n  sync dedup regression" -ForegroundColor Cyan

if (-not (Test-Path $rulesDir)) { Fail "missing $rulesDir — run sync.ps1 first" }

# 注入 CORE/CLAUDE 的 .md 与大小写变体
$coreMdc = Join-Path $rulesDir "CORE.mdc"
if (-not (Test-Path $coreMdc)) { Fail "CORE.mdc missing before test" }
"stale" | Set-Content -Path (Join-Path $rulesDir "CORE.md") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $rulesDir "core.mdc") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $rulesDir "CLAUDE.md") -Encoding utf8
Ok "injected CORE.md, core.mdc, CLAUDE.md variants"

& powershell -ExecutionPolicy Bypass -File $SYNC -Force | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "sync.ps1 exited $LASTEXITCODE" }
Ok "sync.ps1 -Force completed"

foreach ($base in $L0) {
    $matches = @(Get-ChildItem $rulesDir -File -Force | Where-Object { $_.BaseName -ieq $base })
    if ($matches.Count -ne 1) {
        Fail "$base has $($matches.Count) files: $($matches.Name -join ', ')"
    }
    if ($matches[0].Extension -ne ".mdc") {
        Fail "$base expected .mdc got $($matches[0].Name)"
    }
}
Ok "L0 basenames unique (.mdc only) in ~/.cursor/rules/"

$dupGroups = Get-ChildItem $rulesDir -File | Group-Object { $_.BaseName.ToLower() } | Where-Object { $_.Count -gt 1 }
if ($dupGroups) {
    $detail = ($dupGroups | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join "; "
    Fail "duplicate basenames remain: $detail"
}
Ok "no duplicate basenames in personal rules"

Write-Host "`n  ALL sync dedup checks PASSED`n" -ForegroundColor Green
exit 0
