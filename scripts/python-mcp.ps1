<#
.SYNOPSIS
    本端 Python MCP 启动包装：清除可能损坏子进程前缀的 Python 环境变量。
.DESCRIPTION
    只在当前子进程中移除 PYTHONHOME/PYTHONPATH，再调用配置传入的命令与参数。
    不选择 Python 版本，不安装依赖，不读取其他工具配置；版本由所选服务定义决定。
#>
$ErrorActionPreference = 'Stop'
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
if ($args.Count -lt 1) {
    Write-Error 'python-mcp.ps1: missing command'
    exit 1
}
$serverCommand = [string]$args[0]
$serverArguments = @()
if ($args.Count -gt 1) {
    $serverArguments = @($args[1..($args.Count - 1)])
}
& $serverCommand @serverArguments
exit $LASTEXITCODE
