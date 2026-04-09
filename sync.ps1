---
description: 多编辑器配置同步脚本 | 智能识别环境
---

# Claude 配置跨编辑器同步脚本

param(
    [string] = \ C:\Users\DELL\\.claude\,
    [string[]] = @('cursor', 'windsurf', 'trae'),
    [switch],
    [switch]
)

Continue = 'Stop'

# 编辑器配置路径映射
 = @{
    'cursor'    = @{ rules = \C:\Users\DELL\\.cursorrules\; dir = \C:\Users\DELL\\.cursor\ }
    'windsurf'  = @{ rules = \C:\Users\DELL\\.windsurfrules\; dir = \C:\Users\DELL\\.windsurf\ }
    'trae'      = @{ rules = \C:\Users\DELL\\.trae\\.traeignore\; dir = \C:\Users\DELL\\.trae\ }
    'qoder'     = @{ rules = \C:\Users\DELL\\.qoder\\rules\; dir = \C:\Users\DELL\\.qoder\ }
}

# 同步项配置（相对于 ~/.claude）
 = @{
    # 完全同步 - 复制到编辑器目录
    FullSync = @(
        'CLAUDE.md'
        'rules/'
        'agents/'
        'skills/'
    )
    
    # 部分同步 - 合并到规则文件
    MergeSync = @(
        # CLAUDE.md 合并到各编辑器的 rules 文件
    )
    
    # 不同步 - Claude Code 专用
    Skip = @(
        'hooks/'
        '.mcp.json'
        '.claude.json'
        'sync.ps1'
        'SYNC_GUIDE.md'
        'experiences/'
        '.git/'
        'plugins/'
        '*.log'
    )
}

function Write-ColorOutput {
    param([string], [string] = 'White')
    Write-Host  -ForegroundColor 
}

function Test-ShouldSync {
    param([string])
    
    # 检查是否在 Skip 列表
    foreach ( in .Skip) {
        if ( -like ) { return False }
        if ( -like \*\) { return False }
    }
    
    # 检查是否在 FullSync 列表
    foreach ( in .FullSync) {
        if ( -eq ) { return True }
        if ( -like \*\) { return True }
    }
    
    return False
}

function Merge-ToRules {
    param(
        [string],
        [string],
        [string]
    )
    
     = @()
    
    # 1. 添加 CLAUDE.md 核心内容
    if (Test-Path ) {
         += Get-Content  -Raw
         += \

---

\
    }
    
    # 2. 合并 rules/ 目录下的所有 .md 文件
    if (Test-Path ) {
         = Get-ChildItem  -Filter '*.md' | Sort-Object Name
        foreach ( in ) {
             += \## From 

\
             += Get-Content .FullName -Raw
             += \

---

\
        }
    }
    
    # 3. 合并 agents/ 的关键定义
     = Join-Path (Split-Path ) 'agents'
    if (Test-Path ) {
         += \## Available Agents

\
         = Get-ChildItem  -Filter '*.md' | Where-Object { .Name -ne 'README.md' }
        foreach ( in  | Select-Object -First 20) {
             = Get-Content .FullName -TotalCount 20
             = ( | Select-String '^description:' | Select-Object -First 1) -replace '^description:\\s*', ''
            if () {
                 += \- ****: 
\
            }
        }
    }
    
    # 写入输出
    if (-not ) {
         -join '' | Out-File  -Encoding UTF8
    }
    
    Write-ColorOutput \ 合并规则 \ 'Green'
}

function Sync-ToEditor {
    param([string])
    
     = []
    if (-not ) {
        Write-ColorOutput \未知编辑器: \ 'Red'
        return
    }
    
    Write-ColorOutput \
[同步到 ]\ 'Cyan'
    
    # 确保目录存在
    if (-not (Test-Path .dir)) {
        if (-not ) {
            New-Item -ItemType Directory -Path .dir -Force | Out-Null
        }
        Write-ColorOutput \ 创建目录: \ 'Yellow'
    }
    
    # 备份现有配置
    if ( -and (Test-Path .rules)) {
         = \.bak_20260409_093723\
        if (-not ) {
            Copy-Item .rules  -Force
        }
        Write-ColorOutput \ 备份: \ 'Yellow'
    }
    
    # 合并生成规则文件
    Merge-ToRules \
        -ClaudeMdPath (Join-Path  'CLAUDE.md') \
        -RulesDir (Join-Path  'rules') \
        -OutputPath .rules
    
    # 同步完整目录
    foreach ( in .FullSync) {
         = Join-Path  
        if (-not (Test-Path )) { continue }
        
         = Join-Path .dir 
        
        if (Test-Path  -PathType Container) {
            # 目录同步
            if (-not ) {
                if (Test-Path ) {
                    Remove-Item  -Recurse -Force
                }
                Copy-Item   -Recurse -Force
            }
            Write-ColorOutput \ 同步目录: \ 'Green'
        } else {
            # 文件已在 Merge 中处理，跳过
            continue
        }
    }
    
    Write-ColorOutput \ 同步完成 \ 'Green'
}

# 主执行
Write-ColorOutput \=== Claude 配置同步工具 ===\ 'Cyan'
Write-ColorOutput \源目录: \ 'White'
Write-ColorOutput \目标编辑器:  \ 'White'
if () { Write-ColorOutput \[演练模式] 不会实际修改文件\ 'Yellow' }

foreach ( in ) {
    Sync-ToEditor 
}

Write-ColorOutput \
同步完成！重启编辑器生效。\ 'Green'
