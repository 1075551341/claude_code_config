#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 多编辑器同步脚本 v14.5 — 仅L0入口 + 个人级单落点

.DESCRIPTION
    索引模式(默认): 7 总纲软链接 + skills/agents 目录联接 + 编辑器 rules 单文件链接与路由部署
    全量模式(-Full): 7 总纲 + agents/ 联接 + rules/skills 编辑器原生格式转换 + 路由规则部署

    不同步：commands/、hooks/、scripts/、MCP 配置。

.PARAMETER Full
    全量同步（agents 联接 + rules/skills 原生格式转换）

.PARAMETER Force
    强制重建所有链接

.PARAMETER DryRun
    仅预览，不写盘

.PARAMETER Scope
    同步范围（Cursor Guard 影响驱动同步用）:
    all=默认全量 | indexes=仅7总纲+INDEX软链 | rules=仅 rules 部署

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Full -Force
    powershell -ExecutionPolicy Bypass -File sync.ps1 -DryRun
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Scope rules -Force
#>

param(
    [switch]$Full,
    [switch]$Force,
    [switch]$DryRun,
    [ValidateSet("all", "rules", "indexes")]
    [string]$Scope = "all"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$BACKUP_DIR = Join-Path $CLAUDE_DIR "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$EDITORS = @("cursor", "devin", "trae", "qoder")
$CODEARTS_EDITORS = @("codearts-agent")
$SYNC_DIRS = @("skills", "agents")
$SYNC_DIRS_FULL_LINK = @("agents")
$SYNC_DIRS_FULL_NATIVE = @("rules", "skills")
$SYNC_FILES = @("CLAUDE.md", "CLAUDE-ROUTER.mdc", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md", "rules-INDEX.md")
$ROUTER_SOURCE_FILE = "CLAUDE-ROUTER.mdc"
$ROUTER_DEPLOY_BASENAME = "00-CLAUDE-ROUTER"
$ROUTER_DEPLOY_WHITELIST = @("00-CLAUDE-ROUTER.mdc", "00-CLAUDE-ROUTER.md")
$CLAUDE_RULE_DEPLOY_NAMES = @("CLAUDE.mdc", "CLAUDE.md")
# Cursor Guard 部署产物 — sync 清理时保留（非 ~/.claude/rules 源）
$CURSOR_GUARD_RULE_WHITELIST = @("CURSOR-EDITOR.mdc")
$EDITOR_RULE_PROTECT = $ROUTER_DEPLOY_WHITELIST + $CLAUDE_RULE_DEPLOY_NAMES + $CURSOR_GUARD_RULE_WHITELIST
# Cursor：同时部署到个人桥接目录与当前工作区项目规则目录
$GLOBAL_CURSOR_RULES_DIR = Join-Path $env:USERPROFILE ".cursor\rules"
$CLAUDE_CURSOR_PROJECT_DIR = Join-Path $CLAUDE_DIR ".cursor"
$CLAUDE_CURSOR_PROJECT_RULES_DIR = Join-Path $CLAUDE_CURSOR_PROJECT_DIR "rules"
# Devin Desktop 读 workspace .devin/rules/（非 ~/.devin/rules/ 编辑器配置目录）
$CLAUDE_DEVIN_RULES_DIR = Join-Path $CLAUDE_DIR ".devin\rules"
$DEVIN_MISPLACED_RULES_DIR = Join-Path $env:USERPROFILE ".devin\rules"
# CodeArts 码道：个人级 ~/.config/codeartsdoer/rule/（内核 rule-discovery 实际读取路径）
# UI 文案写 ~/.codeartsdoer/rule/ 为误导；skills 仍在 ~/.codeartsdoer/skills/
$CODEARTS_DOER_PERSONAL_RULES_DIR = Join-Path $env:USERPROFILE ".config\codeartsdoer\rule"
$CODEARTS_DOER_LEGACY_PERSONAL_RULES_DIR = Join-Path $env:USERPROFILE ".codeartsdoer\rule"
$CODEARTS_DOER_PROJECT_RULES_DIR = Join-Path $CLAUDE_DIR ".codeartsdoer\rule"
$CODEARTS_AGENT_LEGACY_RULES_DIR = Join-Path $env:APPDATA "codearts-agent\User\rules"
$CODEARTS_L0_BASE_NAMES = @("00-CLAUDE-ROUTER", "CLAUDE", "CORE")
$CODEARTS_USER_DIRS = @{
    "codearts-agent" = (Join-Path $env:APPDATA "codearts-agent\User")
}
$PROJECT_L0_BASE_NAMES = @(
    "00-CLAUDE-ROUTER",
    "CLAUDE",
    "CORE",
    "CURSOR-EDITOR"
)
$STALE_LINKS = @("hooks", "scripts", "commands", "AGENTS.md")

# 编辑器原生规则目录映射（使用各编辑器真正识别的全局/个人路径）
# Cursor: ~/.cursor/rules/*.mdc 为个人桥接（v14.5+ 仅L0入口）
# Devin Desktop: ~/.claude/.devin/rules/*.md（workspace，trigger 格式）+ global_rules.md（全局）
# Trae: ~/.trae/user_rules/*.md (Trae特有的全局rules目录，支持alwaysApply frontmatter)
$NATIVE_RULES_DIR_MAP = @{
    "cursor"   = @{ TargetDir = $GLOBAL_CURSOR_RULES_DIR; Ext = ".mdc"; Format = "cursor" }
    "devin"    = @{ TargetDir = $CLAUDE_DEVIN_RULES_DIR; Ext = ".md"; Format = "windsurf" }
    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\user_rules"); Ext = ".md"; Format = "trae" }
    "qoder"    = @{ TargetDir = (Join-Path $env:USERPROFILE ".qoder\rules"); Ext = ".mdc"; Format = "cursor" }
}
$CURSOR_PROJECT_RULES_CONFIG = @{ TargetDir = $CLAUDE_CURSOR_PROJECT_RULES_DIR; Ext = ".mdc"; Format = "cursor" }

# Full 模式：skills 原生副本目录（避免与 Index 模式 skills/ 联接冲突）
$NATIVE_SKILLS_DIR_MAP = @{
    "cursor"   = @{ TargetDir = (Join-Path $env:USERPROFILE ".cursor\skills-native"); Format = "cursor" }
    "devin"    = @{ TargetDir = (Join-Path $env:USERPROFILE ".devin\skills-native"); Format = "windsurf" }

    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\skills-native"); Format = "trae" }
    "qoder"    = @{ TargetDir = (Join-Path $env:USERPROFILE ".qoder\skills-native"); Format = "cursor" }
}

# Devin 全局 rules 单文件路径（核心规则，受 6000 字符限制）
$DEVIN_GLOBAL_RULES_FILE = Join-Path $env:USERPROFILE ".codeium\windsurf\memories\global_rules.md"

# Devin 字符限制
# 全局 global_rules.md: 6000 字符; 工作区 rules/*.md: 12000 字符/文件
$DEVIN_MAX_CHARS_GLOBAL = 6000
$DEVIN_MAX_CHARS_PER_FILE = 12000


$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

function Remove-ScopedSameTypeTarget {
    param(
        [string]$TargetPath,
        [string]$ScopeLabel,
        [string]$RequiredExt = "",
        [switch]$IsDirectory
    )
    <#
    .SYNOPSIS
        在指定同步范围内删除同类型、同名目标（链接或实体），再写入/链接。
        不跨目录（skills 只管 skills、rules 只管 rules），不删其他扩展名。
    #>
    if (-not $TargetPath) { return $false }
    $leaf = Split-Path $TargetPath -Leaf
    if ($RequiredExt -and -not $leaf.EndsWith($RequiredExt, [StringComparison]::OrdinalIgnoreCase)) {
        return $false
    }
    if (-not (Test-Path $TargetPath)) { return $false }

    if ($DryRun) {
        Write-Fix "[预演] 将删除 $ScopeLabel/$leaf（同类型同名）"
        $script:stats.Removed++
        return $true
    }

    $item = Get-Item $TargetPath -Force
    if ($IsDirectory -or $item.PSIsContainer) {
        Remove-Item $TargetPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    elseif (IsLink $TargetPath) {
        Remove-Item $TargetPath -Force -ErrorAction SilentlyContinue
    }
    else {
        Remove-Item $TargetPath -Force -ErrorAction SilentlyContinue
    }
    Write-Fix "已删除 $ScopeLabel/$leaf（同类型同名）"
    $script:stats.Removed++
    return $true
}

function Sync-SingleFile {
    param(
        [string]$Source,
        [string]$Target,
        [string]$Label
    )
    if (-not (Test-Path $Source)) {
        Write-Skip "源文件缺失: $Label"
        return
    }

    # 先删除同路径同类型目标（链接或实体文件），再创建新链接
    $ext = [System.IO.Path]::GetExtension($Target)
    $scope = if ($Label -match '/') { ($Label -split '/')[0] } else { "root" }
    Remove-ScopedSameTypeTarget -TargetPath $Target -ScopeLabel $scope -RequiredExt $ext | Out-Null

    if ($DryRun) { Write-Ok "[预演] 将创建 $Label 链接"; $script:stats.Links++; return }
    try {
        if ($isAdmin) {
            New-Item -ItemType SymbolicLink -Path $Target -Target $Source -Force | Out-Null
        }
        else {
            $r = & cmd.exe /c "mklink `"$Target`" `"$Source`"" 2>&1
            if ($LASTEXITCODE -ne 0) { throw "mklink failed: $r" }
        }
        Write-Ok "$Label 已链接"
        $script:stats.Links++
    }
    catch {
        Write-Fail "${Label}: $_"
        $script:stats.Errors++
    }
}

function Write-Ok { param($m) Write-Host "    [OK]  $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "    [!!]  $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "    [XX]  $m" -ForegroundColor Red }
function Write-Fix { param($m) Write-Host "    [FIX] $m" -ForegroundColor DarkCyan }
function Write-Skip { param($m) Write-Host "    [--]  $m" -ForegroundColor DarkGray }
function Write-Info { param($m) Write-Host "  >> $m"      -ForegroundColor Cyan }

function IsLink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    return [bool]((Get-Item $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function New-Link {
    param([string]$Source, [string]$Target)
    if ($isAdmin) {
        New-Item -ItemType SymbolicLink -Path $Target -Target $Source -Force | Out-Null
    }
    else {
        $r = & cmd.exe /c "mklink /J `"$Target`" `"$Source`"" 2>&1
        if ($LASTEXITCODE -ne 0) { throw "mklink /J failed: $r" }
    }
}

function Remove-DirTarget {
    param(
        [string]$Path,
        [string]$Editor,
        [string]$Label
    )
    if (-not (Test-Path $Path)) { return }
    if (IsLink $Path) {
        if ($DryRun) { Write-Fix "[预演] 将删除联接: $Label"; $script:stats.Removed++; return }
        & cmd.exe /c "rmdir `"$Path`"" 2>&1 | Out-Null
        if (Test-Path $Path) { Remove-Item $Path -Force -ErrorAction SilentlyContinue }
        Write-Fix "已删除联接: $Label"
        $script:stats.Removed++
    }
    else {
        if ($DryRun) { Write-Fix "[预演] 将备份并删除实体目录: $Label"; return }
        Write-Warn "$Label 为实体目录，将备份后删除"
        $backupName = "${Editor}_$($Label -replace '/','_')"
        Copy-Item $Path (Join-Path $BACKUP_DIR $backupName) -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item $Path -Recurse -Force
        Write-Fix "已备份并删除实体目录: $Label"
        $script:stats.Removed++
    }
}

function Sync-DirJunction {
    param(
        [string]$Source,
        [string]$Target,
        [string]$Label,
        [string]$Editor
    )
    if (-not (Test-Path $Source)) {
        Write-Skip "源目录缺失: $Label"
        return
    }

    if (Test-Path $Target) {
        if (IsLink $Target) {
            if (-not $Force) {
                $actual = (Get-Item $Target -Force).Target
                if ($actual -is [array]) { $actual = $actual[0] }
                if ($actual -eq $Source) { Write-Ok "$Label 链接正确"; return }
                Write-Warn "$Label 链接目标不一致，将重建"
            }
            if (-not $DryRun) {
                & cmd.exe /c "rmdir `"$Target`"" 2>&1 | Out-Null
                if (Test-Path $Target) { Remove-Item $Target -Force -ErrorAction SilentlyContinue }
            }
        }
        else {
            Write-Warn "$Label 为实体目录，将备份后替换为链接"
            if (-not $DryRun) {
                Copy-Item $Target (Join-Path $BACKUP_DIR "${Editor}_${Label}") -Recurse -Force
                Remove-Item $Target -Recurse -Force
            }
        }
    }

    if ($DryRun) { Write-Ok "[预演] 将创建 $Label 链接"; $script:stats.Links++; return }
    try {
        New-Link -Source $Source -Target $Target
        Write-Ok "$Label 已链接"
        $script:stats.Links++
    }
    catch {
        Write-Fail "${Label}: $_"
        $script:stats.Errors++
    }
}

function Cleanup-FullNativeArtifacts {
    param(
        [string]$TargetDir,
        [string]$EditorName
    )
    if ($Full) { return }
    $nativeSkills = Join-Path $TargetDir "skills-native"
    if (Test-Path $nativeSkills) {
        if ($DryRun) { Write-Fix "[预演] 将删除 Full 模式 skills-native/"; return }
        Remove-DirTarget -Path $nativeSkills -Editor $EditorName -Label "skills-native/"
    }
}

function Write-SyncModeJson {
    param(
        [string]$TargetDir,
        [string]$Mode
    )
    if ($DryRun) { return }
    $payload = @{
        mode      = $Mode
        version   = "14.3"
        updated   = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        source    = $CLAUDE_DIR
    } | ConvertTo-Json -Compress
    $path = Join-Path $TargetDir "sync-mode.json"
    [System.IO.File]::WriteAllText($path, $payload, [System.Text.Encoding]::UTF8)
}

function Get-RouterSourceContent {
    $src = Join-Path $CLAUDE_DIR $ROUTER_SOURCE_FILE
    if (-not (Test-Path $src)) { return $null }
    return [System.IO.File]::ReadAllText($src, [System.Text.Encoding]::UTF8)
}

function Get-FrontmatterBlockScore {
    param([string]$FmText)
    $score = 0
    if ($FmText -match '(?m)^trigger:\s*\S+') { $score += 10 }
    if ($FmText -match '(?m)^description:\s*\S+') { $score += 5 }
    if ($FmText -match '(?m)^globs:\s*\S+') { $score += 3 }
    if ($FmText -match '(?m)^alwaysApply:\s*true' -and $FmText -notmatch '(?m)^trigger:') { $score += 1 }
    return $score
}

function Strip-OrphanFrontmatterFromBody {
    param([string]$Body)
    $result = $Body
    while ($true) {
        $trimmed = $result.TrimStart()
        if (-not $trimmed.StartsWith("---")) { break }
        $secondDash = $trimmed.IndexOf("---", 3)
        if ($secondDash -eq -1) { break }
        $result = $trimmed.Substring($secondDash + 3).TrimStart("`n")
    }
    return $result
}

function Split-RuleFrontmatterBlocks {
    param([string]$Content)
    $blocks = [System.Collections.Generic.List[hashtable]]::new()
    $pos = 0
    while ($pos -lt $Content.Length) {
        $remaining = $Content.Substring($pos)
        $leading = $remaining.Length - $remaining.TrimStart().Length
        if ($leading -gt 0) { $pos += $leading; continue }
        if (-not $remaining.StartsWith("---")) { break }
        $secondDash = $remaining.IndexOf("---", 3)
        if ($secondDash -eq -1) { break }
        $fmText = $remaining.Substring(3, $secondDash - 3).Trim()
        $blocks.Add(@{ Text = $fmText; Score = (Get-FrontmatterBlockScore -FmText $fmText) })
        $pos += $secondDash + 3
    }
    $body = if ($pos -lt $Content.Length) { $Content.Substring($pos).TrimStart("`n") } else { "" }
    return @{ Blocks = $blocks; Body = $body }
}

function Normalize-RuleSourceContent {
    param([string]$Content)
    <#
    .SYNOPSIS
        合并多重 frontmatter（如 AGENTS.md 残留双块），避免编辑器解析为多条同名规则
    #>
    $parsed = Split-RuleFrontmatterBlocks -Content $Content
    if ($parsed.Blocks.Count -eq 0) { return $Content }
    if ($parsed.Blocks.Count -eq 1) {
        $body = Strip-OrphanFrontmatterFromBody -Body $parsed.Body
        return "---`n$($parsed.Blocks[0].Text)`n---`n`n$body"
    }
    $best = ($parsed.Blocks | Sort-Object { $_.Score } -Descending | Select-Object -First 1).Text
    $body = Strip-OrphanFrontmatterFromBody -Body $parsed.Body
    return "---`n$best`n---`n`n$body"
}

function Remove-AllRuleVariantsByBaseName {
    param(
        [string]$TargetRulesDir,
        [string]$BaseName,
        [string]$ScopeLabel = "rules"
    )
    <#
    .SYNOPSIS
        删除 rules/ 内同 basename 的全部变体（.md/.mdc/大小写），先删后写，防重复
    #>
    if (-not $BaseName -or -not (Test-Path $TargetRulesDir)) { return }
    foreach ($f in Get-ChildItem $TargetRulesDir -File -Force -ErrorAction SilentlyContinue) {
        if ($f.BaseName -ieq $BaseName) {
            Remove-ScopedSameTypeTarget -TargetPath $f.FullName -ScopeLabel $ScopeLabel -RequiredExt $f.Extension | Out-Null
        }
    }
}

function Test-SourceNewerThanTarget {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )
    if (-not $SourcePath -or -not (Test-Path $SourcePath)) { return $false }
    if (-not (Test-Path $TargetPath)) { return $true }
    if (IsLink $TargetPath) { return $true }
    $srcTime = (Get-Item $SourcePath -Force).LastWriteTimeUtc
    $tgtItem = Get-Item $TargetPath -Force
    if ($tgtItem.PSIsContainer) { return $true }
    return $srcTime -gt $tgtItem.LastWriteTimeUtc
}

function Convert-ToCursorRuleContent {
    param([string]$Content)
    <#
    .SYNOPSIS
        将 rules/*.md 规范为单一 frontmatter + Cursor .mdc 原生格式
    #>
    $normalized = Normalize-RuleSourceContent -Content $Content
    if (-not $normalized.StartsWith("---")) {
        return "---`ndescription: Claude rule`nalwaysApply: true`n---`n`n$normalized"
    }

    $secondDash = $normalized.IndexOf("---", 3)
    if ($secondDash -eq -1) { return $normalized }

    $frontmatter = $normalized.Substring(3, $secondDash - 3).Trim()
    $body = Strip-OrphanFrontmatterFromBody -Body $normalized.Substring($secondDash + 3)

    $description = ""
    $alwaysApply = $null
    $globs = ""
    $triggerMode = ""
    $pathItems = [System.Collections.Generic.List[string]]::new()
    $inPathsBlock = $false

    foreach ($line in $frontmatter -split "`n") {
        $line = $line.Trim()
        if ($line -match "^description:\s*(.+)") {
            $description = $Matches[1].Trim().Trim("'").Trim('"')
            $inPathsBlock = $false
        }
        elseif ($line -match "^alwaysApply:\s*(true|false)") {
            $alwaysApply = ($Matches[1] -eq "true")
            $inPathsBlock = $false
        }
        elseif ($line -match "^trigger:\s*(\S+)") {
            $triggerMode = $Matches[1]
            if ($triggerMode -eq "always_on") { $alwaysApply = $true }
            $inPathsBlock = $false
        }
        elseif ($line -match "^globs:\s*(.+)") {
            $globs = $Matches[1].Trim().Trim("'").Trim('"')
            $inPathsBlock = $false
        }
        elseif ($line -match "^paths:\s*$") {
            $inPathsBlock = $true
        }
        elseif ($inPathsBlock -and $line -match "^-\s*['`"]?(.+?)['`"]?\s*$") {
            $pathItems.Add($Matches[1].Trim())
        }
        elseif ($line -match "^\S") {
            $inPathsBlock = $false
        }
    }

    if ($globs -eq "" -and $pathItems.Count -gt 0) {
        $globs = ($pathItems -join ", ")
    }

    $newFm = [System.Text.StringBuilder]::new()
    [void]$newFm.AppendLine("---")
    if ($description -ne "") { [void]$newFm.AppendLine("description: $description") }
    if ($triggerMode -eq "model_decision" -or $triggerMode -eq "manual" -or $triggerMode -eq "glob") {
        # Cursor：按需/glob 规则仅 description + globs，不设 alwaysApply
    }
    elseif ($null -ne $alwaysApply) {
        [void]$newFm.AppendLine("alwaysApply: $(if ($alwaysApply) { 'true' } else { 'false' })")
    }
    elseif ($triggerMode -eq "always_on") {
        [void]$newFm.AppendLine("alwaysApply: true")
    }
    if ($globs -ne "") { [void]$newFm.AppendLine("globs: $globs") }
    [void]$newFm.AppendLine("---")
    return $newFm.ToString().TrimEnd() + "`n" + $body.TrimStart("`n")
}

function Convert-ToNativeRuleContent {
    param(
        [string]$Content,
        [string]$Format
    )
    $normalized = Normalize-RuleSourceContent -Content $Content
    switch ($Format) {
        "cursor" { return Convert-ToCursorRuleContent -Content $normalized }
        "trae"   { return $normalized }
        default  { return Convert-Frontmatter -Content $normalized -Format $Format }
    }
}

function Write-RuleDeployFile {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$Content,
        [string]$ScopeLabel = "rules"
    )
    if ($DryRun) { return $true }
    $dir = Split-Path $TargetPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $shouldWrite = $Force -or -not (Test-Path $TargetPath)
    # L0 关键入口：-Force 或 Scope 为 L0 时始终重写（刷新 Cursor 索引/UI）
    if ($ScopeLabel -eq "L0") { $shouldWrite = $true }
    if (-not $shouldWrite) {
        $existing = [System.IO.File]::ReadAllText($TargetPath, [System.Text.Encoding]::UTF8)
        if ($existing -ne $Content) {
            $shouldWrite = $true
        }
        elseif (Test-SourceNewerThanTarget -SourcePath $SourcePath -TargetPath $TargetPath) {
            $shouldWrite = $true
        }
    }
    if (-not $shouldWrite) { return $false }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($TargetPath)
    $rulesDir = Split-Path $TargetPath -Parent
    $isRulesDirDeploy = ($ScopeLabel -match 'rules$') -or ($rulesDir -match '[\\/]rules$')
    if ($isRulesDirDeploy) {
        # 先删同 basename 全部变体（.md / .mdc / 大小写），再写入，防 Cursor UI 重复
        Remove-AllRuleVariantsByBaseName -TargetRulesDir $rulesDir -BaseName $baseName -ScopeLabel $ScopeLabel
    }
    else {
        $ext = [System.IO.Path]::GetExtension($TargetPath)
        Remove-ScopedSameTypeTarget -TargetPath $TargetPath -ScopeLabel $ScopeLabel -RequiredExt $ext | Out-Null
    }
    [System.IO.File]::WriteAllText($TargetPath, $Content, [System.Text.Encoding]::UTF8)
    return $true
}

function Write-RouterDeployFile {
    param(
        [string]$Path,
        [string]$Content
    )
    $routerSource = Join-Path $CLAUDE_DIR $ROUTER_SOURCE_FILE
    return Write-RuleDeployFile -SourcePath $routerSource -TargetPath $Path -Content $Content -ScopeLabel "rules"
}

function Cleanup-ClaudeRulesDeployArtifacts {
    <#
    .SYNOPSIS
        清理历史上误写入 ~/.claude/rules/ 的路由部署产物（同步仅针对编辑器，不修改 Claude Code 源 rules）
    #>
    $rulesDir = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesDir)) { return }
    foreach ($name in $ROUTER_DEPLOY_WHITELIST) {
        $p = Join-Path $rulesDir $name
        if (Test-Path $p) {
            if ($DryRun) { Write-Fix "[预演] 将删除 Claude Code 源目录中的部署产物: rules/$name" }
            else { Remove-Item $p -Force; Write-Fix "已删除 Claude Code 源目录中的部署产物: rules/$name"; $script:stats.Removed++ }
        }
    }
}

function Deploy-RouterRule {
    param(
        [hashtable]$RulesConfig
    )
    $srcContent = Get-RouterSourceContent
    if (-not $srcContent) { return $false }
    $targetDir = $RulesConfig.TargetDir
    $content = if ($RulesConfig.Format -eq "cursor" -or $RulesConfig.Format -eq "trae") {
        $srcContent
    }
    else {
        Convert-Frontmatter -Content $srcContent -Format $RulesConfig.Format
    }
    $routerPath = Join-Path $targetDir "$ROUTER_DEPLOY_BASENAME$($RulesConfig.Ext)"
    if (Write-RouterDeployFile -Path $routerPath -Content $content) {
        Write-Fix "路由规则已部署 → $routerPath"
        $script:stats.Files++
        return $true
    }
    return $false
}

function Deploy-ClaudeMdRule {
    param(
        [hashtable]$RulesConfig
    )
    <#
    .SYNOPSIS
        将 ~/.claude/CLAUDE.md 部署到编辑器 rules/（Cursor: CLAUDE.mdc）
    #>
    $src = Join-Path $CLAUDE_DIR "CLAUDE.md"
    if (-not (Test-Path $src)) {
        Write-Skip "源 CLAUDE.md 缺失，跳过 rules 部署"
        return $false
    }
    $srcContent = [System.IO.File]::ReadAllText($src, [System.Text.Encoding]::UTF8)
    $content = Convert-ToNativeRuleContent -Content $srcContent -Format $RulesConfig.Format
    $claudeDesc = "Claude 全局配置 — 五柱×五阶段×三横切"
    if ($RulesConfig.Format -in @("cursor", "windsurf")) {
        if ($content -match '(?ms)^---\r?\n(.*?)\r?\n---\r?\n(.*)$') {
            $fm = $Matches[1]
            $body = $Matches[2]
            if ($fm -match '(?m)^description:\s*$') {
                $fm = $fm -replace '(?m)^description:\s*$', "description: $claudeDesc"
            }
            elseif ($fm -notmatch '(?m)^description:\s+\S') {
                $fm = "description: $claudeDesc`n" + $fm.TrimEnd()
            }
            $body = $body -replace '(?m)^description:\s*Claude 全局配置[^\r\n]*\r?\n', ''
            $content = "---`n$($fm.TrimEnd())`n---`n$($body.TrimStart())"
        }
    }
    $targetPath = Join-Path $RulesConfig.TargetDir "CLAUDE$($RulesConfig.Ext)"
    if ($DryRun) {
        Write-Ok "[预演] 将部署 CLAUDE.md → rules/CLAUDE$($RulesConfig.Ext)"
        return $true
    }
    if (Write-RuleDeployFile -SourcePath $src -TargetPath $targetPath -Content $content -ScopeLabel "rules") {
        Write-Fix "CLAUDE.md 已部署 → $targetPath"
        $script:stats.Files++
        return $true
    }
    Write-Ok "CLAUDE$($RulesConfig.Ext) 已是最新"
    return $false
}

function Deploy-L0KeyEntries {
    param(
        [hashtable]$RulesConfig,
        [string]$EditorName = "cursor"
    )
    <#
    .SYNOPSIS
        L0 关键入口（ROUTER → CLAUDE → CORE → CURSOR-EDITOR）：
        ① 批量删除同 basename 全部变体（.md/.mdc/大小写）
        ② 按序强制部署，防 Cursor Settings 重复/过期
    #>
    $targetRulesDir = $RulesConfig.TargetDir
    $ext = $RulesConfig.Ext
    $format = $RulesConfig.Format

    if (-not (Test-Path $targetRulesDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $targetRulesDir -Force | Out-Null
    }

    Write-Info "L0 关键入口 [$EditorName]：先删同类型同名，再部署"

    foreach ($baseName in $PROJECT_L0_BASE_NAMES) {
        if ($DryRun) {
            if (-not (Test-Path $targetRulesDir)) { continue }
            $variants = @(Get-ChildItem $targetRulesDir -File -Force -ErrorAction SilentlyContinue |
                Where-Object { $_.BaseName -ieq $baseName })
            if ($variants.Count -gt 0) {
                Write-Fix "[预演] 将删除 L0/$baseName.* ($($variants.Count) 个变体)"
            }
        }
        else {
            Remove-AllRuleVariantsByBaseName -TargetRulesDir $targetRulesDir -BaseName $baseName -ScopeLabel "L0"
        }
    }

    if ($DryRun) {
        Write-Ok "[预演] 将部署 L0: 00-CLAUDE-ROUTER$ext, CLAUDE$ext, CORE$ext$(if ($format -eq 'cursor') { ", CURSOR-EDITOR$ext" })"
        return
    }

    Deploy-RouterRule -RulesConfig $RulesConfig | Out-Null
    Deploy-ClaudeMdRule -RulesConfig $RulesConfig | Out-Null

    $coreSrc = Join-Path $CLAUDE_DIR "rules\CORE.md"
    if (Test-Path $coreSrc) {
        $raw = [System.IO.File]::ReadAllText($coreSrc, [System.Text.Encoding]::UTF8)
        $converted = Convert-ToNativeRuleContent -Content $raw -Format $format
        $corePath = Join-Path $targetRulesDir "CORE$ext"
        if (Write-RuleDeployFile -SourcePath $coreSrc -TargetPath $corePath -Content $converted -ScopeLabel "L0") {
            Write-Fix "L0 CORE 已部署 → $corePath"
            $script:stats.Files++
        }
    }
    else {
        Write-Skip "源 rules/CORE.md 缺失，跳过 L0 CORE"
    }

    if ($format -eq "cursor") {
        $cursorEditorSrc = Join-Path $CLAUDE_DIR "templates\cursor-guard\rules\CURSOR-EDITOR.mdc"
        if (Test-Path $cursorEditorSrc) {
            $ceContent = [System.IO.File]::ReadAllText($cursorEditorSrc, [System.Text.Encoding]::UTF8)
            $cePath = Join-Path $targetRulesDir "CURSOR-EDITOR$ext"
            if (Write-RuleDeployFile -SourcePath $cursorEditorSrc -TargetPath $cePath -Content $ceContent -ScopeLabel "L0") {
                Write-Fix "L0 CURSOR-EDITOR 已部署 → $cePath"
                $script:stats.Files++
            }
        }
        else {
            Write-Skip "templates/cursor-guard/rules/CURSOR-EDITOR.mdc 缺失"
        }
    }
}

function Cleanup-StaleRulesAlternateFormat {
    param(
        [hashtable]$RulesConfig,
        [string[]]$ValidBaseNames,
        [string]$TargetRulesDir
    )
    <#
    .SYNOPSIS
        Cursor 等 .mdc 编辑器：移除同 basename 的旧 .md 软链，避免 Cursor 继续加载过期副本
        仅在 rules/ 范围内操作，不跨 skills/agents
    #>
    if ($RulesConfig.Ext -ne ".mdc") { return }
    if (-not (Test-Path $TargetRulesDir) -or (IsLink $TargetRulesDir)) { return }

    $protected = @($EDITOR_RULE_PROTECT)
    foreach ($base in $ValidBaseNames) {
        $staleMd = Join-Path $TargetRulesDir "$base.md"
        if ((Test-Path $staleMd) -and ("$base.md" -notin $protected)) {
            Remove-ScopedSameTypeTarget -TargetPath $staleMd -ScopeLabel "rules" -RequiredExt ".md" | Out-Null
        }
    }
    foreach ($name in $CLAUDE_RULE_DEPLOY_NAMES) {
        if ($name.EndsWith(".md", [StringComparison]::OrdinalIgnoreCase)) {
            $stale = Join-Path $TargetRulesDir $name
            if (Test-Path $stale) {
                Remove-ScopedSameTypeTarget -TargetPath $stale -ScopeLabel "rules" -RequiredExt ".md" | Out-Null
            }
        }
    }
}

function Sync-EditorRulesIndex {
    param(
        [string]$EditorName
    )
    if (-not $NATIVE_RULES_DIR_MAP.ContainsKey($EditorName)) { return }
    $cfg = $NATIVE_RULES_DIR_MAP[$EditorName]
    $targetRulesDir = $cfg.TargetDir
    $ext = $cfg.Ext
    $format = $cfg.Format
    $rulesSrc = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesSrc)) {
        Write-Skip "源 rules 目录缺失，跳过编辑器 rules 同步"
        return
    }

    if ((Test-Path $targetRulesDir) -and (IsLink $targetRulesDir)) {
        if ($DryRun) { Write-Fix "[预演] 将移除 rules/ 联接（改为编辑器实体目录+原生规则）" }
        else { Remove-DirTarget -Path $targetRulesDir -Editor $EditorName -Label "rules/" }
    }

    if (-not (Test-Path $targetRulesDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $targetRulesDir -Force | Out-Null
    }

    # L0 关键入口优先：先删同名变体，再部署 ROUTER/CLAUDE/CORE/CURSOR-EDITOR
    Deploy-L0KeyEntries -RulesConfig $cfg -EditorName $EditorName

    # 清理非L0的过期规则文件（v14.5+：仅同步L0关键入口，详细rules通过L0路由按需Read加载）
    if ((Test-Path $targetRulesDir) -and -not (IsLink $targetRulesDir)) {
        $existing = Get-ChildItem $targetRulesDir -File -Force -ErrorAction SilentlyContinue
        foreach ($ef in $existing) {
            if ($ef.BaseName -in $PROJECT_L0_BASE_NAMES) { continue }
            if ($DryRun) {
                Write-Fix "[预演] 将删除非L0规则 $ef.Name"
            }
            else {
                Remove-ScopedSameTypeTarget -TargetPath $ef.FullName -ScopeLabel "rules" -RequiredExt $ef.Extension | Out-Null
                Write-Fix "已删除非L0规则 $ef.Name（L0路由按需加载）"
                $script:stats.Removed++
            }
        }
    }

    $ruleFiles = Get-ChildItem $rulesSrc -Filter "*.md" |
        Where-Object { $_.Name -ne "README.md" } |
        Sort-Object Name
    $validBaseNames = @($ruleFiles | ForEach-Object { $_.BaseName })

    if (-not $DryRun) {
        Cleanup-StaleRulesAlternateFormat -RulesConfig $cfg -ValidBaseNames $validBaseNames -TargetRulesDir $targetRulesDir
        if ($EditorName -eq "devin") {
            Sync-DevinGlobalRules -RuleFiles $ruleFiles
        }
    }
}

function Sync-CursorProjectRules {
    <#
    .SYNOPSIS
        v14.5+：取消项目级规则部署（~/.claude/.cursor/rules/），仅保留个人级（~/.cursor/rules/）。
        清理项目级目录中的所有规则文件，避免 Cursor 双落点导致双份显示。
        详细 rules 通过 L0 路由（ROUTER→CLAUDE→CORE）按需 Read 加载。
    #>
    $targetRulesDir = $CURSOR_PROJECT_RULES_CONFIG.TargetDir

    if (-not (Test-Path $targetRulesDir)) { return }

    Write-Info "Cursor 项目规则清理 → $targetRulesDir（仅保留个人级 ~/.cursor/rules/）"

    if ((Test-Path $targetRulesDir) -and (IsLink $targetRulesDir)) {
        if ($DryRun) { Write-Fix "[预演] 将删除 Cursor 项目 rules/ 联接" }
        else {
            Remove-DirTarget -Path $targetRulesDir -Editor "cursor-project" -Label "rules/"
            Write-Fix "已删除 Cursor 项目 rules/ 联接（双份源）"
            $script:stats.Removed++
        }
        return
    }

    $existingFiles = Get-ChildItem $targetRulesDir -File -Force -ErrorAction SilentlyContinue
    if ($existingFiles.Count -eq 0) {
        if ($DryRun) { Write-Fix "[预演] 将删除空的项目级 rules/ 目录" }
        else {
            Remove-Item $targetRulesDir -Force -ErrorAction SilentlyContinue
            Write-Fix "已删除空的项目级 rules/ 目录"
        }
        return
    }

    foreach ($ef in $existingFiles) {
        if ($DryRun) {
            Write-Fix "[预演] 将删除项目级规则 $ef.Name（个人级 ~/.cursor/rules/ 已有L0入口）"
        }
        else {
            Remove-Item $ef.FullName -Force -ErrorAction SilentlyContinue
            Write-Fix "已删除项目级规则 $ef.Name（避免双份显示）"
            $script:stats.Removed++
        }
    }

    if (-not $DryRun) {
        $remaining = Get-ChildItem $targetRulesDir -File -Force -ErrorAction SilentlyContinue
        if ($remaining.Count -eq 0) {
            Remove-Item $targetRulesDir -Force -ErrorAction SilentlyContinue
            Write-Fix "已清空项目级 rules/ 目录"
        }
        Write-SyncModeJson -TargetDir $CLAUDE_CURSOR_PROJECT_DIR -Mode $(if ($Full) { "full" } else { "index" })
    }
}


function Cleanup-DevinMisplacedRulesDir {
    <#
    .SYNOPSIS
        Devin 不读 ~/.devin/rules/（那是编辑器用户目录，类似 ~/.cursor/extensions）。
        误部署在此处的 rules 会导致 Devin UI 显示为空。
    #>
    if (-not (Test-Path $DEVIN_MISPLACED_RULES_DIR)) { return }
    Write-Host ""
    Write-Host "  -- devin-cleanup (误路径 ~/.devin/rules/) ----------------" -ForegroundColor DarkGray
    if ($DryRun) {
        Write-Fix "[预演] 将删除误路径 ~/.devin/rules/"
        return
    }
    Remove-Item $DEVIN_MISPLACED_RULES_DIR -Recurse -Force -ErrorAction SilentlyContinue
    Write-Fix "已删除误路径 ~/.devin/rules/（Devin 读 ~/.claude/.devin/rules/）"
    $script:stats.Removed++
}

function Get-LinkTargetPath {
    param([string]$Path)
    if (-not (IsLink $Path)) { return $null }
    $actual = (Get-Item $Path -Force).Target
    if ($actual -is [array]) { $actual = $actual[0] }
    return $actual
}

function Clear-CursorProjectLegacyArtifacts {
    <#
    .SYNOPSIS
        v14.5+：清理 ~/.claude/.cursor/ 项目级目录中的遗留联接和规则文件。
        项目级规则已迁移至个人级 ~/.cursor/rules/，避免双份显示。
    #>
    if (-not (Test-Path $CLAUDE_CURSOR_PROJECT_DIR)) { return }
    foreach ($stale in @("skills", "agents", "hooks", "commands", "scripts")) {
        $sp = Join-Path $CLAUDE_CURSOR_PROJECT_DIR $stale
        if ((Test-Path $sp) -and (IsLink $sp)) {
            if ($DryRun) { Write-Fix "[预演] 将删除 Cursor 项目遗留联接 .cursor/$stale" }
            else {
                Remove-DirTarget -Path $sp -Editor "cursor-project" -Label ".cursor/$stale"
            }
        }
    }
    # v14.5+：清理项目级 rules/ 目录（已迁移至个人级 ~/.cursor/rules/）
    $projRulesDir = Join-Path $CLAUDE_CURSOR_PROJECT_DIR "rules"
    if ((Test-Path $projRulesDir) -and -not (IsLink $projRulesDir)) {
        $projRules = Get-ChildItem $projRulesDir -File -Force -ErrorAction SilentlyContinue
        if ($projRules.Count -gt 0) {
            foreach ($pf in $projRules) {
                if ($DryRun) { Write-Fix "[预演] 将删除项目级规则 .cursor/rules/$($pf.Name)" }
                else {
                    Remove-Item $pf.FullName -Force -ErrorAction SilentlyContinue
                    Write-Fix "已删除项目级规则 .cursor/rules/$($pf.Name)"
                    $script:stats.Removed++
                }
            }
        }
        $remaining = Get-ChildItem $projRulesDir -File -Force -ErrorAction SilentlyContinue
        if ($remaining.Count -eq 0 -and -not $DryRun) {
            Remove-Item $projRulesDir -Force -ErrorAction SilentlyContinue
            Write-Fix "已清空项目级 .cursor/rules/ 目录"
        }
    }
    elseif ((Test-Path $projRulesDir) -and (IsLink $projRulesDir)) {
        if ($DryRun) { Write-Fix "[预演] 将删除项目级 rules/ 联接" }
        else {
            Remove-DirTarget -Path $projRulesDir -Editor "cursor-project" -Label ".cursor/rules/"
        }
    }
}

function Update-CodeArtsDoerMetadata {
    param([string]$RulesDir)
    if (-not (Test-Path $RulesDir)) { return }
    $entries = [System.Collections.Generic.List[hashtable]]::new()
    foreach ($f in Get-ChildItem $RulesDir -Filter "*.mdc" -File -ErrorAction SilentlyContinue | Sort-Object Name) {
        $content = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
        $body = $content
        $triggerType = "manual"
        $desc = $f.BaseName
        if ($content -match '(?ms)^---\r?\n(.*?)\r?\n---\r?\n(.*)$') {
            $fm = $Matches[1]
            $body = $Matches[2].Trim()
            if ($fm -match '(?m)alwaysApply:\s*true' -or $fm -match '(?m)trigger:\s*always_on') {
                $triggerType = "always"
            }
            if ($fm -match '(?m)^description:\s*(.+)') {
                $desc = $Matches[1].Trim().Trim("'").Trim('"')
            }
        }
        if ($desc.Length -gt 200) { $desc = $desc.Substring(0, 200) }
        $entries.Add(@{
            filePath    = $f.Name
            name        = $f.BaseName
            description = $desc
            content     = $body
            triggerType = $triggerType
            source      = "user"
        })
    }
    if ($entries.Count -eq 0) { return }
    $metaPath = Join-Path $RulesDir "metadata.properties"
    if ($DryRun) {
        Write-Ok "[预演] 将更新 metadata.properties ($($entries.Count) 条)"
        return
    }
    $json = ConvertTo-Json -InputObject @($entries) -Compress -Depth 6
    [System.IO.File]::WriteAllText($metaPath, "projectExpert=$json", [System.Text.Encoding]::UTF8)
    Write-Fix "metadata.properties 已更新 ($($entries.Count) 条) → $RulesDir"
    $script:stats.Files++
}

function Sync-CodeArtsDoerRules {
    <#
    .SYNOPSIS
        v14.5+：华为云码道 CodeArts Doer 规则同步 — 仅L0入口。
        个人级：~/.config/codeartsdoer/rule/*.mdc（内核 load user rules 路径）
        项目级：仅清理（避免双份显示），不再部署。
        详细 rules 通过 L0 路由（ROUTER→CLAUDE→CORE）按需 Read 加载。
    #>
    Write-Host ""
    Write-Host "  -- codeartsdoer ----------------------------------------" -ForegroundColor DarkGray

    $rulesSrc = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesSrc)) {
        Write-Skip "源 rules 缺失，跳过 CodeArts 码道"
        return
    }

    # 个人级：仅部署 L0 入口
    $targetDir = $CODEARTS_DOER_PERSONAL_RULES_DIR
    if (-not (Test-Path $targetDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    Write-Info "CodeArts [personal] → $targetDir"

    foreach ($baseName in $CODEARTS_L0_BASE_NAMES) {
        if ($DryRun) { continue }
        Remove-AllRuleVariantsByBaseName -TargetRulesDir $targetDir -BaseName $baseName -ScopeLabel "codearts-personal"
    }

    $routerSrc = Join-Path $CLAUDE_DIR $ROUTER_SOURCE_FILE
    if (Test-Path $routerSrc) {
        $raw = [System.IO.File]::ReadAllText($routerSrc, [System.Text.Encoding]::UTF8)
        $converted = Convert-ToNativeRuleContent -Content $raw -Format "cursor"
        $dst = Join-Path $targetDir "00-CLAUDE-ROUTER.mdc"
        if (-not $DryRun -and (Write-RuleDeployFile -SourcePath $routerSrc -TargetPath $dst -Content $converted -ScopeLabel "codearts-personal")) {
            Write-Fix "codearts-personal/00-CLAUDE-ROUTER.mdc 已部署"
            $script:stats.Files++
        }
    }

    $claudeSrc = Join-Path $CLAUDE_DIR "CLAUDE.md"
    if (Test-Path $claudeSrc) {
        $raw = [System.IO.File]::ReadAllText($claudeSrc, [System.Text.Encoding]::UTF8)
        $converted = Convert-ToNativeRuleContent -Content $raw -Format "cursor"
        $dst = Join-Path $targetDir "CLAUDE.mdc"
        if (-not $DryRun -and (Write-RuleDeployFile -SourcePath $claudeSrc -TargetPath $dst -Content $converted -ScopeLabel "codearts-personal")) {
            Write-Fix "codearts-personal/CLAUDE.mdc 已部署"
            $script:stats.Files++
        }
    }

    $coreSrc = Join-Path $rulesSrc "CORE.md"
    if (Test-Path $coreSrc) {
        $raw = [System.IO.File]::ReadAllText($coreSrc, [System.Text.Encoding]::UTF8)
        $converted = Convert-ToNativeRuleContent -Content $raw -Format "cursor"
        $dst = Join-Path $targetDir "CORE.mdc"
        if (-not $DryRun -and (Write-RuleDeployFile -SourcePath $coreSrc -TargetPath $dst -Content $converted -ScopeLabel "codearts-personal")) {
            Write-Fix "codearts-personal/CORE.mdc 已部署"
            $script:stats.Files++
        }
    }

    # 清理个人级非L0规则
    if ((Test-Path $targetDir) -and -not $DryRun) {
        $existing = Get-ChildItem $targetDir -File -Force -ErrorAction SilentlyContinue
        foreach ($ef in $existing) {
            if ($ef.BaseName -in $CODEARTS_L0_BASE_NAMES -or $ef.Name -eq "metadata.properties") { continue }
            Remove-ScopedSameTypeTarget -TargetPath $ef.FullName -ScopeLabel "codearts-personal" -RequiredExt $ef.Extension | Out-Null
            Write-Fix "已删除非L0规则 codearts-personal/$($ef.Name)"
            $script:stats.Removed++
        }
    }

    if (-not $DryRun) {
        Update-CodeArtsDoerMetadata -RulesDir $targetDir
    }

    # 注：~/.codeartsdoer/cache/user/rule/ 是内核运行时缓存，启动时会被重置为空。
    # 真正的配置源是 ~/.config/codeartsdoer/rule/（上方 $targetDir），内核从此读取。
    # 因此不再同步到 cache 路径，避免写入后被覆盖。

    # 项目级：仅清理（不再部署，避免双份显示）
    $projDir = $CODEARTS_DOER_PROJECT_RULES_DIR
    if (Test-Path $projDir) {
        Write-Info "CodeArts [project] → $projDir（仅清理）"
        $projFiles = Get-ChildItem $projDir -File -Force -ErrorAction SilentlyContinue
        foreach ($pf in $projFiles) {
            if ($DryRun) {
                Write-Fix "[预演] 将删除项目级规则 codearts-project/$($pf.Name)"
            }
            else {
                Remove-Item $pf.FullName -Force -ErrorAction SilentlyContinue
                Write-Fix "已删除项目级规则 codearts-project/$($pf.Name)"
                $script:stats.Removed++
            }
        }
        $remaining = Get-ChildItem $projDir -File -Force -ErrorAction SilentlyContinue
        if ($remaining.Count -eq 0 -and -not $DryRun) {
            Remove-Item $projDir -Force -ErrorAction SilentlyContinue
            Write-Fix "已清空项目级 .codeartsdoer/rule/ 目录"
        }
    }
}

function Cleanup-CodeArtsAgentLegacyRules {
    <#
    .SYNOPSIS
        清理误同步到 AppData\codearts-agent\User\rules\ 的副本（码道不读此路径）
    #>
    if (-not (Test-Path $CODEARTS_AGENT_LEGACY_RULES_DIR)) { return }
    Write-Host ""
    Write-Host "  -- codearts-agent-legacy (误路径清理) ------------------" -ForegroundColor DarkGray
    if ($DryRun) {
        Write-Fix "[预演] 将删除误路径 $CODEARTS_AGENT_LEGACY_RULES_DIR"
        return
    }
    Remove-Item $CODEARTS_AGENT_LEGACY_RULES_DIR -Recurse -Force -ErrorAction SilentlyContinue
    Write-Fix "已删除误路径 codearts-agent/User/rules/（码道读 ~/.config/codeartsdoer/rule/）"
    $script:stats.Removed++
}

function Cleanup-CodeArtsLegacyPersonalRules {
    <#
    .SYNOPSIS
        清理误同步到 ~/.codeartsdoer/rule/ 的副本（UI 文案误导；内核读 ~/.config/codeartsdoer/rule/）
    #>
    if (-not (Test-Path $CODEARTS_DOER_LEGACY_PERSONAL_RULES_DIR)) { return }
    $legacyFiles = @(Get-ChildItem $CODEARTS_DOER_LEGACY_PERSONAL_RULES_DIR -File -Force -ErrorAction SilentlyContinue)
    if ($legacyFiles.Count -eq 0) { return }

    Write-Host ""
    Write-Host "  -- codearts-legacy-personal (误路径 ~/.codeartsdoer/rule/) ---" -ForegroundColor DarkGray
    foreach ($f in $legacyFiles) {
        if ($DryRun) {
            Write-Fix "[预演] 将删除误路径 ~/.codeartsdoer/rule/$($f.Name)"
            continue
        }
        Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
        Write-Fix "已删除误路径 ~/.codeartsdoer/rule/$($f.Name)"
        $script:stats.Removed++
    }
}

function Sync-DeployRouterArtifacts {
    <#
    .SYNOPSIS
        全量模式：向各编辑器原生 rules 目录补部署路由规则（源 ~/.claude/CLAUDE-ROUTER.mdc，不写回 Claude Code rules/）
    #>
    if (-not $Full) { return }
    foreach ($entry in $NATIVE_RULES_DIR_MAP.GetEnumerator()) {
        $editor = $entry.Key
        $cfg = $entry.Value
        if ((Test-Path $cfg.TargetDir) -and (IsLink $cfg.TargetDir)) { continue }
        if (-not (Test-Path (Split-Path $cfg.TargetDir -Parent))) { continue }
        Deploy-RouterRule -RulesConfig $cfg | Out-Null
    }
}

function Sync-EditorTarget {
    param(
        [string]$EditorName,
        [string]$TargetDir
    )

    Write-Host ""
    Write-Host "  -- $EditorName -------------------------------------------" -ForegroundColor DarkGray

    if (-not (Test-Path $TargetDir)) {
        Write-Skip "未找到目标目录，跳过"
        $script:stats.Skipped++
        return
    }

    if ($Scope -eq "rules") {
        Sync-EditorRulesIndex -EditorName $EditorName
        return
    }

    if ($Scope -eq "indexes") {
        foreach ($stale in $STALE_LINKS) {
            $sp = Join-Path $TargetDir $stale
            if ((Test-Path $sp) -and (IsLink $sp)) {
                if ($DryRun) { Write-Fix "[预演] 将删除陈旧 $stale/ 链接" }
                else { Remove-Item $sp -Force; Write-Fix "已删除陈旧 $stale/ 软链接"; $script:stats.Removed++ }
            }
        }
        foreach ($file in $SYNC_FILES) {
            $src = Join-Path $CLAUDE_DIR $file
            $dst = Join-Path $TargetDir $file
            Sync-SingleFile -Source $src -Target $dst -Label $file
        }
        if (-not $DryRun) {
            Write-SyncModeJson -TargetDir $TargetDir -Mode $(if ($Full) { "full" } else { "index" })
        }
        return
    }

    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $TargetDir $stale
        if ((Test-Path $sp) -and (IsLink $sp)) {
            if ($DryRun) { Write-Fix "[预演] 将删除陈旧 $stale/ 链接" }
            else { Remove-Item $sp -Force; Write-Fix "已删除陈旧 $stale/ 软链接"; $script:stats.Removed++ }
        }
    }

    foreach ($file in $SYNC_FILES) {
        $src = Join-Path $CLAUDE_DIR $file
        $dst = Join-Path $TargetDir $file
        Sync-SingleFile -Source $src -Target $dst -Label $file
    }

    if ($Full) {
        foreach ($dir in $SYNC_DIRS_FULL_LINK) {
            $src = Join-Path $CLAUDE_DIR $dir
            $dst = Join-Path $TargetDir $dir
            Sync-DirJunction -Source $src -Target $dst -Label "$dir/" -Editor $EditorName
        }

        foreach ($dir in $SYNC_DIRS_FULL_NATIVE) {
            $dst = Join-Path $TargetDir $dir
            if ((Test-Path $dst) -and (IsLink $dst)) {
                if ($DryRun) { Write-Fix "[预演] 将移除 $dir/ 联接（Full 原生转换）" }
                else { Remove-DirTarget -Path $dst -Editor $EditorName -Label "$dir/" }
            }
        }

        if ($NATIVE_RULES_DIR_MAP.ContainsKey($EditorName)) {
            $rulesConfig = $NATIVE_RULES_DIR_MAP[$EditorName]
            if (-not $DryRun) {
                Sync-NativeRulesFiles -TargetDir $TargetDir -EditorName $EditorName -RulesConfig $rulesConfig
            }
            else {
                Write-Ok "[预演] 将生成 rules 原生 $($rulesConfig.Ext) 文件（$($rulesConfig.Format) 格式）"
            }
        }

        if ($NATIVE_SKILLS_DIR_MAP.ContainsKey($EditorName)) {
            $skillsConfig = $NATIVE_SKILLS_DIR_MAP[$EditorName]
            if (-not $DryRun) {
                Sync-NativeSkillsFiles -EditorName $EditorName -SkillsConfig $skillsConfig
            }
            else {
                Write-Ok "[预演] 将生成 skills-native/ 原生 SKILL.md（$($skillsConfig.Format) 格式）"
            }
        }

        Write-SyncModeJson -TargetDir $TargetDir -Mode "full"
    }
    else {
        foreach ($dir in $SYNC_DIRS) {
            $src = Join-Path $CLAUDE_DIR $dir
            $dst = Join-Path $TargetDir $dir
            Sync-DirJunction -Source $src -Target $dst -Label "$dir/" -Editor $EditorName
        }

        Sync-EditorRulesIndex -EditorName $EditorName

        Cleanup-FullNativeArtifacts -TargetDir $TargetDir -EditorName $EditorName
        Write-SyncModeJson -TargetDir $TargetDir -Mode "index"
    }
}

function Sync-NativeRulesFiles {
    param(
        [string]$TargetDir,
        [string]$EditorName,
        [hashtable]$RulesConfig
    )
    <#
    .SYNOPSIS
        将 ~/.claude/rules/RULES_*.md 转换为编辑器原生的规则格式
        使用各编辑器真正识别的路径：
        - Cursor/Qoder: ~/.cursor/rules/*.mdc（v14.5+ 仅L0入口）
        - Devin: ~/.claude/.devin/rules/*.md (每个规则一个文件，遵守字符限制)
        - Trae: ~/.trae/user_rules/*.md (每个规则一个文件，alwaysApply格式)
    #>
    $rulesSrc = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesSrc)) {
        Write-Skip "源 rules 目录缺失，跳过原生规则文件生成"
        return
    }

    $ruleFiles = Get-ChildItem $rulesSrc -Filter "*.md" |
        Where-Object { $_.Name -ne "README.md" } |
        Sort-Object Name
    if ($ruleFiles.Count -eq 0) {
        Write-Skip "无规则文件，跳过原生规则文件生成"
        return
    }

    $format = $RulesConfig.Format
    $ext = $RulesConfig.Ext
    $targetRulesDir = $RulesConfig.TargetDir

    # 确保目标目录存在
    if (-not (Test-Path $targetRulesDir) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $targetRulesDir -Force | Out-Null
    }

    # 如果目标目录中有旧的 rules/ 联接，需要删除
    if ((Test-Path $targetRulesDir) -and (IsLink $targetRulesDir)) {
        if (-not $DryRun) {
            & cmd.exe /c "rmdir `"$targetRulesDir`"" 2>&1 | Out-Null
            New-Item -ItemType Directory -Path $targetRulesDir -Force | Out-Null
            Write-Fix "已删除旧的联接并创建实体目录"
        }
    }

    # 仅清理 rules 目录内同目标扩展名的过期文件（不删 .md/.mdc 等其他类型）
    if ((Test-Path $targetRulesDir) -and -not (IsLink $targetRulesDir)) {
        $validBaseNames = @($ruleFiles | ForEach-Object { $_.BaseName -replace '^RULES_','' })
        $existing = Get-ChildItem $targetRulesDir -Filter "*$ext" -ErrorAction SilentlyContinue
        foreach ($ef in $existing) {
            if ($ef.Name -in $EDITOR_RULE_PROTECT) { continue }
            $base = $ef.BaseName -replace '^RULES_',''
            if ($base -notin $validBaseNames) {
                Remove-ScopedSameTypeTarget -TargetPath $ef.FullName -ScopeLabel "rules" -RequiredExt $ext | Out-Null
            }
        }
    }

    $syncedCount = 0
    $skippedCount = 0
    $truncatedCount = 0
    $totalChars = 0

    foreach ($rf in $ruleFiles) {
        $category = $rf.BaseName -replace "^RULES_", ""

        # v14.5+：Cursor/Qoder 仅部署 L0 入口，非 L0 通过路由按需 Read
        if ($format -eq "cursor" -and $category -notin $PROJECT_L0_BASE_NAMES) {
            continue
        }

        $srcContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)

        $targetFileName = "$category$ext"
        $targetPath = Join-Path $targetRulesDir $targetFileName

        $convertedContent = Convert-ToNativeRuleContent -Content $srcContent -Format $format

        if ($format -eq "cursor" -and $category -eq "CORE") {
            $convertedContent += @"

## 全量模式 Skills 路径

技能按 name Read：`~/.cursor/skills-native/<name>/SKILL.md`
完整源：`~/.claude/skills/<name>/SKILL.md`
"@
        }

        # Devin 字符限制检查
        if ($format -eq "windsurf") {
            if ($convertedContent.Length -gt $DEVIN_MAX_CHARS_PER_FILE) {
                $convertedContent = Truncate-ToCharLimit -Content $convertedContent -Limit $DEVIN_MAX_CHARS_PER_FILE
                $truncatedCount++
            }
            $totalChars += $convertedContent.Length
        }

        if ($DryRun) { $syncedCount++; continue }

        if (Write-RuleDeployFile -SourcePath $rf.FullName -TargetPath $targetPath -Content $convertedContent -ScopeLabel "rules") {
            $syncedCount++
        }
        else {
            $skippedCount++
        }
    }

    if ($syncedCount -gt 0) {
        Write-Fix "rules 已生成 $syncedCount 个 $ext 文件（$format 格式）→ $targetRulesDir"
        $stats.Files += $syncedCount
    }
    if (-not $DryRun) {
        Deploy-ClaudeMdRule -RulesConfig $RulesConfig | Out-Null
        Deploy-RouterRule -RulesConfig $RulesConfig | Out-Null
    }
    if ($skippedCount -gt 0) {
        Write-Ok "$skippedCount 个 $ext 规则文件已是最新"
    }
    if ($truncatedCount -gt 0) {
        Write-Warn "$truncatedCount 个规则因超过 $($DEVIN_MAX_CHARS_PER_FILE) 字符限制被截断"
    }

    # Devin: 额外同步核心规则到全局 global_rules.md
    if ($EditorName -eq "devin" -and -not $DryRun) {
        Sync-DevinGlobalRules -RuleFiles $ruleFiles
    }
}

function Sync-NativeSkillsFiles {
    param(
        [string]$EditorName,
        [hashtable]$SkillsConfig
    )
    $skillsSrc = Join-Path $CLAUDE_DIR "skills"
    if (-not (Test-Path $skillsSrc)) {
        Write-Skip "源 skills 目录缺失，跳过原生技能文件生成"
        return
    }

    $skillDirs = Get-ChildItem $skillsSrc -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
        Sort-Object Name
    if ($skillDirs.Count -eq 0) {
        Write-Skip "无技能目录，跳过原生技能文件生成"
        return
    }

    $format = $SkillsConfig.Format
    $targetRoot = $SkillsConfig.TargetDir

    if (-not (Test-Path $targetRoot) -and -not $DryRun) {
        New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
    }

    if ((Test-Path $targetRoot) -and (IsLink $targetRoot)) {
        if (-not $DryRun) {
            Remove-DirTarget -Path $targetRoot -Editor $EditorName -Label "skills-native/"
            New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
        }
    }

    $validNames = @($skillDirs | ForEach-Object { $_.Name })
    if ((Test-Path $targetRoot) -and -not (IsLink $targetRoot)) {
        $existing = Get-ChildItem $targetRoot -Directory -ErrorAction SilentlyContinue
        foreach ($ed in $existing) {
            if ($ed.Name -notin $validNames) {
                Remove-ScopedSameTypeTarget -TargetPath $ed.FullName -ScopeLabel "skills-native" -IsDirectory | Out-Null
            }
        }
    }

    $syncedCount = 0
    $skippedCount = 0
    $truncatedCount = 0

    foreach ($sd in $skillDirs) {
        $srcPath = Join-Path $sd.FullName "SKILL.md"
        $srcContent = [System.IO.File]::ReadAllText($srcPath, [System.Text.Encoding]::UTF8)
        $skillName = $sd.Name
        $targetDir = Join-Path $targetRoot $skillName
        $targetPath = Join-Path $targetDir "SKILL.md"

        $convertedContent = if ($format -eq "cursor" -or $format -eq "trae") {
            $srcContent
        }
        else {
            Convert-Frontmatter -Content $srcContent -Format $format
        }

        if ($format -eq "windsurf" -and $convertedContent.Length -gt $DEVIN_MAX_CHARS_PER_FILE) {
            $convertedContent = Truncate-ToCharLimit -Content $convertedContent -Limit $DEVIN_MAX_CHARS_PER_FILE
            $truncatedCount++
        }

        if ($DryRun) { $syncedCount++; continue }

        if (-not $Force -and (Test-Path $targetPath)) {
            $existingContent = [System.IO.File]::ReadAllText($targetPath, [System.Text.Encoding]::UTF8)
            if ($existingContent -eq $convertedContent) {
                $skippedCount++
                continue
            }
        }

        # skills-native/<name>/：先删同名目录再写入，不触碰 rules/ 等其他范围
        Remove-ScopedSameTypeTarget -TargetPath $targetDir -ScopeLabel "skills-native/$skillName" -IsDirectory | Out-Null
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        Remove-ScopedSameTypeTarget -TargetPath $targetPath -ScopeLabel "skills-native/$skillName" -RequiredExt ".md" | Out-Null
        [System.IO.File]::WriteAllText($targetPath, $convertedContent, [System.Text.Encoding]::UTF8)
        $syncedCount++
    }

    if ($syncedCount -gt 0) {
        Write-Fix "skills 已生成 $syncedCount 个 SKILL.md（$format 格式）→ $targetRoot"
        $stats.Files += $syncedCount
    }
    if ($skippedCount -gt 0) {
        Write-Ok "$skippedCount 个 SKILL.md 已是最新"
    }
    if ($truncatedCount -gt 0) {
        Write-Warn "$truncatedCount 个技能因超过 $($DEVIN_MAX_CHARS_PER_FILE) 字符限制被截断"
    }
}

function Truncate-ToCharLimit {
    param(
        [string]$Content,
        [int]$Limit
    )
    <#
    .SYNOPSIS
        将内容截断到指定字符限制，保留 frontmatter 完整
    #>
    if ($Content.Length -le $Limit) { return $Content }

    # 找到 frontmatter 结束位置
    $bodyStart = 0
    if ($Content.StartsWith("---")) {
        $secondDash = $Content.IndexOf("---", 3)
        if ($secondDash -gt 0) {
            $bodyStart = $secondDash + 3
        }
    }

    $frontmatter = $Content.Substring(0, $bodyStart)
    $body = $Content.Substring($bodyStart)

    # 截断 body
    $maxBodyLen = $Limit - $frontmatter.Length - 50  # 留 50 字符给截断提示
    if ($maxBodyLen -lt 100) { $maxBodyLen = 100 }

    $truncatedBody = $body.Substring(0, [Math]::Min($maxBodyLen, $body.Length))
    return "$frontmatter$truncatedBody`n`n<!-- 内容因字符限制被截断，完整规则请查看 ~/.claude/rules/ -->"
}

function Sync-DevinGlobalRules {
    param(
        [object[]]$RuleFiles
    )
    <#
    .SYNOPSIS
        同步 Devin 的全局 global_rules.md 单文件（仅 CLAUDE.md）
        路径：~/.codeium/windsurf/memories/global_rules.md
        限制：6000 字符/文件
        策略：
          - 优先写入完整 CLAUDE.md
          - 若超出字符限制：写入精简速查（不注入 rules/ 内容）
    #>
    $targetPath = $DEVIN_GLOBAL_RULES_FILE
    $targetDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    $claudeMdPath = Join-Path $CLAUDE_DIR "CLAUDE.md"
    $editorClaudeMd = if (Test-Path $claudeMdPath) { [System.IO.File]::ReadAllText($claudeMdPath, [System.Text.Encoding]::UTF8) } else { "" }
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("trigger: always_on")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")

    if ($editorClaudeMd -ne "") {
        [void]$sb.Append($editorClaudeMd)
    }

    $newContent = $sb.ToString()

    if ($newContent.Length -gt $DEVIN_MAX_CHARS_GLOBAL) {
        $sb2 = [System.Text.StringBuilder]::new()
        [void]$sb2.AppendLine("---")
        [void]$sb2.AppendLine("trigger: always_on")
        [void]$sb2.AppendLine("---")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("# Claude 全局配置（Devin 速查）")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("Devin 的 global_rules.md 有 6000 字符限制，因此此处为精简速查。")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("完整内容请查看：`~/.claude/CLAUDE.md` 与 `~/.claude/SPEC.md`。")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("## 铁律（R1–R11）")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("- **任务完成**：必须验证通过才算完成")
        [void]$sb2.AppendLine("- **修改确认**：Read → Edit → Read 确认")
        [void]$sb2.AppendLine("- **Bug 修复**：Grep 全项目同类模式 → 全部修复 → Grep 确认零遗漏")
        [void]$sb2.AppendLine("- **配置变更**：改接口/类型/路由 → Grep 引用 → 全部同步 → 构建验证")
        [void]$sb2.AppendLine("- **重试上限**：同一方案失败 ≤2 次，先定位根因")
        [void]$sb2.AppendLine("- **非简单任务**：头脑风暴 → 精炼 → 计划 → 执行 → 交叉验证 → 模式提取")
        [void]$sb2.AppendLine("- **交叉验证**：无证据禁止声称完成")
        [void]$sb2.AppendLine("- **高危确认**：删数据/强推 main/destroy 必须用户确认")
        [void]$sb2.AppendLine("- **命令安全**：禁止 `cd + 重定向` / 禁止 powershell -Command 包裹")
        [void]$sb2.AppendLine("- **简洁优先**：最小代码解决问题，拒绝过度设计")
        [void]$sb2.AppendLine("- **安全默认**：不信任输入、最小权限、无硬编码密钥")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("## 非简单任务：文件落点")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("- 规格/验收：`~/.claude/spec/<project>/<task>.md`（或同目录分 spec.md / design.md / tasks.md）")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("## 工具优先（Tool-First）")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("优先顺序：Skills → Agents → MCP → Rules → 再自行实现。")

        $newContent = $sb2.ToString()
        if ($newContent.Length -gt $DEVIN_MAX_CHARS_GLOBAL) {
            $newContent = $newContent.Substring(0, $DEVIN_MAX_CHARS_GLOBAL - 50) + "`n`n<!-- 内容因字符限制被截断 -->"
        }
        Write-Warn "global_rules.md 超过 $($DEVIN_MAX_CHARS_GLOBAL) 字符限制，已改为写入精简速查"
    }

    if ($DryRun) {
        Write-Fix "[预演] 将更新 global_rules.md（仅 CLAUDE.md / 或精简速查）"
        return
    }

    if (-not $Force -and (Test-Path $targetPath)) {
        $existingContent = [System.IO.File]::ReadAllText($targetPath, [System.Text.Encoding]::UTF8)
        if ($existingContent -eq $newContent) {
            Write-Ok "global_rules.md 已是最新"
            return
        }
    }

    if (Test-Path $targetPath) {
        Copy-Item $targetPath ($targetPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
    }

    Remove-ScopedSameTypeTarget -TargetPath $targetPath -ScopeLabel "devin/global_rules" -RequiredExt ".md" | Out-Null
    [System.IO.File]::WriteAllText($targetPath, $newContent, [System.Text.Encoding]::UTF8)
    Write-Fix "global_rules.md 已更新 ($($newContent.Length) 字符) → $targetPath"
    $stats.Files++
}

function Convert-Frontmatter {
    param(
        [string]$Content,
        [string]$Format
    )
    <#
    .SYNOPSIS
        将 Claude Code/Cursor 格式的 YAML frontmatter 转换为目标编辑器格式
        cursor: 保留原格式（description, alwaysApply, globs）
        windsurf(Devin): 转为 trigger 格式（trigger: always_on/model_decision/glob/manual, globs, description）
        trae: 转为 alwaysApply 格式（description, alwaysApply, globs）— 与 Cursor 格式相同
    #>
    # Trae 格式与 Cursor 相同（alwaysApply 格式），直接返回原内容
    if ($Format -eq "trae") {
        return $Content
    }

    # Windsurf(Devin) 格式：转为 trigger 格式
    if (-not $Content.StartsWith("---")) {
        # 无 frontmatter，添加默认 trigger: always_on
        return "---`ntrigger: always_on`n---`n`n$Content"
    }

    $secondDash = $Content.IndexOf("---", 3)
    if ($secondDash -eq -1) {
        return $Content
    }

    $frontmatter = $Content.Substring(3, $secondDash - 3).Trim()
    $body = $Content.Substring($secondDash + 3).TrimStart()

    # 解析 frontmatter 字段
    $description = ""
    $alwaysApply = $false
    $globs = ""
    $hasAlwaysApply = $false

    foreach ($line in $frontmatter -split "`n") {
        $line = $line.Trim()
        if ($line -match "^description:\s*(.+)") {
            $description = $Matches[1].Trim().Trim("'").Trim('"')
        }
        elseif ($line -match "^alwaysApply:\s*(true|false)") {
            $alwaysApply = $Matches[1] -eq "true"
            $hasAlwaysApply = $true
        }
        elseif ($line -match "^globs:\s*(.+)") {
            $globs = $Matches[1].Trim().Trim("'").Trim('"')
        }
    }

    # 构建 Windsurf(Devin) 格式的 frontmatter
    $newFm = [System.Text.StringBuilder]::new()

    if ($alwaysApply) {
        [void]$newFm.AppendLine("trigger: always_on")
    }
    elseif ($globs -ne "") {
        [void]$newFm.AppendLine("trigger: glob")
        [void]$newFm.AppendLine("globs: $globs")
    }
    else {
        [void]$newFm.AppendLine("trigger: model_decision")
    }

    if ($description -ne "") {
        [void]$newFm.AppendLine("description: $description")
    }

    $newFrontmatter = $newFm.ToString().TrimEnd()
    return "---`n$newFrontmatter`n---`n`n$body"
}

function Convert-RulesFrontmatter {
    param([string]$Content, [string]$Format)
    return Convert-Frontmatter -Content $Content -Format $Format
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 多编辑器同步脚本 v14.3" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录 : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标编辑器: $($EDITORS -join ', '), $($CODEARTS_EDITORS -join ', ')" -ForegroundColor DarkGray
$modeLabel = if ($Full) { "全量（agents联接 + rules/skills原生转换）" } else { "索引（7总纲 + skills/agents联接 + rules单文件链接）" }
Write-Host "  同步模式: $modeLabel" -ForegroundColor DarkGray
$syncModeLabel = if ($isAdmin) { "管理员（符号链接）" } else { "非管理员（目录联接，Junction）" }
Write-Host "  模式   : $syncModeLabel" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "  [预演] 仅预览，不写盘" -ForegroundColor Yellow }
if ($Force) { Write-Host "  [强制] 重建全部链接" -ForegroundColor Yellow }
if ($Scope -ne "all") { Write-Host "  [范围] Scope=$Scope（Cursor Guard 分段同步）" -ForegroundColor Yellow }
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

$stats = @{ Links = 0; Files = 0; Removed = 0; Errors = 0; Skipped = 0 }

if (-not $DryRun) {
    Cleanup-ClaudeRulesDeployArtifacts
}

foreach ($editor in $EDITORS | Sort-Object) {
    $targetDir = Join-Path $env:USERPROFILE ".$editor"
    Sync-EditorTarget -EditorName $editor -TargetDir $targetDir
}

# ── CodeArts 码道：~/.codeartsdoer/rule/ + ~/.claude/.codeartsdoer/rule/ ──
if ($Scope -in @("all", "rules")) {
    Sync-CursorProjectRules
    Sync-CodeArtsDoerRules
    Cleanup-CodeArtsAgentLegacyRules
    Cleanup-CodeArtsLegacyPersonalRules
}

# ── codearts-agent 旧 IDE：仅 7 总纲软链（不 sync rules 到误路径）──
foreach ($editor in $CODEARTS_EDITORS | Sort-Object) {
    $targetDir = $CODEARTS_USER_DIRS[$editor]
    if (-not $targetDir) { continue }
    if ($Scope -eq "rules") { continue }
    Write-Host ""
    Write-Host "  -- $editor (indexes only) ---------------------------" -ForegroundColor DarkGray
    if (-not (Test-Path $targetDir)) {
        Write-Skip "未找到目标目录，跳过"
        $stats.Skipped++
        continue
    }
    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $targetDir $stale
        if ((Test-Path $sp) -and (IsLink $sp)) {
            if ($DryRun) { Write-Fix "[预演] 将删除陈旧 $stale/ 链接" }
            else { Remove-Item $sp -Force; Write-Fix "已删除陈旧 $stale/ 软链接"; $stats.Removed++ }
        }
    }
    foreach ($file in $SYNC_FILES) {
        $src = Join-Path $CLAUDE_DIR $file
        $dst = Join-Path $targetDir $file
        Sync-SingleFile -Source $src -Target $dst -Label $file
    }
    foreach ($dir in $SYNC_DIRS) {
        $src = Join-Path $CLAUDE_DIR $dir
        $dst = Join-Path $targetDir $dir
        Sync-DirJunction -Source $src -Target $dst -Label "$dir/" -Editor $editor
    }
    if (-not $DryRun) {
        Write-SyncModeJson -TargetDir $targetDir -Mode $(if ($Full) { "full" } else { "index" })
    }
}

if ($Scope -in @("all", "rules")) {
    Clear-CursorProjectLegacyArtifacts
    Cleanup-DevinMisplacedRulesDir
}

if ($Scope -eq "all") {
    if (-not $DryRun) {
        Sync-DeployRouterArtifacts
    }
    else {
        Write-Host "  [预演] 将部署 CLAUDE-ROUTER → 各编辑器必加载 rules" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  =====================================================" -ForegroundColor DarkGray
$syncDoneMsg = if ($DryRun) { "预演结束" } else { "同步完成" }
Write-Host "  $syncDoneMsg！" -ForegroundColor Green
Write-Host ""
Write-Host "  新建/确认链接数 : $($stats.Links)" -ForegroundColor White
Write-Host "  规则文件数       : $($stats.Files)" -ForegroundColor White
Write-Host "  删除陈旧软链接   : $($stats.Removed)" -ForegroundColor White
Write-Host "  跳过编辑器数     : $($stats.Skipped)" -ForegroundColor White
if ($stats.Errors -gt 0) {
    Write-Host "  错误数           : $($stats.Errors)" -ForegroundColor Red
}
Write-Host ""
if ($Full) {
    Write-Host "  已同步: 7总纲软链接 + agents/联接 + rules/skills 原生格式转换" -ForegroundColor DarkGray
    Write-Host "  切回索引: powershell -File sync.ps1 -Force" -ForegroundColor DarkGray
} else {
    Write-Host "  已同步: 7总纲软链接 + skills/agents 联接 + Cursor 个人/项目 rules" -ForegroundColor DarkGray
    Write-Host "  总纲执行: CLAUDE-ROUTER → CLAUDE.md → MANIFEST.yaml → *-INDEX.md → SPEC.md" -ForegroundColor DarkGray
    Write-Host "  全量模式: powershell -File sync.ps1 -Full（+ rules/skills 原生转换）" -ForegroundColor DarkGray
}
Write-Host "  不同步: hooks/ scripts/ MCP配置 plugins/ commands/ settings.json（Claude Code 专用，仅 ~/.claude）" -ForegroundColor DarkGray
Write-Host ""
