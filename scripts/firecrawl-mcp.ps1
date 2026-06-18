# Firecrawl MCP 启动包装：从用户/系统环境变量读取 API Key，避免 mcp.json 硬编码或 ${} 不展开
$ErrorActionPreference = 'Stop'

$key = [Environment]::GetEnvironmentVariable('FIRECRAWL_API_KEY', 'Machine')
if (-not $key) {
    $key = [Environment]::GetEnvironmentVariable('FIRECRAWL_API_KEY', 'User')
}
if (-not $key) {
    Write-Error 'FIRECRAWL_API_KEY not set in User or Machine environment variables.'
    exit 1
}

$env:FIRECRAWL_API_KEY = $key
& npx -y firecrawl-mcp @args
