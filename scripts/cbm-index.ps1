# @描述 为指定目录建立 codebase-memory-mcp 索引（Windows JSON 转义友好）
# @状态 codebase-memory 自 v10.10 起永久禁用（全盘索引爆 CPU/内存，见 R17 / validate_config V18）。
#       本脚本仅为手工排查场景保留，日常代码探索一律用 codegraph_explore，勿再建 cbm 索引。
# @用法 .\scripts\cbm-index.ps1 [repo_path]
# @示例 .\scripts\cbm-index.ps1                    # 默认 ~/.claude（不推荐，用户主目录量级会撑爆内存）
# @示例 .\scripts\cbm-index.ps1 D:\apdms           # 业务项目

param(
    [string]$RepoPath = (Join-Path $env:USERPROFILE ".claude")
)

$ErrorActionPreference = "Stop"
$RepoPath = (Resolve-Path $RepoPath).Path
$jsonPath = Join-Path $env:TEMP "cbm-index-$(Get-Random).json"
@{ repo_path = $RepoPath } | ConvertTo-Json -Compress | Set-Content -Path $jsonPath -Encoding UTF8

try {
    Write-Host "Indexing: $RepoPath" -ForegroundColor Cyan
    $payload = Get-Content -Raw $jsonPath
    npx -y codebase-memory-mcp@0.8.1 cli index_repository $payload
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Done. Project slug uses path-derived name; run list_projects to confirm." -ForegroundColor Green
}
finally {
    Remove-Item -Force $jsonPath -ErrorAction SilentlyContinue
}
