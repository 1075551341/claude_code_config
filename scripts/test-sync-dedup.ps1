<#
.SYNOPSIS
    sync.ps1 去重回归：注入同 basename 变体 → sync -All -Force → 断言每个 basename 只剩一份 .mdc

.DESCRIPTION
    覆盖 sync.ps1 的 Remove-SameBasenameVariants 与多编辑器通道（v11.1）：
      1. ~/.cursor/plugins/local/claude-config/rules  — Cursor 实际加载的唯一通道
      2. ~/.cursor/rules — 必须被清空同名项，否则 Cursor 会双份加载 Always Apply
      3. ~/.qoder-cn/rules（*.mdc）与 ~/.trae-cn/user_rules（*.md）— 变体去重 + 内容刷新
         + 用户自有规则（不在 .claude-managed 台账内）不得被孤儿清除误删；目录缺席自动跳过

    注意用 -Force：plugin/编辑器通道的去重挂在「内容有变更」分支下（sync.ps1 $needCopy），
    稳定状态下 hash 相同会整段跳过，不加 -Force 测不到去重逻辑。

.EXAMPLE
    # 全部命令（无参数）
    powershell -ExecutionPolicy Bypass -File scripts/test-sync-dedup.ps1

.NOTES
    会真实调用 sync.ps1 -All -Force 并临时造脏数据，跑完自行清理。
    退出码 0 = 去重正常；1 = 出现同名残留或内容未刷新（First-Fail 立即退出）。
#>
# 注意：#Requires 必须放在帮助块之后，否则 Get-Help 读不到上面的命令示例。
#Requires -Version 5.1

$ErrorActionPreference = "Stop"
$CLAUDE_DIR   = Join-Path $env:USERPROFILE ".claude"
$SYNC         = Join-Path $CLAUDE_DIR "scripts\sync.ps1"
$pluginRules  = Join-Path $env:USERPROFILE ".cursor\plugins\local\claude-config\rules"
$cursorRules  = Join-Path $env:USERPROFILE ".cursor\rules"
# sync.ps1 投放到 plugin 的 basename 集合：rules/*.md（除 README）+ 00-CLAUDE（v11: ROUTER 并入 CLAUDE.md）+ CURSOR-EDITOR
$EXPECTED_BASES = @(
    (Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -File |
        Where-Object { $_.Name -ne "README.md" } | ForEach-Object { $_.BaseName })
    "00-CLAUDE"
    "CURSOR-EDITOR"
)

function Fail($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red; exit 1 }
function Ok($m) { Write-Host "  [OK]   $m" -ForegroundColor Green }

Write-Host "`n  sync dedup regression" -ForegroundColor Cyan

if (-not (Test-Path $pluginRules)) { Fail "missing $pluginRules — run sync.ps1 first" }
if (-not (Test-Path (Join-Path $pluginRules "CORE.mdc"))) { Fail "CORE.mdc missing before test" }

# 注入同 basename 变体。NTFS 大小写不敏感，core.mdc 与 CORE.mdc 是同一文件，
# 写它等于把正确内容污染成 stale —— 用于验证同步会把内容刷回来。
"stale" | Set-Content -Path (Join-Path $pluginRules "CORE.md")     -Encoding utf8
"stale" | Set-Content -Path (Join-Path $pluginRules "core.mdc")    -Encoding utf8
"stale" | Set-Content -Path (Join-Path $pluginRules "CONTEXT.md")  -Encoding utf8
if (-not (Test-Path $cursorRules)) { New-Item -ItemType Directory -Path $cursorRules -Force | Out-Null }
"stale" | Set-Content -Path (Join-Path $cursorRules "CORE.mdc")    -Encoding utf8
"stale" | Set-Content -Path (Join-Path $cursorRules "MCP.md")      -Encoding utf8
Ok "injected variants into plugin / ~/.cursor/rules"

& powershell -ExecutionPolicy Bypass -File $SYNC -All -Force | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "sync.ps1 exited $LASTEXITCODE" }
Ok "sync.ps1 -All -Force completed"

# 1) plugin 目录：每个 basename 恰好一份，且必须是 .mdc
foreach ($base in $EXPECTED_BASES) {
    $hits = @(Get-ChildItem $pluginRules -File -Force | Where-Object { $_.BaseName -ieq $base })
    if ($hits.Count -ne 1) {
        Fail "plugin/$base has $($hits.Count) files: $($hits.Name -join ', ')"
    }
    if ($hits[0].Extension -ne ".mdc") {
        Fail "plugin/$base expected .mdc got $($hits[0].Name)"
    }
}
$dups = @(Get-ChildItem $pluginRules -File | Group-Object { $_.BaseName.ToLower() } | Where-Object { $_.Count -gt 1 })
if ($dups.Count -gt 0) {
    Fail "plugin duplicate basenames: $((($dups | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join '; '))"
}
Ok "plugin rules: one .mdc per basename, no duplicates"

