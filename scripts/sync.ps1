#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 多编辑器同步脚本 v9.2

.DESCRIPTION
    从 ~/.claude 向各编辑器用户目录同步以下内容：
      - skills/、agents/ → 目录联接（Junction）或符号链接
      - CLAUDE.md → 编辑器精简版（移除 [CC] 标记段落：工具匹配/Agent路由/自迭代/跨编辑器映射）
      - TOOL_MATCHING_GUIDE.md、SYNC_GUIDE.md → 文件复制
      - rules/ → 生成编辑器原生规则文件（.cursorrules/.traerules/.windsurfrules）
      - MCP 配置 → 从 settings.json mcpServers 同步到各编辑器：
          - Cursor/Trae/Windsurf: 写入 mcp.json（mcpServers 格式）
          - CodeArts Agent: 写入 mcpServerRegistrations（数组格式，格式转换）
      - CodeArts agent 编辑器：将精简版 CLAUDE.md + alwaysApply 核心规则合并写入 additionalSystemPrompt
      - Windsurf global_rules.md：精简版 CLAUDE.md + alwaysApply 核心规则合并

    同时向各编辑器 settings.json 合并写入 env.CLAUDE_IN_EDITOR（与 fix.ps1 中
    _editor_hook_launcher 的 GetConsoleWindow() 判定互为补充）。

    合并策略不破坏界面配置：若已有 settings.json 无法按严格 JSON 解析（如含 // 的 JSONC、
    尾逗号等），则跳过写入并告警，不会用空对象覆盖字体、主题、workbench 等项；写回时使用
    ConvertTo-Json -Depth 100，避免深层嵌套（如颜色自定义）被截断。

    不同步：hooks/、scripts/、以及 .claude 下的 settings.json（不把 CLI 整份配置拷到编辑器）。
    会清理旧版遗留：hooks/、scripts/ 的错误软链接。
    会从 terminal.integrated.env.windows 中移除 CLAUDE_IN_EDITOR，避免污染集成终端里
    的 Claude Code CLI（CLI 应在真实终端正常跑全量 Hook）。

.PARAMETER Force
    强制重建所有目录链接

.PARAMETER DryRun
    仅预览，不写盘

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Force
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
$COPY_FILES = @("CLAUDE.md", "TOOL_MATCHING_GUIDE.md", "SYNC_GUIDE.md")
$STALE_LINKS = @("hooks", "scripts")

# 编辑器原生规则目录映射（使用各编辑器真正识别的全局路径）
# Cursor: ~/.cursor/rules/*.mdc (项目级格式，放在用户目录下作为同步中转)
# Windsurf: ~/.windsurf/rules/*.md (项目级多文件) + ~/.codeium/windsurf/memories/global_rules.md (核心规则单文件)
# Trae: ~/.trae/user_rules/*.md (Trae特有的全局rules目录，支持alwaysApply frontmatter)
$NATIVE_RULES_DIR_MAP = @{
    "cursor"   = @{ TargetDir = (Join-Path $env:USERPROFILE ".cursor\rules"); Ext = ".mdc"; Format = "cursor" }
    "windsurf" = @{ TargetDir = (Join-Path $env:USERPROFILE ".windsurf\rules"); Ext = ".md"; Format = "windsurf" }
    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\user_rules"); Ext = ".md"; Format = "trae" }
}

# Windsurf 全局 skills 路径
$WINDSURF_GLOBAL_SKILLS_DIR = Join-Path $env:USERPROFILE ".codeium\windsurf\skills"

# Windsurf 全局 rules 单文件路径（核心规则，受 6000 字符限制）
$WINDSURF_GLOBAL_RULES_FILE = Join-Path $env:USERPROFILE ".codeium\windsurf\memories\global_rules.md"

# Windsurf 字符限制
# 全局 global_rules.md: 6000 字符; 工作区 rules/*.md: 12000 字符/文件
$WINDSURF_MAX_CHARS_GLOBAL = 6000
$WINDSURF_MAX_CHARS_PER_FILE = 12000

# 各编辑器 Roaming 用户设置路径（VS Code 系）
$ROAMING_SETTINGS = @{
    "cursor"   = (Join-Path $env:APPDATA "Cursor\User\settings.json")
    "windsurf" = (Join-Path $env:APPDATA "Windsurf\User\settings.json")
    "trae"     = (Join-Path $env:APPDATA "Trae\User\settings.json")
    "qoder"    = (Join-Path $env:APPDATA "Qoder\User\settings.json")
}

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

