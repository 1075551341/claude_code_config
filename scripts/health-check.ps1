#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 环境健康检查脚本 v1.1（增强版）
.DESCRIPTION
    全面检查 .claude 开发环境的完整性和健康状态，包括：
    目录结构、配置文件、hooks 一致性、运行环境、MCP 服务器、软链接等。
    输出可读的健康报告并保存到 logs 目录。
.NOTES
    用法：powershell -ExecutionPolicy Bypass -File health-check.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$TARGETS = @("cursor", "trae", "qoder", "windsurf")

$checkResults = @()
$passCount = 0
$warnCount = 0
$failCount = 0

function Add-Check {
    param(
        [string]$Category,
        [string]$Item,
        [string]$Status,
        [string]$Detail
    )
    $script:checkResults += @{
        Category = $Category
        Item     = $Item
        Status   = $Status
        Detail   = $Detail
    }
    switch ($Status) {
        "pass" { $script:passCount++; Write-Host "   [OK] $Item" -ForegroundColor Green -NoNewline }
        "warn" { $script:warnCount++; Write-Host "   [!]  $Item" -ForegroundColor Yellow -NoNewline }
        "fail" { $script:failCount++; Write-Host "   [X]  $Item" -ForegroundColor Red -NoNewline }
    }
    if ($Detail) {
        Write-Host " — $Detail" -ForegroundColor DarkGray
    } else {
        Write-Host ""
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Claude Code 环境健康检查 v1.1 (增强版)     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  检查目录: $CLAUDE_DIR" -ForegroundColor DarkGray
Write-Host "  检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host ""

# ══════════════════════════════════════════════════════
# 1. 目录结构完整性
# ══════════════════════════════════════════════════════
Write-Host "  目录结构完整性" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$requiredDirs = @(
    @{ Path = "skills";      Desc = "技能库" }
    @{ Path = "agents";      Desc = "代理配置" }
    @{ Path = "rules";       Desc = "规则文件" }
    @{ Path = "hooks";       Desc = "钩子脚本" }
    @{ Path = "scripts";     Desc = "工具脚本" }
    @{ Path = "logs";        Desc = "日志目录" }
    @{ Path = "experiences"; Desc = "经验积累" }
    @{ Path = "plans";       Desc = "计划文档" }
    @{ Path = "backups";     Desc = "备份目录" }
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $CLAUDE_DIR $dir.Path
    if (Test-Path $fullPath) {
        $itemCount = (Get-ChildItem -Path $fullPath -Recurse -File -ErrorAction SilentlyContinue).Count
        Add-Check -Category "目录结构" -Item "$($dir.Desc) ($($dir.Path)/)" -Status "pass" -Detail "$itemCount 个文件"
    } else {
        Add-Check -Category "目录结构" -Item "$($dir.Desc) ($($dir.Path)/)" -Status "warn" -Detail "目录不存在"
    }
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 2. 关键配置文件
# ══════════════════════════════════════════════════════
Write-Host "  关键配置文件" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$requiredFiles = @(
    @{ Path = "CLAUDE.md";     Desc = "全局行为规范" }
    @{ Path = "settings.json"; Desc = "Claude 设置" }
    @{ Path = ".mcp.json";     Desc = "MCP 服务器配置" }
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $CLAUDE_DIR $file.Path
    if (Test-Path $fullPath) {
        $fileInfo = Get-Item $fullPath
        $sizeKB = [math]::Round($fileInfo.Length / 1KB, 1)
        Add-Check -Category "配置文件" -Item $file.Desc -Status "pass" -Detail "$($file.Path) (${sizeKB}KB)"
    } else {
        Add-Check -Category "配置文件" -Item $file.Desc -Status "fail" -Detail "$($file.Path) 不存在"
    }
}

# settings.json 有效性检查
$settingsPath = Join-Path $CLAUDE_DIR "settings.json"
if (Test-Path $settingsPath) {
    try {
        $content = Get-Content $settingsPath -Raw -Encoding utf8
        $settingsObj = $content | ConvertFrom-Json
        Add-Check -Category "配置文件" -Item "settings.json 格式" -Status "pass" -Detail "JSON 语法正确"

        # 检查关键字段
        $hasHooks = $null -ne $settingsObj.hooks
        $hasPermissions = $null -ne $settingsObj.permissions
        $hasMcpServers = $null -ne $settingsObj.mcpServers
        $fieldDetail = @()
        if ($hasHooks) { $fieldDetail += "hooks" }
        if ($hasPermissions) { $fieldDetail += "permissions" }
        if ($hasMcpServers) { $fieldDetail += "mcpServers" }
        Add-Check -Category "配置文件" -Item "settings.json 关键字段" -Status "pass" -Detail "包含: $($fieldDetail -join ', ')"
    } catch {
        Add-Check -Category "配置文件" -Item "settings.json 格式" -Status "fail" -Detail "JSON 解析失败: $_"
    }
}

# .mcp.json 有效性检查
$mcpJsonPath = Join-Path $CLAUDE_DIR ".mcp.json"
if (Test-Path $mcpJsonPath) {
    try {
        $content = Get-Content $mcpJsonPath -Raw -Encoding utf8
        $mcpConfig = $content | ConvertFrom-Json
        $serverCount = 0
        if ($mcpConfig.mcpServers) {
            $serverCount = ($mcpConfig.mcpServers | Get-Member -MemberType NoteProperty).Count
        }
        Add-Check -Category "配置文件" -Item ".mcp.json 格式" -Status "pass" -Detail "JSON 正确，$serverCount 个 MCP 服务器"
    } catch {
        Add-Check -Category "配置文件" -Item ".mcp.json 格式" -Status "fail" -Detail "JSON 解析失败: $_"
    }
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 3. Hooks 钩子检查（含 settings.json 交叉校验）
# ══════════════════════════════════════════════════════
Write-Host "  Hooks 钩子检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$hooksDir = Join-Path $CLAUDE_DIR "hooks"
if (Test-Path $hooksDir) {
    $hookFiles = Get-ChildItem -Path $hooksDir -File -Filter "*.py"
    if ($hookFiles.Count -gt 0) {
        foreach ($hook in $hookFiles) {
            $hookContent = Get-Content $hook.FullName -Raw -ErrorAction SilentlyContinue
            if ($hookContent -and $hookContent.Length -gt 10) {
                Add-Check -Category "Hooks" -Item $hook.Name -Status "pass" -Detail "$([math]::Round($hook.Length / 1KB, 1))KB"
            } else {
                Add-Check -Category "Hooks" -Item $hook.Name -Status "warn" -Detail "文件内容为空或过短"
            }
        }

        # settings.json 中引用的 hook 文件交叉校验
        if ($settingsObj -and $settingsObj.hooks) {
            $referencedFiles = @()
            $hookCategories = $settingsObj.hooks | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
            foreach ($cat in $hookCategories) {
                $entries = $settingsObj.hooks.$cat
                foreach ($entry in $entries) {
                    foreach ($h in $entry.hooks) {
                        if ($h.command -match "([^\s/\\]+\.py)") {
                            $referencedFiles += $Matches[1]
                        }
                    }
                }
            }

            $localHookNames = $hookFiles | Select-Object -ExpandProperty Name
            $missingFromDisk = $referencedFiles | Where-Object { $localHookNames -notcontains $_ } | Select-Object -Unique
            if ($missingFromDisk.Count -gt 0) {
                foreach ($mf in $missingFromDisk) {
                    Add-Check -Category "Hooks" -Item "settings.json 引用: $mf" -Status "fail" -Detail "文件不存在于 hooks 目录"
                }
            } else {
                Add-Check -Category "Hooks" -Item "配置一致性" -Status "pass" -Detail "settings.json 引用的 $($referencedFiles.Count) 个文件均存在"
            }
        }
    } else {
        Add-Check -Category "Hooks" -Item "钩子文件" -Status "warn" -Detail "hooks 目录为空"
    }
} else {
    Add-Check -Category "Hooks" -Item "hooks 目录" -Status "fail" -Detail "目录不存在"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 4. Python 环境检查（hooks 运行依赖）
# ══════════════════════════════════════════════════════
Write-Host "  Python 环境检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pyVer = & python --version 2>&1
    Add-Check -Category "Python" -Item "Python 解释器" -Status "pass" -Detail "$pyVer"

    $pipCmd = Get-Command pip -ErrorAction SilentlyContinue
    if ($pipCmd) {
        Add-Check -Category "Python" -Item "pip 包管理器" -Status "pass" -Detail ""
    } else {
        Add-Check -Category "Python" -Item "pip 包管理器" -Status "warn" -Detail "未找到 pip"
    }

    $pyDeps = @("json", "os", "sys", "pathlib", "subprocess", "datetime")
    $depFail = @()
    foreach ($dep in $pyDeps) {
        $result = & python -c "import $dep" 2>&1
        if ($LASTEXITCODE -ne 0) { $depFail += $dep }
    }
    if ($depFail.Count -eq 0) {
        Add-Check -Category "Python" -Item "标准库模块" -Status "pass" -Detail "核心模块均可用"
    } else {
        Add-Check -Category "Python" -Item "标准库模块" -Status "fail" -Detail "缺失: $($depFail -join ', ')"
    }
} else {
    Add-Check -Category "Python" -Item "Python 解释器" -Status "fail" -Detail "未安装，hooks 将无法运行"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 5. Node.js / npm / pnpm 检查
# ══════════════════════════════════════════════════════
Write-Host "  Node.js 环境检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$nodeTools = @(
    @{ Cmd = "node";  Name = "Node.js";   VerArg = "--version" }
    @{ Cmd = "npm";   Name = "npm";       VerArg = "--version" }
    @{ Cmd = "pnpm";  Name = "pnpm";      VerArg = "--version" }
    @{ Cmd = "npx";   Name = "npx";       VerArg = "--version" }
)

foreach ($tool in $nodeTools) {
    $found = Get-Command $tool.Cmd -ErrorAction SilentlyContinue
    if ($found) {
        $ver = & $tool.Cmd $tool.VerArg 2>&1 | Select-Object -First 1
        Add-Check -Category "Node.js" -Item $tool.Name -Status "pass" -Detail $ver
    } else {
        $status = if ($tool.Cmd -eq "pnpm") { "warn" } else { "fail" }
        Add-Check -Category "Node.js" -Item $tool.Name -Status $status -Detail "未安装"
    }
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 6. Git 配置检查
# ══════════════════════════════════════════════════════
Write-Host "  Git 配置检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if ($gitCmd) {
    $gitVer = & git --version 2>&1
    Add-Check -Category "Git" -Item "Git" -Status "pass" -Detail $gitVer

    $userName = & git config --global user.name 2>&1
    if ($userName -and $LASTEXITCODE -eq 0) {
        Add-Check -Category "Git" -Item "user.name" -Status "pass" -Detail $userName
    } else {
        Add-Check -Category "Git" -Item "user.name" -Status "warn" -Detail "未配置全局 user.name"
    }

    $userEmail = & git config --global user.email 2>&1
    if ($userEmail -and $LASTEXITCODE -eq 0) {
        Add-Check -Category "Git" -Item "user.email" -Status "pass" -Detail $userEmail
    } else {
        Add-Check -Category "Git" -Item "user.email" -Status "warn" -Detail "未配置全局 user.email"
    }

    $defaultBranch = & git config --global init.defaultBranch 2>&1
    if ($defaultBranch -and $LASTEXITCODE -eq 0) {
        Add-Check -Category "Git" -Item "默认分支" -Status "pass" -Detail $defaultBranch
    } else {
        Add-Check -Category "Git" -Item "默认分支" -Status "warn" -Detail "未设置，默认为 master"
    }
} else {
    Add-Check -Category "Git" -Item "Git" -Status "fail" -Detail "未安装"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 7. Docker 检查
# ══════════════════════════════════════════════════════
Write-Host "  Docker 环境检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    $dockerVer = & docker --version 2>&1
    Add-Check -Category "Docker" -Item "Docker CLI" -Status "pass" -Detail $dockerVer

    $dockerInfo = & docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Check -Category "Docker" -Item "Docker 守护进程" -Status "pass" -Detail "运行中"
    } else {
        Add-Check -Category "Docker" -Item "Docker 守护进程" -Status "warn" -Detail "未运行或无权限"
    }
} else {
    Add-Check -Category "Docker" -Item "Docker" -Status "warn" -Detail "未安装"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 8. MCP 服务器连接检查
# ══════════════════════════════════════════════════════
Write-Host "  MCP 服务器连接检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Redis
$redisCli = Get-Command redis-cli -ErrorAction SilentlyContinue
if ($redisCli) {
    try {
        $redisPing = & redis-cli ping 2>&1
        if ($redisPing -and $redisPing.ToString().Trim() -eq "PONG") {
            Add-Check -Category "MCP" -Item "Redis" -Status "pass" -Detail "连接正常 (PONG)"
        } else {
            Add-Check -Category "MCP" -Item "Redis" -Status "warn" -Detail "客户端已安装，服务未响应"
        }
    } catch {
        Add-Check -Category "MCP" -Item "Redis" -Status "warn" -Detail "连接测试失败"
    }
} else {
    Add-Check -Category "MCP" -Item "Redis" -Status "warn" -Detail "redis-cli 未安装"
}

# PostgreSQL
$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlCmd) {
    try {
        $portOpen = $false
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 5432)
        $portOpen = $tcp.Connected
        $tcp.Close()
        if ($portOpen) {
            Add-Check -Category "MCP" -Item "PostgreSQL" -Status "pass" -Detail "服务运行中 (端口 5432)"
        } else {
            Add-Check -Category "MCP" -Item "PostgreSQL" -Status "warn" -Detail "客户端已安装，服务未运行"
        }
    } catch {
        Add-Check -Category "MCP" -Item "PostgreSQL" -Status "warn" -Detail "端口 5432 不可达"
    }
} else {
    Add-Check -Category "MCP" -Item "PostgreSQL" -Status "warn" -Detail "psql 未安装"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 9. 软链接状态检查
# ══════════════════════════════════════════════════════
Write-Host "  软链接状态检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$syncDirs = @("skills", "agents", "rules", "hooks", "scripts")

foreach ($target in $TARGETS) {
    $targetDir = Join-Path $env:USERPROFILE ".$target"
    if (-not (Test-Path $targetDir)) {
        Add-Check -Category "软链接" -Item ".$target" -Status "warn" -Detail "目标目录不存在"
        continue
    }

    $linkedCount = 0
    $missingCount = 0
    $wrongTarget = 0
    $missingItems = @()

    foreach ($dir in $syncDirs) {
        $linkPath = Join-Path $targetDir $dir
        $expectedTarget = Join-Path $CLAUDE_DIR $dir

        if (Test-Path $linkPath) {
            $info = Get-Item $linkPath -Force
            if ($info.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                $actualTarget = $info.Target
                if ($actualTarget -is [array]) { $actualTarget = $actualTarget[0] }
                if ($actualTarget -eq $expectedTarget) {
                    $linkedCount++
                } else {
                    $wrongTarget++
                    $missingItems += "$dir(目标不正确)"
                }
            } else {
                $missingCount++
                $missingItems += $dir
            }
        } else {
            $missingCount++
            $missingItems += $dir
        }
    }

    $totalIssues = $missingCount + $wrongTarget
    if ($totalIssues -eq 0) {
        Add-Check -Category "软链接" -Item ".$target" -Status "pass" -Detail "全部 $linkedCount 个目录已正确链接"
    } elseif ($linkedCount -gt 0) {
        Add-Check -Category "软链接" -Item ".$target" -Status "warn" -Detail "已链接 $linkedCount 个，问题: $($missingItems -join ', ')"
    } else {
        Add-Check -Category "软链接" -Item ".$target" -Status "warn" -Detail "尚未同步，运行 sync-tools.ps1"
    }
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 10. 磁盘空间检查
# ══════════════════════════════════════════════════════
Write-Host "  磁盘空间检查" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

try {
    $drive = (Get-Item $CLAUDE_DIR).PSDrive
    $freeGB = [math]::Round($drive.Free / 1GB, 1)
    $usedGB = [math]::Round($drive.Used / 1GB, 1)
    $totalGB = [math]::Round(($drive.Free + $drive.Used) / 1GB, 1)
    $freePercent = [math]::Round(($drive.Free / ($drive.Free + $drive.Used)) * 100)

    if ($freePercent -gt 20) {
        Add-Check -Category "磁盘" -Item "$($drive.Name): 驱动器" -Status "pass" -Detail "可用 ${freeGB}GB / 共 ${totalGB}GB (${freePercent}% 空闲)"
    } elseif ($freePercent -gt 10) {
        Add-Check -Category "磁盘" -Item "$($drive.Name): 驱动器" -Status "warn" -Detail "可用 ${freeGB}GB / 共 ${totalGB}GB (${freePercent}% 空闲，建议清理)"
    } else {
        Add-Check -Category "磁盘" -Item "$($drive.Name): 驱动器" -Status "fail" -Detail "可用 ${freeGB}GB / 共 ${totalGB}GB (${freePercent}% 空闲，空间不足)"
    }

    # .claude 目录大小
    $claudeSize = (Get-ChildItem -Path $CLAUDE_DIR -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $claudeSizeMB = [math]::Round($claudeSize / 1MB, 1)
    Add-Check -Category "磁盘" -Item ".claude 目录大小" -Status "pass" -Detail "${claudeSizeMB}MB"
} catch {
    Add-Check -Category "磁盘" -Item "磁盘信息" -Status "warn" -Detail "无法获取磁盘信息"
}

Write-Host ""

# ══════════════════════════════════════════════════════
# 11. 健康报告汇总
# ══════════════════════════════════════════════════════
$totalChecks = $passCount + $warnCount + $failCount
$healthScore = if ($totalChecks -gt 0) { [math]::Round(($passCount / $totalChecks) * 100) } else { 0 }

if ($healthScore -ge 90) {
    $healthColor = "Green"
    $healthEmoji = "[优秀]"
} elseif ($healthScore -ge 70) {
    $healthColor = "Yellow"
    $healthEmoji = "[良好]"
} else {
    $healthColor = "Red"
    $healthEmoji = "[需改善]"
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  $healthEmoji 环境健康评分: $healthScore / 100" -ForegroundColor $healthColor
Write-Host ""
Write-Host "┌──────────────────────────────────────────┐" -ForegroundColor DarkGray
Write-Host "│  通过: $($passCount.ToString().PadLeft(3)) 项                              │" -ForegroundColor Green
Write-Host "│  警告: $($warnCount.ToString().PadLeft(3)) 项                              │" -ForegroundColor Yellow
Write-Host "│  失败: $($failCount.ToString().PadLeft(3)) 项                              │" -ForegroundColor Red
Write-Host "│  总计: $($totalChecks.ToString().PadLeft(3)) 项                              │" -ForegroundColor White
Write-Host "└──────────────────────────────────────────┘" -ForegroundColor DarkGray
Write-Host ""

# 输出失败项建议
$failures = $checkResults | Where-Object { $_.Status -eq "fail" }
$warnings = $checkResults | Where-Object { $_.Status -eq "warn" }

if ($failures.Count -gt 0) {
    Write-Host "  需要修复的问题:" -ForegroundColor Red
    foreach ($f in $failures) {
        Write-Host "   · [$($f.Category)] $($f.Item): $($f.Detail)" -ForegroundColor Red
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "  建议关注的问题:" -ForegroundColor Yellow
    foreach ($w in $warnings) {
        Write-Host "   · [$($w.Category)] $($w.Item): $($w.Detail)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 保存报告
$logDir = Join-Path $CLAUDE_DIR "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$reportLines = @(
    "# 环境健康检查报告"
    "生成时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    "健康评分：$healthScore / 100"
    ""
    "## 检查结果"
    "- 通过: $passCount 项"
    "- 警告: $warnCount 项"
    "- 失败: $failCount 项"
    ""
)

$categories = $checkResults | ForEach-Object { $_.Category } | Select-Object -Unique
foreach ($cat in $categories) {
    $reportLines += "## $cat"
    $items = $checkResults | Where-Object { $_.Category -eq $cat }
    foreach ($item in $items) {
        $icon = switch ($item.Status) { "pass" { "[OK]" }; "warn" { "[!]" }; "fail" { "[X]" } }
        $reportLines += "- $icon $($item.Item): $($item.Detail)"
    }
    $reportLines += ""
}

$reportPath = Join-Path $logDir "health-check-$(Get-Date -Format 'yyyyMMdd').md"
$reportLines -join "`n" | Out-File -FilePath $reportPath -Encoding utf8

Write-Host "  报告已保存：$reportPath" -ForegroundColor Cyan
Write-Host ""

if ($failCount -eq 0 -and $warnCount -eq 0) {
    Write-Host "  环境完全健康，无需任何操作！" -ForegroundColor Green
} elseif ($failCount -eq 0) {
    Write-Host "  环境基本健康，有少量可优化项" -ForegroundColor Green
} else {
    Write-Host "  存在 $failCount 个问题需要修复，请查看上方详情" -ForegroundColor Yellow
}
Write-Host ""
