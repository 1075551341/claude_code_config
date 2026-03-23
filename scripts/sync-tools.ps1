#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 工具同步脚本 v3.1（增强版）
.DESCRIPTION
    将 ~/.claude 中的 skills、agents、rules、hooks、scripts 等资源
    通过软链接（符号链接/Junction）同步到 Cursor、Trae、Qoder、Windsurf 等编辑器。
    同时以文件副本方式同步 CLAUDE.md、.mcp.json、settings.json。
    支持 -Force 强制重建链接，支持 -DryRun 预览模式。
.PARAMETER Force
    强制重建所有软链接（即使已存在且正确）
.PARAMETER DryRun
    预览模式，不实际执行任何操作
.NOTES
    需要以管理员权限运行（创建符号链接需要）
    用法：powershell -ExecutionPolicy Bypass -File sync-tools.ps1 [-Force] [-DryRun]
#>

param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$BACKUP_DIR = Join-Path (Join-Path $CLAUDE_DIR "backups") (Get-Date -Format "yyyyMMdd_HHmmss")
$TARGETS = @("cursor", "trae", "qoder", "windsurf")

# 需要通过软链接同步的目录
$SYNC_DIRS = @("skills", "agents", "rules", "hooks", "scripts")

# 需要以文件副本方式同步的配置文件
$SYNC_FILES = @("CLAUDE.md", ".mcp.json", "settings.json")

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Claude Code 工具同步脚本 v3.1 (增强版)          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  源目录: $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  目标:   $($TARGETS -join ', ')" -ForegroundColor DarkGray
if ($DryRun) {
    Write-Host "  模式:   预览（不实际执行）" -ForegroundColor Yellow
}
if ($Force) {
    Write-Host "  选项:   强制重建所有链接" -ForegroundColor Yellow
}
Write-Host ""

# ── 检查管理员权限 ─────────────────────────────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "  已获取管理员权限，将使用符号链接" -ForegroundColor Green
} else {
    Write-Host "  非管理员模式，将使用 Junction 方式替代" -ForegroundColor Yellow
}
Write-Host ""

# ── 创建备份目录 ───────────────────────────────────────────
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

# ── 统计变量 ───────────────────────────────────────────────
$stats = @{
    LinkCreated   = 0
    LinkSkipped   = 0
    LinkRepaired  = 0
    FileCopied    = 0
    FileSkipped   = 0
    BackupCount   = 0
    ErrorCount    = 0
    TargetSkipped = 0
}

# ── 校验软链接目标是否正确 ─────────────────────────────────
function Test-SymlinkTarget {
    param(
        [string]$LinkPath,
        [string]$ExpectedTarget
    )
    try {
        $item = Get-Item $LinkPath -Force -ErrorAction Stop
        if (-not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            return $false
        }
        $actualTarget = $item.Target
        if ($actualTarget -is [array]) { $actualTarget = $actualTarget[0] }
        return ($actualTarget -eq $ExpectedTarget)
    } catch {
        return $false
    }
}