function Get-FileMD5 {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return "" }
    try {
        $out = & certutil -hashfile $Path MD5 2>&1
        if ($LASTEXITCODE -eq 0) {
            $m = $out | Select-String "[0-9a-fA-F]{32}" | Select-Object -First 1
            if ($m) { return $m.Matches.Value.ToLower() }
        }
    }
    catch {}
    $fi = Get-Item $Path
    return "$($fi.Length)_$($fi.LastWriteTime.Ticks)"
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

function Read-Json {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    # 优先使用 [IO.File]::ReadAllText + UTF8 编码，避免 PowerShell Get-Content 编码问题
    try { return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) | ConvertFrom-Json } catch {}
    try { return Get-Content $Path -Raw -Encoding utf8 | ConvertFrom-Json } catch {}
    try { return Get-Content $Path -Raw -Encoding unicode | ConvertFrom-Json } catch {}
    return $null
}

function Write-Json {
    param([string]$Path, $Obj)
    # Depth 100：防止 workbench/编辑器深层主题与扩展配置被截断（PS 默认深度仅 2）
    [System.IO.File]::WriteAllText($Path, ($Obj | ConvertTo-Json -Depth 100), [System.Text.Encoding]::UTF8)
}

function Set-EditorEnvVar {
    param([string]$SettingsPath, [string]$EditorName, [string]$VarName, [string]$VarValue)
    # 仅合并 settings.json 顶层 env.*；保留其余所有键。
    # 从 terminal.integrated.env.windows 中删除同名变量，避免影响集成终端里的 CLI。

    $fileExists = Test-Path $SettingsPath
    $es = $null
    if ($fileExists) {
        $es = Read-Json $SettingsPath
        if ($null -eq $es) {
            Write-Warn "$EditorName  跳过 $SettingsPath（非严格 JSON / 解析失败），文件未修改，以保留字体、主题与界面相关配置。"
            Write-Warn "$EditorName  请手动添加 `"env`": { `"$VarName`": `"$VarValue`" }，或去掉 JSONC/尾逗号后重新执行 sync。"
            return
        }
    }
    else {
        # 新建文件：从空对象开始（此前无文件，不存在覆盖界面配置问题）
        $es = [PSCustomObject]@{}
    }

    $changed = $false

    # Set in env block
    if (-not $es.PSObject.Properties.Match('env').Count) {
        $es | Add-Member -MemberType NoteProperty -Name 'env' -Value ([PSCustomObject]@{})
    }
    if (-not $es.env.PSObject.Properties.Match($VarName).Count) {
        $es.env | Add-Member -MemberType NoteProperty -Name $VarName -Value $VarValue -Force
        $changed = $true
    }
    elseif ($es.env.$VarName -ne $VarValue) {
        $es.env.$VarName = $VarValue
        $changed = $true
    }

    # 从 terminal.integrated.env.windows 移除（避免污染 CLI 终端环境）
    $propT = 'terminal.integrated.env.windows'
    if ($es.PSObject.Properties.Match($propT).Count) {
        $tw = $es.$propT
        if ($tw -and $tw.PSObject.Properties.Match($VarName).Count) {
            $tw.PSObject.Properties.Remove($VarName)
            $changed = $true
            Write-Fix "$EditorName  已从 terminal.integrated.env.windows 移除 $VarName"
        }
    }

    if ($changed) {
        if ($fileExists) {
            Copy-Item $SettingsPath ($SettingsPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
        }
        $parent = Split-Path $SettingsPath -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory $parent -Force | Out-Null }
        Write-Json -Path $SettingsPath -Obj $es
        Write-Fix "$EditorName  $VarName=$VarValue"
    }
    else {
        Write-Ok "$EditorName  $VarName 已正确，无需修改"
    }
}

