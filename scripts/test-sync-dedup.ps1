#Requires -Version 7.5
<#
.SYNOPSIS
    sync.ps1 schema-v2 regression: stale variants are repaired, duplicates removed,
    user-owned rules survive.

.DESCRIPTION
    Covers:
      1. ~/.cursor/plugins/local/claude-config/rules (fully managed)
      2. ~/.cursor/rules shadow collisions
      3. Qoder / Trae / Trae CN rule channels (.claude-managed ledger)

.EXAMPLE
    pwsh -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1
#>
$ErrorActionPreference = "Stop"
$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SYNC = Join-Path $CLAUDE_DIR "scripts\sync.ps1"
$pluginRules = Join-Path $env:USERPROFILE ".cursor\plugins\local\claude-config\rules"
$cursorRules = Join-Path $env:USERPROFILE ".cursor\rules"

# Target basenames (source rules rename AGENTS.md -> AGENTS-COLLAB.md).
$RULE_BASES = @(Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -File -Filter "*.md" |
    Where-Object { $_.Name -ne "README.md" } |
    ForEach-Object { if ($_.BaseName -eq "AGENTS") { "AGENTS-COLLAB" } else { $_.BaseName } })
$EXPECTED_BASES = @($RULE_BASES) + @("00-AGENTS", "CURSOR-EDITOR")

$script:InjectedBackup = @{}
function Save-Existing($p) {
    if (Test-Path -LiteralPath $p) { $script:InjectedBackup[$p] = [IO.File]::ReadAllText($p) }
}
function Restore-Or-Remove($p) {
    if ($script:InjectedBackup.ContainsKey($p)) {
        [IO.File]::WriteAllText($p, $script:InjectedBackup[$p])
        $script:InjectedBackup.Remove($p)
    } else {
        Remove-Item $p -Force -ErrorAction SilentlyContinue
    }
}

function Remove-Injected {
    foreach ($p in @(
            (Join-Path $pluginRules "CORE.md"),
            (Join-Path $pluginRules "AGENTS.md"),
            (Join-Path $pluginRules "BACKUP.mdc"),
            (Join-Path $cursorRules "CORE.mdc"),
            (Join-Path $cursorRules "MCP.md"),
            (Join-Path $cursorRules "AGENTS.md"),
            (Join-Path $cursorRules "MY-OWN.md")
        )) { Restore-Or-Remove $p }
    $coreMdc = Join-Path $pluginRules "CORE.mdc"
    if ($script:InjectedBackup.ContainsKey($coreMdc)) { Restore-Or-Remove $coreMdc }
    foreach ($h in @(".qoder\rules", ".trae\user_rules", ".trae-cn\user_rules")) {
        $d = Join-Path $env:USERPROFILE $h
        Restore-Or-Remove (Join-Path $d "MY-CUSTOM.md")
        Restore-Or-Remove (Join-Path $d "CORE.mdc")
    }
}

function Fail($m) {
    try {
        & pwsh -ExecutionPolicy Bypass -File $SYNC -All -Force 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { Write-Host "  [!!]  repair sync exited $LASTEXITCODE" -ForegroundColor Yellow }
    } catch { Write-Host "  [!!]  repair sync failed: $($_.Exception.Message)" -ForegroundColor Yellow }
    Remove-Injected
    Write-Host "  [FAIL] $m" -ForegroundColor Red
    exit 1
}
function Ok($m) { Write-Host "  [OK]   $m" -ForegroundColor Green }

function Assert-Contains($path, $needle, $label) {
    if (-not (Test-Path $path)) { Fail "$label missing" }
    $text = [IO.File]::ReadAllText($path)
    if (-not $text.Contains($needle)) { Fail "$label missing '$needle'" }
}

Write-Host "`n  sync schema-v2 regression" -ForegroundColor Cyan

if (-not (Test-Path $pluginRules)) { Fail "missing $pluginRules - run sync.ps1 first" }
if (-not (Test-Path (Join-Path $pluginRules "CORE.mdc"))) { Fail "CORE.mdc missing before test" }

# Inject stale content + variants + orphans (back up any pre-existing user files).
foreach ($p in @(
        (Join-Path $pluginRules "CORE.md"),
        (Join-Path $pluginRules "CORE.mdc"),
        (Join-Path $pluginRules "AGENTS.md"),
        (Join-Path $pluginRules "BACKUP.mdc")
    )) { Save-Existing $p }
if (-not (Test-Path $cursorRules)) { New-Item -ItemType Directory -Path $cursorRules -Force | Out-Null }
foreach ($p in @(
        (Join-Path $cursorRules "CORE.mdc"),
        (Join-Path $cursorRules "MCP.md"),
        (Join-Path $cursorRules "AGENTS.md"),
        (Join-Path $cursorRules "MY-OWN.md")
    )) { Save-Existing $p }
"stale" | Set-Content -Path (Join-Path $pluginRules "CORE.md") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $pluginRules "core.mdc") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $pluginRules "AGENTS.md") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $pluginRules "BACKUP.mdc") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $cursorRules "CORE.mdc") -Encoding utf8
"stale" | Set-Content -Path (Join-Path $cursorRules "MCP.md") -Encoding utf8
"user-own" | Set-Content -Path (Join-Path $cursorRules "AGENTS.md") -Encoding utf8
"user-own" | Set-Content -Path (Join-Path $cursorRules "MY-OWN.md") -Encoding utf8
Ok "injected variants into plugin / ~/.cursor/rules"

