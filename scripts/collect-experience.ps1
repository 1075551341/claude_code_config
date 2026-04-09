#Requires -Version 5.1
<#
.SYNOPSIS
    开发经验收集与总结脚本
.DESCRIPTION
    从日常开发日志、Git 历史、任务计划中提取经验教训，
    整理成结构化的经验库，方便后续开发参考。
.NOTES
    用法：powershell -ExecutionPolicy Bypass -File collect-experience.ps1 [项目路径]
#>

param(
    [string]$ProjectPath = (Get-Location).Path
)

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$EXP_DIR = Join-Path $CLAUDE_DIR "experiences"
$LOG_DIR = Join-Path $CLAUDE_DIR "logs"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   开发经验收集与总结工具 v1.0                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 确保目录存在
New-Item -ItemType Directory -Path $EXP_DIR -Force | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd"
$expFile = Join-Path $EXP_DIR "experience-$timestamp.md"

$content = @"
# 开发经验总结 - $timestamp

## 📊 项目信息
- 项目路径：$ProjectPath
- 收集时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

"@

# ── 1. 从 Git 历史提取经验 ─────────────────────────
if (Test-Path (Join-Path $ProjectPath ".git")) {
    Write-Host "📝 分析 Git 提交历史..." -ForegroundColor Green

    $gitLog = git -C $ProjectPath log --oneline --since="7 days ago" --no-merges 2>$null
    if ($gitLog) {
        $content += @"

## 📋 最近一周 Git 提交
``````
$($gitLog | Out-String)
``````

"@

        # 统计提交类型
        $commitTypes = @{}
        foreach ($line in $gitLog) {
            if ($line -match '^\w+ (feat|fix|refactor|test|docs|chore|style|perf)') {
                $type = $Matches[1]
                $commitTypes[$type] = [int]$commitTypes[$type] + 1
            }
        }
        if ($commitTypes.Count -gt 0) {
            $content += "### 提交类型分布`n"
            foreach ($type in $commitTypes.Keys | Sort-Object) {
                $content += "- $type : $($commitTypes[$type]) 次`n"
            }
            $content += "`n"
        }
    }

    # 统计变更文件类型
    $changedFiles = git -C $ProjectPath diff --stat HEAD~10..HEAD --name-only 2>$null
    if ($changedFiles) {
        $extCounts = @{}
        foreach ($f in $changedFiles) {
            $ext = [System.IO.Path]::GetExtension($f)
            if ($ext) {
                $extCounts[$ext] = [int]$extCounts[$ext] + 1
            }
        }
        $content += "### 变更文件类型分布`n"
        foreach ($ext in $extCounts.Keys | Sort-Object { $extCounts[$_] } -Descending) {
            $content += "- $ext : $($extCounts[$ext]) 个文件`n"
        }
        $content += "`n"
    }
}

# ── 2. 从任务计划提取经验 ─────────────────────────
$plansDir = Join-Path (Join-Path $ProjectPath ".claude") "plans"
if (Test-Path $plansDir) {
    Write-Host "📝 分析任务计划..." -ForegroundColor Green

    $plans = Get-ChildItem -Path $plansDir -Filter "*.md" -Exclude "latest.md" |
             Sort-Object LastWriteTime -Descending |
             Select-Object -First 5

    if ($plans.Count -gt 0) {
        $content += @"

## 📑 最近任务计划
"@
        foreach ($plan in $plans) {
            $content += "- $($plan.BaseName) ($($plan.LastWriteTime.ToString('yyyy-MM-dd')))`n"
        }
        $content += "`n"
    }
}

# ── 3. 从操作日志提取模式 ─────────────────────────
$opsLog = Join-Path $LOG_DIR "operations.log"
if (Test-Path $opsLog) {
    Write-Host "📝 分析操作日志..." -ForegroundColor Green

    $logContent = Get-Content $opsLog -Tail 200 -ErrorAction SilentlyContinue
    if ($logContent) {
        $toolCounts = @{}
        foreach ($line in $logContent) {
            if ($line -match '\[(\w+)\]') {
                $tool = $Matches[1]
                $toolCounts[$tool] = [int]$toolCounts[$tool] + 1
            }
        }
        if ($toolCounts.Count -gt 0) {
            $content += "### 工具使用频率`n"
            foreach ($tool in $toolCounts.Keys | Sort-Object { $toolCounts[$_] } -Descending | Select-Object -First 10) {
                $content += "- $tool : $($toolCounts[$tool]) 次`n"
            }
            $content += "`n"
        }
    }
}

# ── 4. 经验建议 ──────────────────────────────────
$content += @"

## 💡 自动化建议

1. **高频操作**：考虑为高频工具操作创建快捷命令
2. **重复模式**：识别重复的代码模式，抽取为共享组件/工具
3. **测试覆盖**：检查 fix 类型提交对应的测试是否补充
4. **文档同步**：确保 docs 类型提交与代码变更同步

---

> 此报告由 collect-experience.ps1 自动生成
"@

# 写入文件
$content | Out-File -FilePath $expFile -Encoding utf8

Write-Host ""
Write-Host "✅ 经验总结已生成：$expFile" -ForegroundColor Green
Write-Host ""
