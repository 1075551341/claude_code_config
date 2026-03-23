#Requires -Version 5.1
<#
.SYNOPSIS
    GitHub 热门开发工具搜索与推荐脚本
.DESCRIPTION
    搜索 GitHub 上热门的开发工具仓库，与本地工具库对比，
    推荐可引入的新工具。支持按分类搜索和安全评估。
.NOTES
    用法：powershell -ExecutionPolicy Bypass -File search-github-tools.ps1
    需要网络连接，可选配置 GITHUB_TOKEN 环境变量提高 API 限额
#>

param(
    [string]$Category = "all",
    [switch]$SaveReport
)

$CLAUDE_DIR = Join-Path $env:USERPROFILE ".claude"
$SKILLS_DIR = Join-Path $CLAUDE_DIR "skills"
$LOG_DIR = Join-Path $CLAUDE_DIR "logs"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   GitHub 热门开发工具搜索引擎 v1.0           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$toolCategories = @{
    "前端框架" = @(
        @{ Query = "react component library"; Tags = @("react", "ui", "components") }
        @{ Query = "vue3 component library"; Tags = @("vue", "ui", "components") }
        @{ Query = "tailwind css plugins"; Tags = @("css", "tailwind", "styling") }
    )
    "后端框架" = @(
        @{ Query = "node.js api framework"; Tags = @("nodejs", "api", "backend") }
        @{ Query = "fastapi python framework"; Tags = @("python", "api", "backend") }
        @{ Query = "express middleware"; Tags = @("nodejs", "middleware", "backend") }
    )
    "数据库工具" = @(
        @{ Query = "typescript orm database"; Tags = @("database", "orm", "typescript") }
        @{ Query = "database migration tool"; Tags = @("database", "migration") }
    )
    "测试工具" = @(
        @{ Query = "javascript testing framework 2025"; Tags = @("testing", "javascript") }
        @{ Query = "api testing tool"; Tags = @("testing", "api") }
        @{ Query = "e2e testing framework"; Tags = @("testing", "e2e") }
    )
    "DevOps" = @(
        @{ Query = "docker development tool"; Tags = @("docker", "devops") }
        @{ Query = "ci cd pipeline tool"; Tags = @("cicd", "devops") }
    )
    "开发效率" = @(
        @{ Query = "code generator cli tool"; Tags = @("cli", "generator", "productivity") }
        @{ Query = "developer productivity tool 2025"; Tags = @("productivity", "dx") }
    )
    "安全工具" = @(
        @{ Query = "security scanning tool nodejs"; Tags = @("security", "scanning") }
        @{ Query = "dependency vulnerability scanner"; Tags = @("security", "dependencies") }
    )
    "AI开发" = @(
        @{ Query = "langchain javascript"; Tags = @("ai", "llm", "langchain") }
        @{ Query = "mcp server model context protocol"; Tags = @("ai", "mcp", "tools") }
        @{ Query = "rag retrieval augmented generation"; Tags = @("ai", "rag", "vector") }
    )
}

function Search-GitHub {
    param([string]$Query, [int]$MaxResults = 5)

    $headers = @{ "Accept" = "application/vnd.github.v3+json" }
    $token = $env:GITHUB_TOKEN
    if ($token) {
        $headers["Authorization"] = "token $token"
    }

    $encodedQuery = [System.Uri]::EscapeDataString($Query)
    $url = "https://api.github.com/search/repositories?q=$encodedQuery&sort=stars&order=desc&per_page=$MaxResults"

    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 15 -ErrorAction Stop
        return $response.items
    } catch {
        Write-Host "  ⚠️  搜索失败: $($_.Exception.Message)" -ForegroundColor Yellow
        return @()
    }
}