$editorChannels = @(
    @{ Name = "qoder";    Home = Join-Path $env:USERPROFILE ".qoder";    Dir = "rules";      Ext = ".md" }
    @{ Name = "trae";     Home = Join-Path $env:USERPROFILE ".trae";     Dir = "user_rules"; Ext = ".md" }
    @{ Name = "trae-cn";  Home = Join-Path $env:USERPROFILE ".trae-cn";  Dir = "user_rules"; Ext = ".md" }
)
foreach ($ch in $editorChannels) {
    if (-not (Test-Path $ch.Home)) { continue }
    $dir = Join-Path $ch.Home $ch.Dir
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    foreach ($p in @((Join-Path $dir "CORE$($ch.Ext)"), (Join-Path $dir "CORE.mdc"), (Join-Path $dir "MY-CUSTOM$($ch.Ext)"))) { Save-Existing $p }
    "stale" | Set-Content -Path (Join-Path $dir "CORE$($ch.Ext)") -Encoding utf8
    "stale" | Set-Content -Path (Join-Path $dir "CORE.mdc") -Encoding utf8
    "user-own" | Set-Content -Path (Join-Path $dir "MY-CUSTOM$($ch.Ext)") -Encoding utf8
}

& pwsh -ExecutionPolicy Bypass -File $SYNC -All -Force | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "sync.ps1 exited $LASTEXITCODE" }
Ok "sync.ps1 -All -Force completed"

# 1) plugin: exactly one .mdc per expected base, no duplicate basenames.
foreach ($base in $EXPECTED_BASES) {
    $hits = @(Get-ChildItem $pluginRules -File -Force | Where-Object { $_.BaseName -ieq $base })
    if ($hits.Count -ne 1) { Fail "plugin/$base has $($hits.Count) files: $($hits.Name -join ', ')" }
    if ($hits[0].Extension -ne ".mdc") { Fail "plugin/$base expected .mdc got $($hits[0].Name)" }
}
$dups = @(Get-ChildItem $pluginRules -File -Force | Where-Object { -not $_.Name.StartsWith('.') } | Group-Object { $_.BaseName.ToLower() } | Where-Object { $_.Count -gt 1 })
if ($dups.Count -gt 0) { Fail "plugin duplicate basenames: $((($dups | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join '; '))" }
Ok "plugin rules: one .mdc per basename"

# 2) stale content repaired + adapted frontmatter/body
$core = Join-Path $pluginRules "CORE.mdc"
$coreText = [IO.File]::ReadAllText($core)
if ($coreText.Trim() -eq "stale") { Fail "plugin CORE.mdc still stale" }
Assert-Contains $core "alwaysApply: true" "plugin CORE alwaysApply"
Assert-Contains $core "# CORE" "plugin CORE heading"
Assert-Contains $core "~/.claude/config/workflow.yaml" "plugin CORE adapted path"
if (Test-Path (Join-Path $pluginRules "AGENTS.md")) { Fail "plugin orphan AGENTS.md survived" }
if (Test-Path (Join-Path $pluginRules "BACKUP.mdc")) { Fail "plugin orphan BACKUP.mdc survived" }
Ok "plugin CORE adapted + orphans removed"

# 3) ~/.cursor/rules shadows removed
foreach ($base in @("CORE", "MCP")) {
    $hits = @(Get-ChildItem $cursorRules -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.BaseName -ieq $base })
    if ($hits.Count -gt 0) { Fail "~/.cursor/rules/$base still shadows plugin" }
}
Ok "~/.cursor/rules free of plugin-shadowing rules"
foreach ($n in @("AGENTS.md", "MY-OWN.md")) {
    if (-not (Test-Path (Join-Path $cursorRules $n))) { Fail "~/.cursor/rules/$n was deleted" }
}
Ok "~/.cursor/rules user-owned files survived"

# 4) editor channels: expected files, adaptation, no alt-extension duplicate, user rule survives
foreach ($ch in $editorChannels) {
    if (-not (Test-Path $ch.Home)) { Ok "$($ch.Name): home missing - skipped"; continue }
    $dir = Join-Path $ch.Home $ch.Dir
    foreach ($base in $RULE_BASES) {
        $dst = Join-Path $dir "$base$($ch.Ext)"
        if (-not (Test-Path $dst)) { Fail "$($ch.Name)/$base$($ch.Ext) missing" }
        if (Test-Path (Join-Path $dir "$base.mdc")) { Fail "$($ch.Name)/$base.mdc alt-extension variant survived" }
    }
    Assert-Contains (Join-Path $dir "CORE$($ch.Ext)") "# CORE" "$($ch.Name) CORE heading"
    Assert-Contains (Join-Path $dir "CORE$($ch.Ext)") "~/.claude/config/workflow.yaml" "$($ch.Name) CORE adapted path"
    Assert-Contains (Join-Path $dir "AGENTS$($ch.Ext)") "本文件适配" "$($ch.Name) AGENTS profile"
    if (-not (Test-Path (Join-Path $dir "MY-CUSTOM$($ch.Ext)"))) { Fail "$($ch.Name): user-own rule was deleted" }
    Restore-Or-Remove (Join-Path $dir "MY-CUSTOM$($ch.Ext)")
    Ok "$($ch.Name): refresh + adaptation + user-own survived"
}

Remove-Injected
Write-Host "`n  ALL sync schema-v2 checks PASSED`n" -ForegroundColor Green
exit 0