foreach ($target in $TARGETS) {
    $targetDir = Join-Path $env:USERPROFILE ".$target"

    if (-not (Test-Path $targetDir)) {
        Write-Host "  .$target 目录不存在，跳过" -ForegroundColor Yellow
        $stats.TargetSkipped++
        continue
    }

    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "  同步到 .$target" -ForegroundColor Green
    Write-Host ""

    # ── 同步目录（软链接方式）──────────────────────────────
    foreach ($item in $SYNC_DIRS) {
        $sourcePath = Join-Path $CLAUDE_DIR $item
        $targetPath = Join-Path $targetDir $item

        if (-not (Test-Path $sourcePath)) {
            Write-Host "    源目录 $item 不存在，跳过" -ForegroundColor Yellow
            continue
        }

        if (Test-Path $targetPath) {
            $itemInfo = Get-Item $targetPath -Force
            $isReparsePoint = $itemInfo.Attributes -band [IO.FileAttributes]::ReparsePoint

            if ($isReparsePoint -and -not $Force) {
                $targetCorrect = Test-SymlinkTarget -LinkPath $targetPath -ExpectedTarget $sourcePath
                if ($targetCorrect) {
                    Write-Host "    $item 已是正确的软链接" -ForegroundColor DarkGreen
                    $stats.LinkSkipped++
                    continue
                } else {
                    Write-Host "    $item 软链接目标不正确，将修复" -ForegroundColor Yellow
                    if (-not $DryRun) {
                        Remove-Item -Path $targetPath -Force
                    }
                    $stats.LinkRepaired++
                }
            } elseif ($isReparsePoint -and $Force) {
                Write-Host "    $item 强制重建软链接" -ForegroundColor Yellow
                if (-not $DryRun) {
                    Remove-Item -Path $targetPath -Force
                }
            } else {
                $backupPath = Join-Path $BACKUP_DIR "${target}_${item}"
                Write-Host "    备份已有 $item -> $backupPath" -ForegroundColor DarkCyan
                if (-not $DryRun) {
                    Copy-Item -Path $targetPath -Destination $backupPath -Recurse -Force
                    Remove-Item -Path $targetPath -Recurse -Force
                }
                $stats.BackupCount++
            }
        }

        if ($DryRun) {
            Write-Host "    [预览] 将创建 $item 软链接" -ForegroundColor Cyan
            $stats.LinkCreated++
            continue
        }

        Write-Host "    创建 $item 软链接..." -ForegroundColor Cyan
        try {
            if ($isAdmin) {
                New-Item -ItemType SymbolicLink -Path $targetPath -Target $sourcePath -Force | Out-Null
            } else {
                $mkResult = cmd /c "mklink /J `"$targetPath`" `"$sourcePath`"" 2>&1
                if ($LASTEXITCODE -ne 0) {
                    throw "mklink 失败: $mkResult"
                }
            }
            Write-Host "    $item 同步完成" -ForegroundColor Green
            $stats.LinkCreated++
        } catch {
            Write-Host "    $item 同步失败: $_" -ForegroundColor Red
            $stats.ErrorCount++
        }
    }

    # ── 同步配置文件（副本方式）────────────────────────────
    foreach ($fileName in $SYNC_FILES) {
        $sourceFile = Join-Path $CLAUDE_DIR $fileName
        $targetFile = Join-Path $targetDir $fileName

        if (-not (Test-Path $sourceFile)) {
            continue
        }

        $needCopy = $false
        if (-not (Test-Path $targetFile)) {
            $needCopy = $true
        } else {
            $sourceHash = (Get-FileHash $sourceFile -Algorithm MD5).Hash
            $targetHash = (Get-FileHash $targetFile -Algorithm MD5).Hash
            if ($sourceHash -ne $targetHash) {
                $needCopy = $true
            }
        }

        if ($needCopy) {
            if ($DryRun) {
                Write-Host "    [预览] 将复制 $fileName（内容有更新）" -ForegroundColor DarkCyan
            } else {
                Copy-Item -Path $sourceFile -Destination $targetFile -Force
                Write-Host "    已复制 $fileName（内容已更新）" -ForegroundColor DarkCyan
            }
            $stats.FileCopied++
        } else {
            Write-Host "    $fileName 内容一致，无需更新" -ForegroundColor DarkGreen
            $stats.FileSkipped++
        }
    }

    Write-Host ""
}

# ── 同步结果统计 ───────────────────────────────────────────
$stopwatch.Stop()
$elapsed = $stopwatch.Elapsed

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  同步结果统计" -ForegroundColor Green
Write-Host "┌──────────────────────────────────────────────────┐" -ForegroundColor DarkGray
Write-Host "│  新建软链接:   $($stats.LinkCreated.ToString().PadLeft(3)) 个                             │" -ForegroundColor White
Write-Host "│  已有软链接:   $($stats.LinkSkipped.ToString().PadLeft(3)) 个（跳过）                     │" -ForegroundColor White
Write-Host "│  修复软链接:   $($stats.LinkRepaired.ToString().PadLeft(3)) 个（目标不正确已修复）        │" -ForegroundColor White
Write-Host "│  复制配置文件: $($stats.FileCopied.ToString().PadLeft(3)) 个                             │" -ForegroundColor White
Write-Host "│  文件无变化:   $($stats.FileSkipped.ToString().PadLeft(3)) 个（跳过）                     │" -ForegroundColor White
Write-Host "│  备份数量:     $($stats.BackupCount.ToString().PadLeft(3)) 个                             │" -ForegroundColor White
Write-Host "│  跳过目标:     $($stats.TargetSkipped.ToString().PadLeft(3)) 个（目录不存在）             │" -ForegroundColor White
if ($stats.ErrorCount -gt 0) {
    Write-Host "│  错误:         $($stats.ErrorCount.ToString().PadLeft(3)) 个                             │" -ForegroundColor Red
}
Write-Host "│  耗时:         $($elapsed.TotalSeconds.ToString('F1').PadLeft(5))s                           │" -ForegroundColor White
Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor DarkGray
Write-Host ""

if ($DryRun) {
    Write-Host "  以上为预览结果，实际未执行任何操作" -ForegroundColor Yellow
    Write-Host "  去掉 -DryRun 参数以实际执行同步" -ForegroundColor Yellow
} elseif ($stats.ErrorCount -eq 0) {
    Write-Host "  全部同步完成！" -ForegroundColor Green
} else {
    Write-Host "  同步完成，但有 $($stats.ErrorCount) 个错误，请检查上方日志" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  提示:" -ForegroundColor Yellow
Write-Host "   - 修改 skill/agent/rule/hook → 软链接自动同步，无需重新运行"
Write-Host "   - 修改 CLAUDE.md / .mcp.json / settings.json → 需重新运行以同步副本"
Write-Host "   - 使用 -Force 参数可强制重建所有软链接"
Write-Host "   - 使用 -DryRun 参数可预览同步操作"
Write-Host ""
