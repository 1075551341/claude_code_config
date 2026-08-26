#Requires -Version 5.1
<#
.SYNOPSIS
    fetch MCP 启动包装器 (2026-07-31 修复)

.DESCRIPTION
    解决 mcp-server-fetch 在 Windows 上无法正常使用的问题：
    1. mcp-server-fetch 2026.7.10 依赖 mcp>=1.1.3，而最新 mcp 2.x 移除了
       McpError（重命名为 MCPError）导致 ImportError 崩溃 -> 钉扎 mcp==1.28.1
    2. readabilipy 检测到 node 时调用 ExtractArticle.js，但其打包的
       @mozilla/readability node_modules 不完整（缺 Readability.js），
       导致 tools/call 报错或挂起 -> 从 PATH 移除 node/volta，
       readabilipy 自动 fallback 纯 Python 模式，功能完整可用。
#>
$env:PATH = (($env:PATH -split ';') | Where-Object { $_ -and $_ -notmatch '(?i)(volta|nodejs)' }) -join ';'
& uvx --with "mcp==1.28.1" mcp-server-fetch