# 2) ~/.cursor/rules 不得残留与 plugin 同名项（否则 Cursor 双份加载 Always Apply）
$collisions = @(Get-ChildItem $cursorRules -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $EXPECTED_BASES -icontains $_.BaseName })
if ($collisions.Count -gt 0) {
    Fail "~/.cursor/rules still shadows plugin: $($collisions.Name -join ', ')"
}
Ok "~/.cursor/rules free of plugin-shadowing rules"

# 3) 内容新鲜度：被污染成 stale 的 CORE.mdc 必须刷回 SSOT 原文
$srcCore = Get-Content (Join-Path $CLAUDE_DIR "rules\CORE.md") -Raw -Encoding utf8
$dstCore = Get-Content (Join-Path $pluginRules "CORE.mdc") -Raw -Encoding utf8
if ($dstCore.Trim() -eq "stale") { Fail "plugin CORE.mdc still stale content" }
if ($srcCore -ne $dstCore) { Fail "plugin CORE.mdc content != ~/.claude/rules/CORE.md" }
Ok "plugin CORE.mdc content matches SSOT"

# 4) 多编辑器通道（v11.1）：变体去重 + 内容刷新 + 用户自有规则存活
$RULE_BASES = @(Get-ChildItem (Join-Path $CLAUDE_DIR "rules") -Filter "*.md" -File |
    Where-Object { $_.Name -ne "README.md" } | ForEach-Object { $_.BaseName })
$editorChannels = @(
    @{ Name = "qoder-cn"; Dir = Join-Path $env:USERPROFILE ".qoder-cn\rules";      Ext = ".mdc"; AltExt = ".md"  }
    @{ Name = "trae-cn";  Dir = Join-Path $env:USERPROFILE ".trae-cn\user_rules";  Ext = ".md";  AltExt = ".mdc" }
)
foreach ($ch in $editorChannels) {
    if (-not (Test-Path (Split-Path $ch.Dir -Parent))) {
        Ok "$($ch.Name): home missing - skipped"
        continue
    }
    if (-not (Test-Path $ch.Dir)) { New-Item -ItemType Directory -Path $ch.Dir -Force | Out-Null }
    # 污染 CORE + 注入异扩展变体 + 用户自有规则
    "stale" | Set-Content -Path (Join-Path $ch.Dir "CORE$($ch.Ext)")     -Encoding utf8
    "stale" | Set-Content -Path (Join-Path $ch.Dir "CORE$($ch.AltExt)")  -Encoding utf8
    "user-own" | Set-Content -Path (Join-Path $ch.Dir "MY-CUSTOM$($ch.Ext)") -Encoding utf8

    & powershell -ExecutionPolicy Bypass -File $SYNC -Force | Out-Null
    if ($LASTEXITCODE -ne 0) { Fail "$($ch.Name): sync.ps1 exited $LASTEXITCODE" }

    foreach ($base in $RULE_BASES) {
        $hits = @(Get-ChildItem $ch.Dir -File -Force | Where-Object { $_.BaseName -ieq $base })
        if ($hits.Count -ne 1) { Fail "$($ch.Name)/$base has $($hits.Count) files: $($hits.Name -join ', ')" }
        if ($hits[0].Extension -ne $ch.Ext) { Fail "$($ch.Name)/$base expected $($ch.Ext) got $($hits[0].Name)" }
    }
    $srcCore2 = Get-Content (Join-Path $CLAUDE_DIR "rules\CORE.md") -Raw -Encoding utf8
    $dstCore2 = Get-Content (Join-Path $ch.Dir "CORE$($ch.Ext)") -Raw -Encoding utf8
    if ($srcCore2 -ne $dstCore2) { Fail "$($ch.Name)/CORE$($ch.Ext) content != SSOT" }
    # 用户自有规则必须存活（台账外文件不受孤儿清除影响）
    if (-not (Test-Path (Join-Path $ch.Dir "MY-CUSTOM$($ch.Ext)"))) {
        Fail "$($ch.Name): user-own rule was deleted by orphan cleanup"
    }
    Remove-Item (Join-Path $ch.Dir "MY-CUSTOM$($ch.Ext)") -Force -ErrorAction SilentlyContinue
    Ok "$($ch.Name): dedupe + refresh + user-own rule survived"
}

# 清理：sync 不认识的注入项（basename 不在投放集合内）需自行删除
Remove-Item (Join-Path $cursorRules "MCP.md") -Force -ErrorAction SilentlyContinue

Write-Host "`n  ALL sync dedup checks PASSED`n" -ForegroundColor Green
exit 0
