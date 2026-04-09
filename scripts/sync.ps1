#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 多编辑器同步脚本 v8.5

.DESCRIPTION
    从 ~/.claude 向各编辑器用户目录同步以下内容：
      - skills/、agents/、rules/ → 目录联接（Junction）或符号链接
      - CLAUDE.md、TOOL_MATCHING_GUIDE.md、SYNC_GUIDE.md → 文件复制
      - 新增：自动同步 agents/tool-matcher.md（工具匹配专家）

    同时向各编辑器 settings.json 合并写入 env.CLAUDE_IN_EDITOR（与 fix.ps1 中
    _editor_hook_launcher 的 GetConsoleWindow() 判定互为补充）。

    合并策略不破坏界面配置：若已有 settings.json 无法按严格 JSON 解析（如含 // 的 JSONC、
    尾逗号等），则跳过写入并告警，不会用空对象覆盖字体、主题、workbench 等项；写回时使用
    ConvertTo-Json -Depth 100，避免深层嵌套（如颜色自定义）被截断。

    不同步：hooks/、scripts/、.mcp.json、以及 .claude 下的 settings.json（不把 CLI 整份配置拷到编辑器）。
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
$SYNC_DIRS = @("skills", "agents", "rules")
$COPY_FILES = @("CLAUDE.md", "TOOL_MATCHING_GUIDE.md", "SYNC_GUIDE.md")
$STALE_LINKS = @("hooks", "scripts")

# 各编辑器 Roaming 用户设置路径（VS Code 系）
$ROAMING_SETTINGS = @{
    "cursor"   = (Join-Path $env:APPDATA "Cursor\User\settings.json")
    "windsurf" = (Join-Path $env:APPDATA "Windsurf\User\settings.json")
    "trae"     = (Join-Path $env:APPDATA "Trae\User\settings.json")
    "qoder"    = (Join-Path $env:APPDATA "Qoder\User\settings.json")
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

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 多编辑器同步脚本 v8.5" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录 : $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标编辑器: $($EDITORS -join ', ')" -ForegroundColor DarkGray
Write-Host "  同步项 : $($SYNC_DIRS -join ', ')  +  CLAUDE.md（复制）" -ForegroundColor DarkGray
Write-Host "  环境变量: 仅合并 env.CLAUDE_IN_EDITOR；已清理集成终端 env" -ForegroundColor DarkGray
$syncModeLabel = if ($isAdmin) { "管理员（符号链接）" } else { "非管理员（目录联接，Junction）" }
Write-Host "  模式   : $syncModeLabel" -ForegroundColor DarkGray
if ($DryRun) { Write-Host "  [预演] 仅预览，不写盘" -ForegroundColor Yellow }
if ($Force) { Write-Host "  [强制] 重建全部链接" -ForegroundColor Yellow }
Write-Host ""

if (-not $DryRun) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

$stats = @{ Links = 0; Files = 0; Removed = 0; Env = 0; Errors = 0; Skipped = 0 }

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

    # Copy files (CLAUDE.md must be real file, not symlink)
    foreach ($file in $COPY_FILES) {
        $src = Join-Path $CLAUDE_DIR $file
        $dst = Join-Path $targetDir $file
        if (-not (Test-Path $src)) { Write-Skip "源文件缺失: $file"; continue }
        if ((Test-Path $dst) -and (IsLink $dst)) {
            if (-not $DryRun) { Remove-Item $dst -Force; Write-Fix "$file 原为软链接，已改为复制文件" }
        }
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

Write-Host ""
Write-Host "  =====================================================" -ForegroundColor DarkGray
$syncDoneMsg = if ($DryRun) { "预演结束" } else { "同步完成" }
Write-Host "  $syncDoneMsg！" -ForegroundColor Green
Write-Host ""
Write-Host "  新建/确认链接数 : $($stats.Links)" -ForegroundColor White
Write-Host "  复制文件数       : $($stats.Files)" -ForegroundColor White
Write-Host "  环境写入次数     : $($stats.Env)" -ForegroundColor White
Write-Host "  删除陈旧软链接   : $($stats.Removed)" -ForegroundColor White
Write-Host "  跳过编辑器数     : $($stats.Skipped)" -ForegroundColor White
if ($stats.Errors -gt 0) {
    Write-Host "  错误数           : $($stats.Errors)" -ForegroundColor Red
}
Write-Host ""
Write-Host "  已同步: skills/ agents/ rules/（链接） CLAUDE.md（复制）" -ForegroundColor DarkGray
Write-Host "  不同步: hooks/ scripts/ settings.json .mcp.json" -ForegroundColor DarkGray
Write-Host "  CLAUDE_IN_EDITOR: 已写入用户目录与 Roaming 的 settings.json" -ForegroundColor DarkGray
Write-Host "  terminal.integrated.env.windows: 已移除 CLAUDE_IN_EDITOR（保护 CLI 终端）" -ForegroundColor DarkGray
Write-Host ""