function Get-EditorClaudeMd {
    <#
    .SYNOPSIS
        从源 CLAUDE.md 生成编辑器精简版，移除仅 Claude Code 适用的段落
        移除标记为 [CC] 的段落：工具匹配、Agent 路由、自迭代更新、跨编辑器工具映射
        保留：强制规则、任务流程、迭代精炼、交叉验证、执行风格、修改彻底性、计划优先、代码规范、Git 规范
    #>
    $srcPath = Join-Path $CLAUDE_DIR "CLAUDE.md"
    if (-not (Test-Path $srcPath)) { return "" }

    $content = [System.IO.File]::ReadAllText($srcPath, [System.Text.Encoding]::UTF8)
    $lines = $content -split "`n"

    # 需要移除的段落标题（含 [CC] 标记或仅 CC 适用的段落）
    $ccSectionPatterns = @(
        '工具匹配\s*\[CC\]'
        'Agent\s*路由\s*\[CC\]'
        '自迭代更新'
        '跨编辑器工具映射\s*\[CC\]'
    )
    $ccRegex = $ccSectionPatterns -join '|'

    $result = [System.Collections.ArrayList]::new()
    $skipSection = $false
    $sectionLevel = 0

    foreach ($line in $lines) {
        # 检测 ## 级别标题
        if ($line -match '^##\s+(.+)') {
            $sectionTitle = $Matches[1]
            if ($sectionTitle -match $ccRegex) {
                $skipSection = $true
                continue
            }
            $skipSection = $false
        }
        # 检测 ### 级别标题（子段落，如果父段落被跳过则继续跳过）
        elseif ($line -match '^###\s+' -and $skipSection) {
            continue
        }
        # 检测 --- 分隔线（段落边界）
        elseif ($line -match '^---+$' -and $skipSection) {
            # Separator belongs to skipped section, skip it
            continue
        }

        if ($skipSection) { continue }
        [void]$result.Add($line)
    }

    # Compress consecutive blank lines (max 2)
    $finalLines = [System.Collections.ArrayList]::new()
    $emptyCount = 0
    foreach ($line in $result) {
        if ($line.Trim() -eq '') {
            $emptyCount++
            if ($emptyCount -le 2) { [void]$finalLines.Add($line) }
        } else {
            $emptyCount = 0
            [void]$finalLines.Add($line)
        }
    }

    # Update version marker
    $finalText = ($finalLines -join "`n")
    $finalText = $finalText -replace '跨编辑器共享（Claude Code/Cursor/Windsurf/Trae/VS Code）。`\[CC\]` = 仅Claude Code。', '跨编辑器共享（Cursor/Windsurf/Trae/VS Code）。已移除仅 Claude Code 适用的段落。'
    $finalText = $finalText -replace '_版本：v4\.2 \| 更新：2026-04-10_', '_版本：v4.2-editor | 更新：2026-04-11_'

    return $finalText
}

function Read-SourceMcpServers {
    <#
    .SYNOPSIS
        From ~/.claude/settings.json read mcpServers as MCP sync source
    #>
    $settingsPath = Join-Path $CLAUDE_DIR "settings.json"
    $settings = Read-Json $settingsPath
    if ($null -eq $settings -or -not $settings.PSObject.Properties.Match('mcpServers').Count) {
        Write-Warn "Source MCP config missing or parse failed"
        return $null
    }
    return $settings.mcpServers
}

function Deep-CopyPSObject {
    param([PSCustomObject]$Obj)
    if ($null -eq $Obj) { return $null }
    $json = $Obj | ConvertTo-Json -Depth 100
    return $json | ConvertFrom-Json
}

function Clean-PSObjectMetadata {
    param([PSCustomObject]$Obj)
    # 移除以 _ 开头的元数据属性（如 _description, _comment）
    if ($null -eq $Obj) { return }
    $metaProps = @($Obj.PSObject.Properties.Name | Where-Object { $_ -match "^_" })
    foreach ($prop in $metaProps) {
        $Obj.PSObject.Properties.Remove($prop)
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
        } else {
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
        将核心规则合并为 Windsurf 的全局 global_rules.md 单文件
        路径：~/.codeium/windsurf/memories/global_rules.md
        限制：6000 字符/文件
        策略：精简版 CLAUDE.md 核心段落 + alwaysApply:true 核心规则，遵守字符限制
    #>
    $targetPath = $WINDSURF_GLOBAL_RULES_FILE
    $targetDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    # 筛选核心规则（alwaysApply:true 的规则）
    $coreRules = @()
    foreach ($rf in $RuleFiles) {
        $srcContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)
        # 检查是否 alwaysApply: true
        if ($srcContent -match 'alwaysApply:\s*true') {
            $coreRules += $rf
        }
    }

    # 构建合并内容：精简版 CLAUDE.md 核心段落 + 核心规则
    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("trigger: always_on")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")

    # 加入精简版 CLAUDE.md（移除 [CC] 段落的版本）
    $editorClaudeMd = Get-EditorClaudeMd
    if ($editorClaudeMd -ne "") {
        [void]$sb.Append($editorClaudeMd)
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("")
    }

    foreach ($rf in $coreRules) {
        $srcContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)
        $category = $rf.BaseName -replace "^RULES_", ""

        # 去掉源文件的 frontmatter
        $body = $srcContent
        if ($srcContent.StartsWith("---")) {
            $secondDash = $srcContent.IndexOf("---", 3)
            if ($secondDash -gt 0) {
                $body = $srcContent.Substring($secondDash + 3).TrimStart()
            }
        }

        [void]$sb.AppendLine("## $category Rules")
        [void]$sb.AppendLine("")
        [void]$sb.Append($body)
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("")
    }

    $newContent = $sb.ToString()

    # 检查字符限制（全局 global_rules.md 限制 6000 字符）
    if ($newContent.Length -gt $WINDSURF_MAX_CHARS_GLOBAL) {
        # 截断到限制内
        $newContent = $newContent.Substring(0, $WINDSURF_MAX_CHARS_GLOBAL - 50) + "`n`n<!-- 内容因字符限制被截断 -->"
        Write-Warn "global_rules.md 超过 $($WINDSURF_MAX_CHARS_GLOBAL) 字符限制，已截断"
    }

    if ($DryRun) {
        Write-Fix "[预演] 将更新 global_rules.md ($($coreRules.Count) 个核心规则合并)"
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
    Write-Fix "global_rules.md 已更新 ($($coreRules.Count) 个核心规则合并, $($newContent.Length) 字符) → $targetPath"
    $stats.Files++
}

