#Requires -Version 5.1
<#
.SYNOPSIS
    sync.ps1 去重回归：注入同类型同名变体 → sync -All → 断言仅剩规范扩展名单份

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1
#>
$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SYNC = Join-Path $CLAUDE_DIR "scripts\sync.ps1"
$rulesDir = Join-Path $env:USERPROFILE ".cursor\rules"
# L0 rules actually deployed by sync.ps1 into rules/ (not root CLAUDE.md)
$L0_RULES = @("00-CLAUDE-ROUTER", "CORE")

function Fail($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red; exit 1 }
function Ok($m) { Write-Host "  [OK]   $m" -ForegroundColor Green }

Write-Host "`n  sync dedup regression" -ForegroundColor Cyan

if (-not (Test-Path $rulesDir)) { Fail "missing $rulesDir — run sync.ps1 first" }

$coreMdc = Join-Path $rulesDir "CORE.mdc"
if (-not (Test-Path $coreMdc)) { Fail "CORE.mdc missing before test" }

# 注入同 basename 变体（扩展名 + 大小写）
"stale" | Set-Content -Path (Join-Path $rulesDir "CORE.md") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $rulesDir "core.mdc") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $rulesDir "CONTEXT.md") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $rulesDir "MCP.md") -Encoding utf8
# 误落在 rules/ 的根文件名变体（应在 -All 同步 CONTEXT/MCP/CORE 时被清掉同名；CLAUDE 不在 rules 同步集）
"stale" | Set-Content -Path (Join-Path $rulesDir "CLAUDE.md") -Encoding utf8
Ok "injected CORE.md, core.mdc, CONTEXT.md, MCP.md, CLAUDE.md variants"

& powershell -ExecutionPolicy Bypass -File $SYNC -All | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "sync.ps1 exited $LASTEXITCODE" }
Ok "sync.ps1 -All completed"

foreach ($base in $L0_RULES) {
    $matches = @(Get-ChildItem $rulesDir -File -Force | Where-Object { $_.BaseName -ieq $base })
    if ($matches.Count -ne 1) {
        Fail "$base has $($matches.Count) files: $($matches.Name -join ', ')"
    }
    if ($matches[0].Extension -ne ".mdc") {
        Fail "$base expected .mdc got $($matches[0].Name)"
    }
}
Ok "L0 rule basenames unique (.mdc only) in ~/.cursor/rules/"

# CONTEXT / MCP must be single .mdc after -All
foreach ($base in @("CONTEXT", "MCP")) {
    $matches = @(Get-ChildItem $rulesDir -File -Force | Where-Object { $_.BaseName -ieq $base })
    if ($matches.Count -ne 1 -or $matches[0].Extension -ne ".mdc") {
        Fail "$base variants not cleaned: $($matches.Name -join ', ')"
    }
}
Ok "CONTEXT/MCP single .mdc after -All"

# Misplaced root name under rules/ must be gone
$claudeInRules = @(Get-ChildItem $rulesDir -File -Force | Where-Object { $_.BaseName -ieq "CLAUDE" })
if ($claudeInRules.Count -gt 0) {
    Fail "misplaced CLAUDE still in rules/: $($claudeInRules.Name -join ', ')"
}
Ok "no misplaced CLAUDE.* under rules/"

# No duplicate basenames anywhere in personal rules
$dupGroups = @(Get-ChildItem $rulesDir -File | Group-Object { $_.BaseName.ToLower() } | Where-Object { $_.Count -gt 1 })
if ($dupGroups.Count -gt 0) {
    $detail = ($dupGroups | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join "; "
    Fail "duplicate basenames remain: $detail"
}
Ok "no duplicate basenames in personal rules"

# Content freshness: CORE.mdc must match source (not 'stale')
$srcCore = Get-Content (Join-Path $CLAUDE_DIR "rules\CORE.md") -Raw -Encoding utf8
$dstCore = Get-Content (Join-Path $rulesDir "CORE.mdc") -Raw -Encoding utf8
if ($dstCore -eq "stale`n" -or $dstCore -eq "stale`r`n" -or $dstCore.Trim() -eq "stale") {
    Fail "CORE.mdc still stale content"
}
if ($srcCore -ne $dstCore) {
    Fail "CORE.mdc content != ~/.claude/rules/CORE.md"
}
Ok "CORE.mdc content matches source"

Write-Host "`n  ALL sync dedup checks PASSED`n" -ForegroundColor Green
exit 0