function Get-SafetyScore {
    param($Repo)
    $score = 0
    if ($Repo.stargazers_count -ge 1000) { $score += 30 }
    elseif ($Repo.stargazers_count -ge 100) { $score += 15 }
    if ($Repo.license) { $score += 20 }
    $daysSinceUpdate = ((Get-Date) - [datetime]$Repo.updated_at).Days
    if ($daysSinceUpdate -le 90) { $score += 25 }
    elseif ($daysSinceUpdate -le 365) { $score += 10 }
    if (-not $Repo.archived) { $score += 15 }
    if ($Repo.forks_count -ge 50) { $score += 10 }
    return [math]::Min($score, 100)
}

$allResults = @()
$categoriesToSearch = if ($Category -eq "all") { $toolCategories.Keys } else { @($Category) }

foreach ($cat in $categoriesToSearch) {
    if (-not $toolCategories.ContainsKey($cat)) {
        Write-Host "⚠️  未知分类: $cat" -ForegroundColor Yellow
        continue
    }

    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🔍 $cat" -ForegroundColor Green
    Write-Host ""

    foreach ($searchItem in $toolCategories[$cat]) {
        $repos = Search-GitHub -Query $searchItem.Query -MaxResults 3
        Start-Sleep -Milliseconds 1500

        foreach ($repo in $repos) {
            $safety = Get-SafetyScore -Repo $repo
            $safetyIcon = if ($safety -ge 70) { "🟢" } elseif ($safety -ge 40) { "🟡" } else { "🔴" }
            $stars = if ($repo.stargazers_count -ge 1000) {
                "$([math]::Round($repo.stargazers_count / 1000, 1))k"
            } else { $repo.stargazers_count }

            Write-Host "   $safetyIcon $($repo.full_name)" -ForegroundColor Cyan -NoNewline
            Write-Host " ⭐$stars" -ForegroundColor Yellow -NoNewline
            Write-Host " 安全评分:$safety" -ForegroundColor DarkGray
            Write-Host "      $($repo.description)" -ForegroundColor White
            Write-Host "      $($repo.html_url)" -ForegroundColor DarkGray
            Write-Host ""

            $allResults += @{
                Category = $cat
                Name = $repo.full_name
                Stars = $repo.stargazers_count
                Safety = $safety
                URL = $repo.html_url
                Description = $repo.description
                Tags = $searchItem.Tags
            }
        }
    }
}

if ($SaveReport -or $true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd"
    $reportPath = Join-Path $LOG_DIR "github-tools-$timestamp.md"
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null

    $reportContent = @"
# GitHub 热门工具搜索报告
> 生成时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## 搜索结果统计
- 总计发现：$($allResults.Count) 个仓库
- 高安全评分（≥70）：$(($allResults | Where-Object { $_.Safety -ge 70 }).Count) 个
- 涵盖分类：$($categoriesToSearch.Count) 个

## 推荐工具（安全评分 ≥ 70）

$(($allResults | Where-Object { $_.Safety -ge 70 } | Sort-Object { $_.Stars } -Descending | ForEach-Object {
    "### $($_.Name) ⭐$($_.Stars) 安全:$($_.Safety)/100`n- 分类：$($_.Category)`n- 说明：$($_.Description)`n- 地址：$($_.URL)`n- 标签：$($_.Tags -join ', ')`n"
}) -join "`n")

## 引入建议

1. 优先引入安全评分 ≥ 70 的工具
2. 查看 README 和 Issues 确认活跃度
3. 本地测试通过后添加到 skills 技能库
4. 运行 sync-tools.ps1 同步到所有编辑器

---
> 由 search-github-tools.ps1 自动生成
"@

    $reportContent | Out-File -FilePath $reportPath -Encoding utf8
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "📄 报告已保存：$reportPath" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ 搜索完成！发现 $($allResults.Count) 个工具" -ForegroundColor Green
Write-Host "   高评分推荐：$(($allResults | Where-Object { $_.Safety -ge 70 }).Count) 个" -ForegroundColor Yellow
Write-Host ""
