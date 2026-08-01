#Requires -Version 5.1
<#
.SYNOPSIS
    Playwright MCP 启动包装器（2026-07-31 Qoder 兼容修复）

.DESCRIPTION
    Qoder 的 Go MCP 客户端直接 fork/exec Volta shim (npx.exe) 会失败或 30s 超时。
    通过 powershell.exe 间接启动 npx 可绕过该问题（crawl/firecrawl 已验证此链路）。
    --headless --browser chromium: 减少初始化时间并避免拉起浏览器窗口。
#>
$ErrorActionPreference = 'Stop'
# r3(2026-07-31): npx（无论 @latest 还是固定版本）在 Qoder 环境 30s 超时；改用 node 绝对路径直启包入口，完全绕开 npx
# PLAYWRIGHT_BROWSERS_PATH: 显式指向已安装浏览器目录（Qoder 环境可能缺失该变量，缺失会导致 playwright 尝试下载浏览器而挂起）
$env:PLAYWRIGHT_BROWSERS_PATH = 'D:\config_sys\dev-cache\playwright'
$node = 'D:\config_sys\dev-cache\volta\tools\image\node\20.20.2\node.exe'
& $node 'D:\config_sys\dev-cache\mcp-pkgs\node_modules\@playwright\mcp\cli.js' --headless --browser chromium @args
