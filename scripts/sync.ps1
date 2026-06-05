#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 多编辑器同步脚本 v14.0 — 索引 + 全量双模式

.DESCRIPTION
    索引模式(默认): 6 总纲软链接 + skills/agents/rules 目录联接
    全量模式(-Full): 6 总纲 + agents/ 联接 + rules/skills 编辑器原生格式转换副本

    不同步：commands/、hooks/、scripts/、MCP 配置。

.PARAMETER Full
    全量同步（agents 联接 + rules/skills 原生格式转换）

.PARAMETER Force
    强制重建所有链接

.PARAMETER DryRun
    仅预览，不写盘

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File sync.ps1
    powershell -ExecutionPolicy Bypass -File sync.ps1 -Full -Force
    powershell -ExecutionPolicy Bypass -File sync.ps1 -DryRun
#>

param(
    [switch]$Full,
    [switch]$Force,
    [switch]$DryRun
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$BACKUP_DIR = Join-Path $CLAUDE_DIR "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$EDITORS = @("cursor", "trae", "windsurf", "qoder")
$CODEARTS_EDITORS = @("codearts-agent")
$SYNC_DIRS = @("skills", "agents", "rules")
$SYNC_DIRS_FULL_LINK = @("agents")
$SYNC_DIRS_FULL_NATIVE = @("rules", "skills")
$SYNC_FILES = @("CLAUDE.md", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md", "rules-INDEX.md")
$STALE_LINKS = @("hooks", "scripts", "commands", "AGENTS.md")

# 编辑器原生规则目录映射（使用各编辑器真正识别的全局路径）
# Cursor: ~/.cursor/rules/*.mdc (项目级格式，放在用户目录下作为同步中转)
# Windsurf: ~/.windsurf/rules/*.md (项目级多文件) + ~/.codeium/windsurf/memories/global_rules.md (核心规则单文件)
# Trae: ~/.trae/user_rules/*.md (Trae特有的全局rules目录，支持alwaysApply frontmatter)
$NATIVE_RULES_DIR_MAP = @{
    "cursor"   = @{ TargetDir = (Join-Path $env:USERPROFILE ".cursor\rules"); Ext = ".mdc"; Format = "cursor" }
    "windsurf" = @{ TargetDir = (Join-Path $env:USERPROFILE ".windsurf\rules"); Ext = ".md"; Format = "windsurf" }
    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\user_rules"); Ext = ".md"; Format = "trae" }
    "qoder"    = @{ TargetDir = (Join-Path $env:USERPROFILE ".qoder\rules"); Ext = ".mdc"; Format = "cursor" }
}

# Full 模式：skills 原生副本目录（避免与 Index 模式 skills/ 联接冲突）
$NATIVE_SKILLS_DIR_MAP = @{
    "cursor"   = @{ TargetDir = (Join-Path $env:USERPROFILE ".cursor\skills-native"); Format = "cursor" }
    "windsurf" = @{ TargetDir = (Join-Path $env:USERPROFILE ".windsurf\skills-native"); Format = "windsurf" }
    "trae"     = @{ TargetDir = (Join-Path $env:USERPROFILE ".trae\skills-native"); Format = "trae" }
    "qoder"    = @{ TargetDir = (Join-Path $env:USERPROFILE ".qoder\skills-native"); Format = "cursor" }
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

    # 先删除同名目标（链接或实体文件），再创建新链接，杜绝重复
    if (Test-Path $Target) {
        if ($DryRun) { Write-Fix "[预演] 将删除旧目标: $Label"; $script:stats.Removed++ }
        else {
            # 文件链接直接用 Remove-Item；目录联接才需要 rmdir（此处只处理文件）
            Remove-Item $Target -Force -ErrorAction SilentlyContinue
            Write-Fix "已删除旧目标: $Label"
            $script:stats.Removed++
        }
    }

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
        version   = "14.0"
        updated   = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        source    = $CLAUDE_DIR
    } | ConvertTo-Json -Compress
    $path = Join-Path $TargetDir "sync-mode.json"
    [System.IO.File]::WriteAllText($path, $payload, [System.Text.Encoding]::UTF8)
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
        - Cursor: ~/.cursor/rules/*.mdc (每个规则一个文件，作为同步中转)
        - Windsurf: ~/.windsurf/rules/*.md (每个规则一个文件，遵守字符限制)
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

    # 清理旧规则文件（删除不在源中的 stale 文件，含旧 RULES_*.md/.mdc）
    if ((Test-Path $targetRulesDir) -and -not (IsLink $targetRulesDir)) {
        $validNames = $ruleFiles | ForEach-Object { "$($_.BaseName -replace '^RULES_','')$ext" }
        $validBaseNames = $ruleFiles | ForEach-Object { $_.BaseName -replace '^RULES_','' }
        $stalePatterns = @("*.mdc", "*.md")
        foreach ($pat in $stalePatterns) {
            $existing = Get-ChildItem $targetRulesDir -Filter $pat -ErrorAction SilentlyContinue
            foreach ($ef in $existing) {
                $base = $ef.BaseName -replace '^RULES_',''
                $isValid = ($ef.Name -in $validNames) -or ($base -in $validBaseNames -and $ef.Extension -eq $ext)
                if (-not $isValid) {
                    if ($DryRun) { Write-Fix "[预演] 将删除旧规则: $($ef.Name)" }
                    else { Remove-Item $ef.FullName -Force; Write-Fix "已删除旧规则: $($ef.Name)"; $stats.Removed++ }
                }
            }
        }
    }

    $syncedCount = 0
    $skippedCount = 0
    $truncatedCount = 0
    $totalChars = 0

    foreach ($rf in $ruleFiles) {
        $srcContent = [System.IO.File]::ReadAllText($rf.FullName, [System.Text.Encoding]::UTF8)
        $category = $rf.BaseName -replace "^RULES_", ""  # 兼容新旧命名

        $targetFileName = "$category$ext"
        $targetPath = Join-Path $targetRulesDir $targetFileName

        # 转换内容
        $convertedContent = if ($format -eq "cursor") {
            $srcContent
        }
        else {
            Convert-Frontmatter -Content $srcContent -Format $format
        }

        if ($format -eq "cursor" -and $category -eq "CORE") {
            $convertedContent += @"

<!-- sync v14 Full: 技能原生副本见 ~/.cursor/skills-native/<name>/SKILL.md；完整源 ~/.claude/skills/ -->
"@
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
                if ($DryRun) { Write-Fix "[预演] 将删除旧技能: $($ed.Name)" }
                else { Remove-Item $ed.FullName -Recurse -Force; Write-Fix "已删除旧技能: $($ed.Name)"; $stats.Removed++ }
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

        if ($format -eq "windsurf" -and $convertedContent.Length -gt $WINDSURF_MAX_CHARS_PER_FILE) {
            $convertedContent = Truncate-ToCharLimit -Content $convertedContent -Limit $WINDSURF_MAX_CHARS_PER_FILE
            $truncatedCount++
        }

        if ($DryRun) { $syncedCount++; continue }

        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

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
        Write-Fix "skills 已生成 $syncedCount 个 SKILL.md（$format 格式）→ $targetRoot"
        $stats.Files += $syncedCount
    }
    if ($skippedCount -gt 0) {
        Write-Ok "$skippedCount 个 SKILL.md 已是最新"
    }
    if ($truncatedCount -gt 0) {
        Write-Warn "$truncatedCount 个技能因超过 $($WINDSURF_MAX_CHARS_PER_FILE) 字符限制被截断"
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

function Convert-Frontmatter {
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

function Convert-RulesFrontmatter {
    param([string]$Content, [string]$Format)
    return Convert-Frontmatter -Content $Content -Format $Format
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 多编辑器同步脚本 v14.0" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录 : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标编辑器: $($EDITORS -join ', '), $($CODEARTS_EDITORS -join ', ')" -ForegroundColor DarkGray
$modeLabel = if ($Full) { "全量（agents联接 + rules/skills原生转换）" } else { "索引（6总纲软链 + skills/agents/rules联接）" }
Write-Host "  同步模式: $modeLabel" -ForegroundColor DarkGray
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
    Sync-EditorTarget -EditorName $editor -TargetDir $targetDir
}

# ── CodeArts agent 编辑器同步（目标目录为 AppData Roaming User 目录）──
foreach ($editor in $CODEARTS_EDITORS | Sort-Object) {
    $targetDir = $CODEARTS_USER_DIRS[$editor]
    if (-not $targetDir) {
        Write-Host ""
        Write-Host "  -- $editor (CodeArts) -----------------------------" -ForegroundColor DarkGray
        Write-Skip "未配置 $editor 的用户目录，跳过"
        $stats.Skipped++
        continue
    }
    Sync-EditorTarget -EditorName $editor -TargetDir $targetDir
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
    Write-Host "  已同步: 6总纲软链接 + agents/联接 + rules/skills 原生格式转换" -ForegroundColor DarkGray
    Write-Host "  切回索引: powershell -File sync.ps1 -Force" -ForegroundColor DarkGray
} else {
    Write-Host "  已同步: 6总纲软链接 + skills/agents/rules 目录联接" -ForegroundColor DarkGray
    Write-Host "  总纲执行: CLAUDE.md → MANIFEST.yaml → *-INDEX.md → SPEC.md" -ForegroundColor DarkGray
    Write-Host "  全量模式: powershell -File sync.ps1 -Full（+ rules/skills 原生转换）" -ForegroundColor DarkGray
}
Write-Host "  不同步: hooks/ scripts/ MCP配置 plugins/ commands/" -ForegroundColor DarkGray
Write-Host ""
