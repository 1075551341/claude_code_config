#Requires -Version 5.1
<#
.SYNOPSIS
    Python 系 MCP 启动包装：清掉残缺 PYTHONHOME/PYTHONPATH 后再 exec。

.DESCRIPTION
    Cursor/编辑器 spawn uv/uvx/serena 时，若继承到指向不完整前缀的 PYTHONHOME，
    会 Fatal「No module named encodings」。本包装在启动前移除这两项环境变量。
    uv/uvx 若调用方未传 --python，默认钉到系统 CPython 3.12（已知 encodings 完整）。
    RepoMapper 要求 >=3.13，调用方须显式传 --python 3.13。

    编辑器 mcp.json 各自维护，禁止经 sync.ps1 复制。
#>
$ErrorActionPreference = 'Stop'

Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

if ($args.Count -lt 1) {
    Write-Error 'python-mcp.ps1: missing command'
    exit 1
}

$cmd = [string]$args[0]
$rest = @()
if ($args.Count -gt 1) {
    $rest = @($args[1..($args.Count - 1)])
}

$base = [IO.Path]::GetFileNameWithoutExtension($cmd)
$py312 = 'C:\Python312\python.exe'
if ($base -match '^(uv|uvx)$' -and ($rest -notcontains '--python') -and (Test-Path -LiteralPath $py312)) {
    $rest = @('--python', $py312) + $rest
}

& $cmd @rest
exit $LASTEXITCODE
