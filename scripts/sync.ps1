#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 多编辑器同步脚本 v10.0

.DESCRIPTION
    从 ~/.claude 向各编辑器用户目录同步以下内容：
      - skills/、agents/ → 目录联接（Junction）或符号链接
      - rules/ → 生成编辑器原生规则文件（.cursorrules/.traerules/.windsurfrules）
      - Windsurf global_rules.md：CLAUDE.md + alwaysApply 核心规则合并

    不同步：commands/、CLAUDE.md、TOOL_MATCHING_GUIDE.md、SYNC_GUIDE.md、
    hooks/、scripts/、MCP 配置、CLAUDE_IN_EDITOR 环境变量。

.PARAMETER Force
    强制重建所有目录链接

.PARAMETER DryRun
    仅预览，不写盘

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Force
    powershell -ExecutionPolicy Bypass -File C:\Users\DELL\.claude\scripts\sync.ps1 -Force
    powershell -ExecutionPolicy Bypass -File sync.ps1 -DryRun
#>

param(
    [switch]$Force,
    [switch]$DryRun
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$BACKUP_DIR = Join-Path $CLAUDE_DIR "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$EDITORS = @("cursor", "trae", "windsurf", "qoder")
# CodeArts agent 编辑器使用 AppData Roaming 目录，不使用 ~/.codearts-agent
$CODEARTS_EDITORS = @("codearts-agent")
$SYNC_DIRS = @("skills", "agents")
$STALE_LINKS = @("hooks", "scripts", "commands")

# 编辑器原生规则目录映射（使用各编辑器真正识别的全局路径）
# Cursor: ~/.cursor/rules/*.mdc (项目级格式，放在用户目录下作为同步中转)
# Windsurf: ~/.windsurf/rules/*.md (项目级多文件) + ~/.codeium/windsurf/memories/global_rules.md (核心规则单文件)
# Trae: ~/.trae/user_rules/*.md (Trae特有的全局rules目录，支持alwaysApply frontmatter)
$NATIVE_RULES_DIR_MAP = @{
    "cursor"   = @{ TargetDir = (Join-Path $env:USERPROFILE ".cursor\rules"); Ext = ".mdc"; Format = "cursor" }
    "windsurf" = @{ TargetDir = (Join-Path $env:USERPROFILE ".windsurf\rules"); Ext = ".md"; Format = "windsurf" }
    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\user_rules"); Ext = ".md"; Format = "trae" }
}

# Windsurf 全局 rules 单文件路径（核心规则，受 6000 字符限制）
$WINDSURF_GLOBAL_RULES_FILE = Join-Path $env:USERPROFILE ".codeium\windsurf\memories\global_rules.md"

# Windsurf 字符限制
# 全局 global_rules.md: 6000 字符; 工作区 rules/*.md: 12000 字符/文件
$WINDSURF_MAX_CHARS_GLOBAL = 6000
$WINDSURF_MAX_CHARS_PER_FILE = 12000

# CodeArts agent 编辑器：目标目录为 AppData Roaming 下的 User 目录
$CODEARTS_USER_DIRS = @{
    "codearts-agent" = (Join-Path $env:APPDATA "codearts-agent\User")
}

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)

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
        - Cursor: ~/.cursor/rules/*.mdc (每个规则一个文件，作为同步中转)
        - Windsurf: ~/.windsurf/rules/*.md (每个规则一个文件，遵守字符限制)
        - Trae: ~/.trae/user_rules/*.md (每个规则一个文件，alwaysApply格式)
    #>
    $rulesSrc = Join-Path $CLAUDE_DIR "rules"
    if (-not (Test-Path $rulesSrc)) {
        Write-Skip "源 rules 目录缺失，跳过原生规则文件生成"
        return
    }

    $ruleFiles = Get-ChildItem $rulesSrc -Filter "RULES_*.md" | Sort-Object Name
    if ($ruleFiles.Count -eq 0) {
        Write-Skip "无 RULES_*.md 文件，跳过原生规则文件生成"
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

    # Cursor / Windsurf / Trae：每个规则生成一个独立文件
    $syncedCount = 0
    $skippedCount = 0
    $truncatedCount = 0
    $totalChars = 0

    foreach ($rf in $ruleFiles) {
        $srcContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)
        $category = $rf.BaseName -replace "^RULES_", ""

        $targetFileName = "$category$ext"
        $targetPath = Join-Path $targetRulesDir $targetFileName

        # 转换内容
        $convertedContent = if ($format -eq "cursor") {
            $srcContent  # Cursor .mdc 格式：保留原有 frontmatter
        }
        else {
            Convert-RulesFrontmatter -Content $srcContent -Format $format
        }

        # Windsurf 字符限制检查
        if ($format -eq "windsurf") {
            if ($convertedContent.Length -gt $WINDSURF_MAX_CHARS_PER_FILE) {
                # 截断到限制内，保留 frontmatter + 尽可能多的内容
                $convertedContent = Truncate-ToCharLimit -Content $convertedContent -Limit $WINDSURF_MAX_CHARS_PER_FILE
                $truncatedCount++
            }
            $totalChars += $convertedContent.Length
        }

        if ($DryRun) { $syncedCount++; continue }

        # 比较并写入
        if ((Test-Path $targetPath) -and -not $Force) {
            $existingContent = [System.IO.File]::ReadAllText($targetPath, [System.Text.Encoding]::UTF8)
            if ($existingContent -eq $convertedContent) {
                $skippedCount++
                continue
            }
        }

        [System.IO.File]::WriteAllText($targetPath, $convertedContent, [System.Text.Encoding]::UTF8)
        $syncedCount++
    }

    if ($syncedCount -gt 0) {
        Write-Fix "rules 已生成 $syncedCount 个 $ext 文件（$format 格式）→ $targetRulesDir"
        $stats.Files += $syncedCount
    }
    if ($skippedCount -gt 0) {
        Write-Ok "$skippedCount 个 $ext 规则文件已是最新"
    }
    if ($truncatedCount -gt 0) {
        Write-Warn "$truncatedCount 个规则因超过 $($WINDSURF_MAX_CHARS_PER_FILE) 字符限制被截断"
    }

    # Windsurf: 额外同步核心规则到全局 global_rules.md
    if ($EditorName -eq "windsurf" -and -not $DryRun) {
        Sync-WindsurfGlobalRules -RuleFiles $ruleFiles
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

function Sync-WindsurfGlobalRules {
    param(
        [object[]]$RuleFiles
    )
    <#
    .SYNOPSIS
        同步 Windsurf 的全局 global_rules.md 单文件（仅 CLAUDE.md）
        路径：~/.codeium/windsurf/memories/global_rules.md
        限制：6000 字符/文件
        策略：
          - 优先写入完整 CLAUDE.md
          - 若超出字符限制：写入精简速查（不注入 rules/ 内容）
    #>
    $targetPath = $WINDSURF_GLOBAL_RULES_FILE
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

    # 优先写入完整 CLAUDE.md
    if ($editorClaudeMd -ne "") {
        [void]$sb.Append($editorClaudeMd)
    }

    $newContent = $sb.ToString()

    # 检查字符限制（全局 global_rules.md 限制 6000 字符）
    if ($newContent.Length -gt $WINDSURF_MAX_CHARS_GLOBAL) {
        # 生成精简速查（不注入 rules/）
        $sb2 = [System.Text.StringBuilder]::new()
        [void]$sb2.AppendLine("---")
        [void]$sb2.AppendLine("trigger: always_on")
        [void]$sb2.AppendLine("---")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("# Claude 全局配置（Windsurf 速查）")
        [void]$sb2.AppendLine("")
        [void]$sb2.AppendLine("Windsurf 的 global_rules.md 有 6000 字符限制，因此此处为精简速查。")
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
        if ($newContent.Length -gt $WINDSURF_MAX_CHARS_GLOBAL) {
            $newContent = $newContent.Substring(0, $WINDSURF_MAX_CHARS_GLOBAL - 50) + "`n`n<!-- 内容因字符限制被截断 -->"
        }
        Write-Warn "global_rules.md 超过 $($WINDSURF_MAX_CHARS_GLOBAL) 字符限制，已改为写入精简速查"
    }

    if ($DryRun) {
        Write-Fix "[预演] 将更新 global_rules.md（仅 CLAUDE.md / 或精简速查）"
        return
    }

    # 比较并写入
    if ((Test-Path $targetPath) -and -not $Force) {
        $existingContent = [System.IO.File]::ReadAllText($targetPath, [System.Text.Encoding]::UTF8)
        if ($existingContent -eq $newContent) {
            Write-Ok "global_rules.md 已是最新"
            return
        }
    }

    # 备份
    if (Test-Path $targetPath) {
        Copy-Item $targetPath ($targetPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
    }

    [System.IO.File]::WriteAllText($targetPath, $newContent, [System.Text.Encoding]::UTF8)
    Write-Fix "global_rules.md 已更新 ($($newContent.Length) 字符) → $targetPath"
    $stats.Files++
}

function Convert-RulesFrontmatter {
    param(
        [string]$Content,
        [string]$Format
    )
    <#
    .SYNOPSIS
        将 Claude Code/Cursor 格式的 YAML frontmatter 转换为目标编辑器格式
        cursor: 保留原格式（description, alwaysApply, globs）
        windsurf: 转为 trigger 格式（trigger: always_on/model_decision/glob/manual, globs, description）
        trae: 转为 alwaysApply 格式（description, alwaysApply, globs）— 与 Cursor 格式相同
    #>
    # Trae 格式与 Cursor 相同（alwaysApply 格式），直接返回原内容
    if ($Format -eq "trae") {
        return $Content
    }

    # Windsurf 格式：转为 trigger 格式
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

    # 构建 Windsurf 格式的 frontmatter
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

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 多编辑器同步脚本 v10.0" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录 : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标编辑器: $($EDITORS -join ', '), $($CODEARTS_EDITORS -join ', ')" -ForegroundColor DarkGray
Write-Host "  同步项 : $($SYNC_DIRS -join ', ')  +  rules/（格式转换复制）" -ForegroundColor DarkGray
$syncModeLabel = if ($isAdmin) { "管理员（符号链接）" } else { "非管理员（目录联接，Junction）" }
Write-Host "  模式   : $syncModeLabel" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "  [预演] 仅预览，不写盘" -ForegroundColor Yellow }
if ($Force) { Write-Host "  [强制] 重建全部链接" -ForegroundColor Yellow }
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

$stats = @{ Links = 0; Files = 0; Removed = 0; Errors = 0; Skipped = 0 }

foreach ($editor in $EDITORS | Sort-Object) {
    $targetDir = Join-Path $env:USERPROFILE ".$editor"

    Write-Host ""
    Write-Host "  -- $editor -------------------------------------------" -ForegroundColor DarkGray

    if (-not (Test-Path $targetDir)) {
        Write-Skip "未找到 .$editor 目录，跳过"
        $stats.Skipped++
        continue
    }

    # Remove stale symlinks from old sync versions
    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $targetDir $stale
        if ((Test-Path $sp) -and (IsLink $sp)) {
            if ($DryRun) { Write-Fix "[预演] 将删除陈旧 $stale/ 链接" }
            else { Remove-Item $sp -Force; Write-Fix "已删除陈旧 $stale/ 软链接"; $stats.Removed++ }
        }
    }

    # Sync directories as junctions/symlinks
    foreach ($dir in $SYNC_DIRS) {
        $src = Join-Path $CLAUDE_DIR $dir
        $dst = Join-Path $targetDir $dir
        if (-not (Test-Path $src)) { Write-Skip "源目录缺失: $dir"; continue }

        if (Test-Path $dst) {
            if (IsLink $dst) {
                if (-not $Force) {
                    $actual = (Get-Item $dst -Force).Target
                    if ($actual -is [array]) { $actual = $actual[0] }
                    if ($actual -eq $src) { Write-Ok "$dir 链接正确"; continue }
                    Write-Warn "$dir 链接目标不一致，将重建"
                }
                if (-not $DryRun) { Remove-Item $dst -Force }
            }
            else {
                Write-Warn "$dir 为实体目录，将备份后替换为链接"
                if (-not $DryRun) {
                    Copy-Item $dst (Join-Path $BACKUP_DIR "${editor}_${dir}") -Recurse -Force
                    Remove-Item $dst -Recurse -Force
                }
            }
        }

        if ($DryRun) { Write-Ok "[预演] 将创建 $dir 链接"; $stats.Links++; continue }
        try {
            New-Link -Source $src -Target $dst
            Write-Ok "$dir 已链接"
            $stats.Links++
        }
        catch {
            Write-Fail "${dir}: $_"
            $stats.Errors++
        }
    }

    # Generate native rules files in editor-specific format
    # Cursor: ~/.cursor/rules/*.mdc | Windsurf: ~/.codeium/windsurf/memories/global_rules.md | Trae: ~/.trae/user_rules/*.md
    if ($NATIVE_RULES_DIR_MAP.ContainsKey($editor)) {
        $rulesConfig = $NATIVE_RULES_DIR_MAP[$editor]
        if (-not $DryRun) {
            Sync-NativeRulesFiles -TargetDir $targetDir -EditorName $editor -RulesConfig $rulesConfig
        }
        else {
            Write-Ok "[预演] 将生成 $($rulesConfig.Ext) 规则文件（$($rulesConfig.Format) 格式）"
        }
    }
}

# ── CodeArts agent 编辑器同步（目标目录为 AppData Roaming User 目录）──
foreach ($editor in $CODEARTS_EDITORS | Sort-Object) {
    $targetDir = $CODEARTS_USER_DIRS[$editor]
    if (-not $targetDir) {
        Write-Skip "未配置 $editor 的用户目录，跳过"
        $stats.Skipped++
        continue
    }

    Write-Host ""
    Write-Host "  -- $editor (CodeArts) -----------------------------" -ForegroundColor DarkGray

    if (-not (Test-Path $targetDir)) {
        Write-Skip "未找到 $targetDir 目录，跳过"
        $stats.Skipped++
        continue
    }

    # Remove stale symlinks from old sync versions
    foreach ($stale in $STALE_LINKS) {
        $sp = Join-Path $targetDir $stale
        if ((Test-Path $sp) -and (IsLink $sp)) {
            if ($DryRun) { Write-Fix "[预演] 将删除陈旧 $stale/ 链接" }
            else { Remove-Item $sp -Force; Write-Fix "已删除陈旧 $stale/ 软链接"; $stats.Removed++ }
        }
    }

    # Sync directories as junctions/symlinks
    foreach ($dir in $SYNC_DIRS) {
        $src = Join-Path $CLAUDE_DIR $dir
        $dst = Join-Path $targetDir $dir
        if (-not (Test-Path $src)) { Write-Skip "源目录缺失: $dir"; continue }

        if (Test-Path $dst) {
            if (IsLink $dst) {
                if (-not $Force) {
                    $actual = (Get-Item $dst -Force).Target
                    if ($actual -is [array]) { $actual = $actual[0] }
                    if ($actual -eq $src) { Write-Ok "$dir 链接正确"; continue }
                    Write-Warn "$dir 链接目标不一致，将重建"
                }
                if (-not $DryRun) { Remove-Item $dst -Force }
            }
            else {
                Write-Warn "$dir 为实体目录，将备份后替换为链接"
                if (-not $DryRun) {
                    Copy-Item $dst (Join-Path $BACKUP_DIR "${editor}_${dir}") -Recurse -Force
                    Remove-Item $dst -Recurse -Force
                }
            }
        }

        if ($DryRun) { Write-Ok "[预演] 将创建 $dir 链接"; $stats.Links++; continue }
        try {
            New-Link -Source $src -Target $dst
            Write-Ok "$dir 已链接"
            $stats.Links++
        }
        catch {
            Write-Fail "${dir}: $_"
            $stats.Errors++
        }
    }

    # CodeArts agent: 仅同步目录链接
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
Write-Host "  已同步: skills/ agents/（链接） rules/（格式转换复制）" -ForegroundColor DarkGray
Write-Host "  原生规则: .cursor/rules/*.mdc | .windsurf/rules/*.md | .trae/user_rules/*.md" -ForegroundColor DarkGray
Write-Host "  Windsurf: global_rules.md(完整CLAUDE.md；超限则速查) → ~/.codeium/windsurf/memories/" -ForegroundColor DarkGray
Write-Host "  不同步: commands/ CLAUDE.md TOOL_MATCHING_GUIDE.md SYNC_GUIDE.md hooks/ scripts/ MCP配置 CLAUDE_IN_EDITOR" -ForegroundColor DarkGray
Write-Host ""