function Sync-WindsurfGlobalSkills {
    param([string]$EditorName)
    <#
    .SYNOPSIS
        将 ~/.claude/skills/ 同步到 Windsurf 全局 skills 目录
        路径：~/.codeium/windsurf/skills/
        Windsurf 是唯一支持文件系统全局 skills 的编辑器
    #>
    $srcSkillsDir = Join-Path $CLAUDE_DIR "skills"
    if (-not (Test-Path $srcSkillsDir)) { return }

    if (-not (Test-Path $WINDSURF_GLOBAL_SKILLS_DIR)) {
        New-Item -ItemType Directory -Path $WINDSURF_GLOBAL_SKILLS_DIR -Force | Out-Null
    }

    # 获取源 skills 目录列表
    $srcSkillDirs = Get-ChildItem $srcSkillsDir -Directory -Force | Where-Object {
        (Test-Path (Join-Path $_.FullName "SKILL.md"))
    }

    $syncedCount = 0
    foreach ($srcDir in $srcSkillDirs) {
        $targetSkillDir = Join-Path $WINDSURF_GLOBAL_SKILLS_DIR $srcDir.Name
        $srcSkillMd = Join-Path $srcDir.FullName "SKILL.md"

        if (-not (Test-Path $targetSkillDir)) {
            # 创建联接到源目录
            New-Link -Source $srcDir.FullName -Target $targetSkillDir
            $syncedCount++
        }
    }

    if ($syncedCount -gt 0) {
        Write-Fix "Windsurf 全局 skills 已同步 $syncedCount 个 → $WINDSURF_GLOBAL_SKILLS_DIR"
        $stats.Links += $syncedCount
    }
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

function Sync-McpToDotDir {
    param(
        [string]$TargetDir,
        [string]$EditorName
    )
    <#
    .SYNOPSIS
        将源 mcpServers 同步到编辑器的 mcp.json
        Cursor/Trae: {dotdir}/mcp.json
        Windsurf: ~/.codeium/windsurf/mcp_config.json (Windsurf 真正读取的路径)
    #>
    $sourceMcp = Read-SourceMcpServers
    if ($null -eq $sourceMcp) {
        Write-Skip "$EditorName  源 MCP 配置不可用，跳过 MCP 同步"
        return
    }

    # Windsurf 使用 ~/.codeium/windsurf/mcp_config.json
    $targetMcpPath = if ($EditorName -eq "windsurf") {
        Join-Path $env:USERPROFILE ".codeium\windsurf\mcp_config.json"
    } else {
        Join-Path $TargetDir "mcp.json"
    }

    # 读取目标 mcp.json
    $targetMcp = $null
    if (Test-Path $targetMcpPath) {
        $targetMcp = Read-Json $targetMcpPath
    }
    if ($null -eq $targetMcp) {
        $targetMcp = [PSCustomObject]@{}
    }

    # 确保 mcpServers 属性存在
    if (-not $targetMcp.PSObject.Properties.Match('mcpServers').Count) {
        $targetMcp | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value ([PSCustomObject]@{})
    }

    # 合并源 MCP 到目标（源覆盖同名，保留目标中源不存在的）
    $sourceNames = @($sourceMcp.PSObject.Properties.Name | Where-Object { $_ -notmatch "^_" })
    $convertedCount = 0

    foreach ($name in $sourceNames) {
        $server = Deep-CopyPSObject $sourceMcp.$name
        # 清理元数据
        Clean-PSObjectMetadata $server
        # 设置/覆盖到目标
        if ($targetMcp.mcpServers.PSObject.Properties.Match($name).Count) {
            $targetMcp.mcpServers.$name = $server
        } else {
            $targetMcp.mcpServers | Add-Member -MemberType NoteProperty -Name $name -Value $server -Force
        }
        $convertedCount++
    }

    # 备份 + 写入
    if (Test-Path $targetMcpPath) {
        Copy-Item $targetMcpPath ($targetMcpPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
    }
    Write-Json -Path $targetMcpPath -Obj $targetMcp
    Write-Fix "mcp.json 已同步 ($convertedCount 个服务器)"
    $stats.Mcp++
    $stats.Converted += $convertedCount
}

function Sync-McpToCodeArts {
    param(
        [string]$SettingsPath,
        [string]$EditorName
    )
    <#
    .SYNOPSIS
        将源 mcpServers 转换为 CodeArts mcpServerRegistrations 数组格式并写入
    #>
    $sourceMcp = Read-SourceMcpServers
    if ($null -eq $sourceMcp) {
        Write-Skip "$EditorName  源 MCP 配置不可用，跳过 MCP 同步"
        return
    }

    $es = Read-Json $SettingsPath
    if ($null -eq $es) {
        Write-Warn "$EditorName  CodeArts settings.json 解析失败，跳过 MCP 同步"
        return
    }

    $configKey = "codeartsAiFeaturesExtension.configuration"
    if (-not $es.PSObject.Properties.Match($configKey).Count) {
        Write-Warn "$EditorName  未找到 $configKey，跳过 MCP 同步"
        return
    }
    $config = $es.$configKey

    # 读取现有 mcpServerRegistrations，构建 enabled 索引
    $enabledMap = @{}
    $existingRegs = @()
    if ($config.PSObject.Properties.Match('mcpServerRegistrations').Count) {
        $existingRegs = @($config.mcpServerRegistrations)
        foreach ($reg in $existingRegs) {
            if ($reg.PSObject.Properties.Match('id').Count) {
                $serverName = $reg.id -replace "^stdio_", ""
                if ($reg.PSObject.Properties.Match('config').Count -and
                    $reg.config.PSObject.Properties.Match('enabled').Count) {
                    $enabledMap[$serverName] = $reg.config.enabled
                }
            }
        }
    }

    # 生成新注册数组
    $newRegs = [System.Collections.ArrayList]::new()
    $sourceNames = @($sourceMcp.PSObject.Properties.Name | Where-Object { $_ -notmatch "^_" })
    $convertedCount = 0

    foreach ($name in $sourceNames) {
        $server = $sourceMcp.$name
        $isEnabled = if ($enabledMap.ContainsKey($name)) { $enabledMap[$name] } else { $true }
        $envValue = ""
        if ($server.PSObject.Properties.Match('env').Count -and $null -ne $server.env) {
            $envValue = $server.env
        }
        $reg = [PSCustomObject]@{
            id = "stdio_$name"
            config = [PSCustomObject]@{
                enabled             = $isEnabled
                type                = "stdio"
                command             = if ($server.PSObject.Properties.Match('command').Count) { $server.command } else { "" }
                args                = if ($server.PSObject.Properties.Match('args').Count) { @($server.args) } else { @() }
                env                 = $envValue
                url                 = ""
                autoApprovedTools   = @()
            }
        }
        [void]$newRegs.Add($reg)
        $convertedCount++
    }

    # 保留用户自定义注册（源中不存在的）
    foreach ($reg in $existingRegs) {
        if ($reg.PSObject.Properties.Match('id').Count) {
            $serverName = $reg.id -replace "^stdio_", ""
            if ($serverName -notin $sourceNames) {
                [void]$newRegs.Add($reg)
            }
        }
    }

    # 写回
    $config.mcpServerRegistrations = $newRegs.ToArray()
    Copy-Item $SettingsPath ($SettingsPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
    Write-Json -Path $SettingsPath -Obj $es
    Write-Fix "mcpServerRegistrations 已同步 ($convertedCount 个服务器转换)"
    $stats.Mcp++
    $stats.Converted += $convertedCount
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 多编辑器同步脚本 v9.2" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录 : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标编辑器: $($EDITORS -join ', '), $($CODEARTS_EDITORS -join ', ')" -ForegroundColor DarkGray
Write-Host "  同步项 : $($SYNC_DIRS -join ', ')  +  CLAUDE.md（精简版）" -ForegroundColor DarkGray
Write-Host "  环境变量: 仅合并 env.CLAUDE_IN_EDITOR；已清理集成终端 env" -ForegroundColor DarkGray
$syncModeLabel = if ($isAdmin) { "管理员（符号链接）" } else { "非管理员（目录联接，Junction）" }
Write-Host "  模式   : $syncModeLabel" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "  [预演] 仅预览，不写盘" -ForegroundColor Yellow }
if ($Force) { Write-Host "  [强制] 重建全部链接" -ForegroundColor Yellow }
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

$stats = @{ Links = 0; Files = 0; Removed = 0; Env = 0; Mcp = 0; Converted = 0; Errors = 0; Skipped = 0 }

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

    # Copy files (CLAUDE.md → 编辑器精简版; 其余直接复制)
    foreach ($file in $COPY_FILES) {
        $src = Join-Path $CLAUDE_DIR $file
        $dst = Join-Path $targetDir $file
        if (-not (Test-Path $src)) { Write-Skip "源文件缺失: $file"; continue }
        if ((Test-Path $dst) -and (IsLink $dst)) {
            if (-not $DryRun) { Remove-Item $dst -Force; Write-Fix "$file 原为软链接，已改为复制文件" }
        }

        if ($file -eq "CLAUDE.md") {
            # 生成编辑器精简版 CLAUDE.md（移除 [CC] 标记段落）
            $editorContent = Get-EditorClaudeMd
            if ($editorContent -eq "") { Write-Skip "精简版 CLAUDE.md 生成失败"; continue }
            $needWrite = $Force
            if (-not $needWrite -and (Test-Path $dst)) {
                $existingContent = [System.IO.File]::ReadAllText($dst, [System.Text.Encoding]::UTF8)
                if ($existingContent -ne $editorContent) { $needWrite = $true }
            } else { $needWrite = $true }
            if ($needWrite) {
                if ($DryRun) { Write-Ok "[预演] 将写入精简版 CLAUDE.md" }
                else {
                    [System.IO.File]::WriteAllText($dst, $editorContent, [System.Text.Encoding]::UTF8)
                    Write-Ok "CLAUDE.md 已写入精简版 ($($editorContent.Length) 字符)"
                }
                $stats.Files++
            } else {
                Write-Ok "CLAUDE.md 精简版已是最新"
            }
        } else {
            $needCopy = (-not (Test-Path $dst)) -or $Force -or ((Get-FileMD5 $src) -ne (Get-FileMD5 $dst))
            if ($needCopy) {
                if ($DryRun) { Write-Ok "[预演] 将复制 $file" }
                else { Copy-Item $src $dst -Force; Write-Ok "$file 已复制" }
                $stats.Files++
            }
            else {
                Write-Ok "$file 已是最新"
            }
        }
    }

    # Generate native rules files in editor-specific format
    # 生成编辑器原生规则文件（使用各编辑器真正识别的全局路径）
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

    # Windsurf: 同步 skills 到 ~/.codeium/windsurf/skills/
    if ($editor -eq "windsurf" -and -not $DryRun) {
        Sync-WindsurfGlobalSkills -EditorName $editor
    }

    # Sync MCP configuration to mcp.json
    if (-not $DryRun) {
        Sync-McpToDotDir -TargetDir $targetDir -EditorName $editor
    }
    else {
        Write-Ok "[预演] 将同步 MCP 配置到 mcp.json"
    }

    # CLAUDE_IN_EDITOR: write into dot-dir settings.json
    if (-not $DryRun) {
        $dotDirSettings = Join-Path $targetDir "settings.json"
        Set-EditorEnvVar -SettingsPath $dotDirSettings -EditorName "dot-$editor" `
            -VarName "CLAUDE_IN_EDITOR" -VarValue $editor
        $stats.Env++
    }
    else {
        Write-Ok "[预演] 将设置 $editor/settings.json 中 env.CLAUDE_IN_EDITOR=$editor"
    }

    # CLAUDE_IN_EDITOR: also write into Roaming User settings (more likely inherited)
    if (-not $DryRun) {
        $roaming = $ROAMING_SETTINGS[$editor]
        if ($roaming) {
            Set-EditorEnvVar -SettingsPath $roaming -EditorName "roaming-$editor" `
                -VarName "CLAUDE_IN_EDITOR" -VarValue $editor
        }
    }

    # Create ignore file
    $ignoreFile = Join-Path $targetDir ".${editor}ignore"
    if (-not (Test-Path $ignoreFile) -and -not $DryRun) {
        "# Claude Code internal dirs - do not index`nhooks/`nplugins/`nbackups/`nlogs/`nexperiences/`nplans/" |
        Out-File -FilePath $ignoreFile -Encoding utf8
        Write-Ok "已创建 .${editor}ignore"
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

    # Copy files (CLAUDE.md → 编辑器精简版; 其余直接复制)
    foreach ($file in $COPY_FILES) {
        $src = Join-Path $CLAUDE_DIR $file
        $dst = Join-Path $targetDir $file
        if (-not (Test-Path $src)) { Write-Skip "源文件缺失: $file"; continue }
        if ((Test-Path $dst) -and (IsLink $dst)) {
            if (-not $DryRun) { Remove-Item $dst -Force; Write-Fix "$file 原为软链接，已改为复制文件" }
        }

        if ($file -eq "CLAUDE.md") {
            # 生成编辑器精简版 CLAUDE.md（移除 [CC] 标记段落）
            $editorContent = Get-EditorClaudeMd
            if ($editorContent -eq "") { Write-Skip "精简版 CLAUDE.md 生成失败"; continue }
            $needWrite = $Force
            if (-not $needWrite -and (Test-Path $dst)) {
                $existingContent = [System.IO.File]::ReadAllText($dst, [System.Text.Encoding]::UTF8)
                if ($existingContent -ne $editorContent) { $needWrite = $true }
            } else { $needWrite = $true }
            if ($needWrite) {
                if ($DryRun) { Write-Ok "[预演] 将写入精简版 CLAUDE.md" }
                else {
                    [System.IO.File]::WriteAllText($dst, $editorContent, [System.Text.Encoding]::UTF8)
                    Write-Ok "CLAUDE.md 已写入精简版 ($($editorContent.Length) 字符)"
                }
                $stats.Files++
            } else {
                Write-Ok "CLAUDE.md 精简版已是最新"
            }
        } else {
            $needCopy = (-not (Test-Path $dst)) -or $Force -or ((Get-FileMD5 $src) -ne (Get-FileMD5 $dst))
            if ($needCopy) {
                if ($DryRun) { Write-Ok "[预演] 将复制 $file" }
                else { Copy-Item $src $dst -Force; Write-Ok "$file 已复制" }
                $stats.Files++
            }
            else {
                Write-Ok "$file 已是最新"
            }
        }
    }

    # CLAUDE_IN_EDITOR: write into CodeArts User settings.json
    if (-not $DryRun) {
        $codeartsSettings = Join-Path $targetDir "settings.json"
        Set-EditorEnvVar -SettingsPath $codeartsSettings -EditorName "codearts-$editor" `
            -VarName "CLAUDE_IN_EDITOR" -VarValue $editor
        $stats.Env++
    }
    else {
        Write-Ok "[预演] 将设置 $editor/settings.json 中 env.CLAUDE_IN_EDITOR=$editor"
    }

    # ── CodeArts 专用：将 CLAUDE.md + rules/ 合并写入 additionalSystemPrompt ──
    # CodeArts 不自动读取 rules/ 目录或 CLAUDE.md，需要通过 additionalSystemPrompt 注入
    if (-not $DryRun) {
        $codeartsSettings = Join-Path $targetDir "settings.json"
        $es = Read-Json $codeartsSettings
        if ($null -ne $es) {
            # 构建 additionalSystemPrompt 内容（精简版 CLAUDE.md + alwaysApply 核心规则）
            $sb = [System.Text.StringBuilder]::new()
            # 使用精简版 CLAUDE.md（移除 [CC] 标记段落）
            $editorClaudeMd = Get-EditorClaudeMd
            if ($editorClaudeMd -ne "") {
                [void]$sb.AppendLine("## Project Instructions (CLAUDE.md)")
                [void]$sb.AppendLine("")
                [void]$sb.Append($editorClaudeMd)
                [void]$sb.AppendLine("")
                [void]$sb.AppendLine("")
            }
            $rulesSrc = Join-Path $CLAUDE_DIR "rules"
            if (Test-Path $rulesSrc) {
                # 只注入 alwaysApply:true 的核心规则（CORE + COMMON），避免 token 浪费
                $ruleFiles = Get-ChildItem $rulesSrc -Filter "RULES_*.md" | Sort-Object Name | Where-Object {
                    $c = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
                    $c -match 'alwaysApply:\s*true'
                }
                if ($ruleFiles.Count -gt 0) {
                    [void]$sb.AppendLine("## Core Coding Rules (alwaysApply)")
                    [void]$sb.AppendLine("")
                    foreach ($rf in $ruleFiles) {
                        $rfContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)
                        # 去掉 frontmatter
                        $body = $rfContent
                        if ($rfContent.StartsWith("---")) {
                            $secondDash = $rfContent.IndexOf("---", 3)
                            if ($secondDash -gt 0) {
                                $body = $rfContent.Substring($secondDash + 3).TrimStart()
                            }
                        }
                        $ruleName = $rf.BaseName -replace "^RULES_", ""
                        [void]$sb.AppendLine("### $ruleName Rules")
                        [void]$sb.AppendLine("")
                        [void]$sb.Append($body)
                        [void]$sb.AppendLine("")
                        [void]$sb.AppendLine("")
                    }
                }
            }
            $newPrompt = $sb.ToString()

            # 写入 codeartsAiFeaturesExtension.configuration.additionalSystemPrompt
            # 同时启用 promptEnabled，否则 additionalSystemPrompt 不会生效
            $configKey = "codeartsAiFeaturesExtension.configuration"
            if ($es.PSObject.Properties.Match($configKey).Count) {
                $config = $es.$configKey
                $oldPrompt = ""
                if ($config.PSObject.Properties.Match('additionalSystemPrompt').Count) {
                    $oldPrompt = $config.additionalSystemPrompt
                }
                $needUpdate = $false

                # 更新 additionalSystemPrompt
                if ($oldPrompt -ne $newPrompt) {
                    if (-not $config.PSObject.Properties.Match('additionalSystemPrompt').Count) {
                        $config | Add-Member -MemberType NoteProperty -Name 'additionalSystemPrompt' -Value $newPrompt -Force
                    } else {
                        $config.additionalSystemPrompt = $newPrompt
                    }
                    Write-Fix "additionalSystemPrompt 已更新 ($($newPrompt.Length) 字符)"
                    $needUpdate = $true
                } else {
                    Write-Ok "additionalSystemPrompt 已是最新"
                }

                # 启用 promptEnabled（若为 false 则改为 true）
                if ($config.PSObject.Properties.Match('promptEnabled').Count) {
                    if ($config.promptEnabled -ne $true) {
                        $config.promptEnabled = $true
                        Write-Fix "promptEnabled 已启用（原为 false）"
                        $needUpdate = $true
                    } else {
                        Write-Ok "promptEnabled 已启用"
                    }
                } else {
                    $config | Add-Member -MemberType NoteProperty -Name 'promptEnabled' -Value $true -Force
                    Write-Fix "promptEnabled 已添加并启用"
                    $needUpdate = $true
                }

                if ($needUpdate) {
                    # 备份后写回
                    Copy-Item $codeartsSettings ($codeartsSettings + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
                    Write-Json -Path $codeartsSettings -Obj $es
                    $stats.Files++
                }
            } else {
                Write-Warn "未找到 $configKey，跳过 additionalSystemPrompt 同步"
            }
        }
    }
    else {
        Write-Ok "[预演] 将更新 additionalSystemPrompt (精简版 CLAUDE.md + alwaysApply 核心规则)"
    }

    # Sync MCP configuration to CodeArts mcpServerRegistrations
    if (-not $DryRun) {
        $codeartsSettings = Join-Path $targetDir "settings.json"
        Sync-McpToCodeArts -SettingsPath $codeartsSettings -EditorName $editor
    }
    else {
        Write-Ok "[预演] 将同步 MCP 配置到 mcpServerRegistrations"
    }
}

Write-Host ""
Write-Host "  =====================================================" -ForegroundColor DarkGray
$syncDoneMsg = if ($DryRun) { "预演结束" } else { "同步完成" }
Write-Host "  $syncDoneMsg！" -ForegroundColor Green
Write-Host ""
Write-Host "  新建/确认链接数 : $($stats.Links)" -ForegroundColor White
Write-Host "  复制文件数       : $($stats.Files)" -ForegroundColor White
Write-Host "  环境写入次数     : $($stats.Env)" -ForegroundColor White
Write-Host "  MCP同步编辑器数  : $($stats.Mcp)" -ForegroundColor White
Write-Host "  格式转换配置项数  : $($stats.Converted)" -ForegroundColor White
Write-Host "  删除陈旧软链接   : $($stats.Removed)" -ForegroundColor White
Write-Host "  跳过编辑器数     : $($stats.Skipped)" -ForegroundColor White
if ($stats.Errors -gt 0) {
    Write-Host "  错误数           : $($stats.Errors)" -ForegroundColor Red
}
Write-Host ""
Write-Host "  已同步: skills/ agents/（链接） rules/（格式转换复制） CLAUDE.md（精简版） MCP（格式转换）" -ForegroundColor DarkGray
Write-Host "  原生规则: .cursor/rules/*.mdc | .windsurf/rules/*.md | .trae/user_rules/*.md" -ForegroundColor DarkGray
Write-Host "  Windsurf: global_rules.md(精简CLAUDE.md+核心规则) + skills/ + mcp_config.json → ~/.codeium/windsurf/" -ForegroundColor DarkGray
Write-Host "  CodeArts: additionalSystemPrompt ← 精简CLAUDE.md + alwaysApply核心规则 | mcpServerRegistrations ← MCP" -ForegroundColor DarkGray
Write-Host "  不同步: hooks/ scripts/ settings.json" -ForegroundColor DarkGray
Write-Host "  CLAUDE_IN_EDITOR: 已写入用户目录与 Roaming 的 settings.json" -ForegroundColor DarkGray
Write-Host "  terminal.integrated.env.windows: 已移除 CLAUDE_IN_EDITOR（保护 CLI 终端）" -ForegroundColor DarkGray
Write-Host ""
