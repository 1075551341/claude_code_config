#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code 编辑器 Hook 修复脚本 v5.0

.DESCRIPTION
    部署 _editor_hook_launcher.py v2.0，以 GetConsoleWindow() 为主要判定依据；
    确保 ~/.claude/settings.json 中各 Hook 命令经 launcher 调用；
    并向各编辑器 settings.json 写入 env.CLAUDE_IN_EDITOR（与 launcher 互为补充）。

    === 以往防护为何不可靠 ===

    旧方案依赖的信号，在 Cursor 扩展宿主拉起的 Python 子进程里往往无法稳定继承：

    [X] settings.json 的 env.CLAUDE_IN_EDITOR
        → VS Code 的 env 主要作用于集成终端，未必传到扩展宿主 → claude.exe → python.exe

    [X] VSCODE_PID / VSCODE_CWD / CURSOR_CHANNEL 等
        → 多挂在 Electron 主进程，经扩展宿主链路传递不可靠

    [X] CreateToolhelp32Snapshot 父进程链遍历
        → 异常被吞或超时，可能误判为「不跳过」导致 Hook 仍全量执行

    [X] 依赖 stdin JSON 路径判断
        → Stop 类 Hook 无 stdin，stop-notify 等仍会跑满逻辑，日志里可达 2000ms+

    === 当前方案：GetConsoleWindow() ===

    获取当前进程所附加控制台的窗口句柄。控制台附着会随 CreateProcess 继承（非 exec 替换）。

    CLI：真实终端拥有控制台 → 子进程 python 继承控制台 → GetConsoleWindow()!=0 → 执行完整 Hook。

    编辑器：cursor.exe（无控制台）→ 扩展宿主 / claude 子进程均无控制台 →
            python Hook 子进程 GetConsoleWindow()==0 → 快速跳过。

    特点：单次 Win32 调用（约 <0.1ms）；不依赖环境变量继承；Pre/Post/Stop 行为一致。
    例外：无头/CI 也无控制台 → 需先判断 CLAUDE_CODE_ENTRYPOINT=headless|ci|batch 再决定是否跳过。

    === 预期效果 ===
    修复前：Cursor Hooks 日志常见 2000–6700ms（完整跑 Hook）
    修复后：约 30–60ms（launcher 识别编辑器上下文后立即退出）

.PARAMETER Fix
    应用全部修复项

.PARAMETER Restore
    从 settings.json 中移除 launcher，Hook 命令恢复为直接 python xxx.py

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File fix.ps1
    powershell -ExecutionPolicy Bypass -File fix.ps1 -Fix
    powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore
#>

param(
    [switch]$Fix,
    [switch]$Restore
)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

$CLAUDE_DIR   = Join-Path $env:USERPROFILE ".claude"
$HOOKS_DIR    = Join-Path $CLAUDE_DIR "hooks"
$SETTINGS     = Join-Path $CLAUDE_DIR "settings.json"
$ALL_EDITORS  = @("cursor", "trae", "windsurf", "qoder")
$LAUNCHER_NAME = "_editor_hook_launcher.py"
$LAUNCHER_PATH = Join-Path $HOOKS_DIR $LAUNCHER_NAME

# _editor_hook_launcher.py v2.0 内嵌源码（主判定：GetConsoleWindow，见上方说明）
$LAUNCHER_CONTENT = @'
# -*- coding: utf-8 -*-
"""
_editor_hook_launcher.py v2.0
Fast no-op in editor/IDE context; delegates to real hook in CLI.

PRIMARY detection: GetConsoleWindow() Windows API.
  Real terminal: console attached (hwnd!=0) -> run hooks.
  Editor extension host: no console (hwnd==0) -> skip immediately.
  O(1), no deps, works for Pre/Post/Stop hooks equally.
"""
from __future__ import annotations
import json, os, subprocess, sys

_EDITOR_PATH_NEEDLES = (
    ".cursor/", "/.cursor", "cursor/projects", "roaming/cursor",
    ".windsurf", "/.trae/", "/qoder/", ".vscode/",
    "agent-transcripts", "workspacestorage", "cursor_version", "cursor\\projects",
)
_EDITOR_EXE_NEEDLES = ("cursor", "windsurf", "trae", "qoder", "code.exe")


def _eg_scan(obj, depth=0):
    if depth > 14: return False
    if isinstance(obj, str):
        s = obj.replace("\\", "/").lower()
        return any(n in s for n in _EDITOR_PATH_NEEDLES)
    if isinstance(obj, dict): return any(_eg_scan(v, depth+1) for v in obj.values())
    if isinstance(obj, list): return any(_eg_scan(v, depth+1) for v in obj)
    return False


def _env_forces_full_hooks():
    v = (os.environ.get("CLAUDE_HOOK_FORCE_CLI") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _win_has_no_console():
    """Single Win32 call. Returns True when no console attached (editor context)."""
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleWindow() == 0
    except Exception:
        return False


def _win_editor_in_parent_chain():
    """Fallback parent process walk via CreateToolhelp32Snapshot."""
    try:
        import ctypes
        from ctypes import wintypes
        TH32CS_SNAPPROCESS = 0x2
        ptr_type = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p)==8 else ctypes.c_uint32
        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = (
                ("dwSize",wintypes.DWORD),("cntUsage",wintypes.DWORD),
                ("th32ProcessID",wintypes.DWORD),("th32DefaultHeapID",ptr_type),
                ("th32ModuleID",wintypes.DWORD),("cntThreads",wintypes.DWORD),
                ("th32ParentProcessID",wintypes.DWORD),("pcPriClassBase",wintypes.LONG),
                ("dwFlags",wintypes.DWORD),("szExeFile",ctypes.c_wchar*260),
            )
        k32 = ctypes.windll.kernel32
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == ctypes.c_void_p(-1).value or snap == 0: return False
        by_pid = {}
        try:
            pe = PROCESSENTRY32W(); pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            if not k32.Process32FirstW(snap, ctypes.byref(pe)): return False
            while True:
                by_pid[pe.th32ProcessID] = (pe.th32ParentProcessID, (pe.szExeFile or "").lower())
                if not k32.Process32NextW(snap, ctypes.byref(pe)): break
        finally:
            k32.CloseHandle(snap)
        pid = os.getppid(); seen = set()
        for _ in range(20):
            if pid <= 4 or pid in seen: break
            seen.add(pid)
            row = by_pid.get(pid)
            if not row: break
            ppid, exe = row
            if any(x in exe for x in _EDITOR_EXE_NEEDLES): return True
            pid = ppid
    except Exception:
        pass
    return False


def should_skip_editor(raw):
    # [0] Hard override: always run hooks
    if _env_forces_full_hooks(): return False

    # [1] Headless/CI: no console but needs hooks - check BEFORE console check
    cep = (os.environ.get("CLAUDE_CODE_ENTRYPOINT") or "").strip().lower()
    if cep in ("headless", "ci", "batch"): return False

    # [2] PRIMARY: GetConsoleWindow - fastest, most reliable, works for ALL hook types
    #    Editor extension host has no console -> hook subprocesses have no console
    #    Real terminal sessions always have console attached
    if sys.platform == "win32" and _win_has_no_console():
        return True

    # [3] Sentinel env var
    if os.environ.get("CLAUDE_IN_EDITOR"): return True

    # [4] CWD contains editor path
    try:
        cwd = os.getcwd().replace("\\", "/").lower()
        if any(n in cwd for n in _EDITOR_PATH_NEEDLES): return True
    except Exception:
        pass

    # [5] VS Code / Cursor family env markers
    for _k in ("VSCODE_PID","VSCODE_IPC_HOOK","VSCODE_NLS_CONFIG","VSCODE_CWD",
               "VSCODE_CODE_CACHE_PATH","CURSOR_CHANNEL","ELECTRON_RUN_AS_NODE",
               "VSCODE_HANDLES_UNCAUGHT_ERRORS","VSCODE_ESM_ENTRYPOINT",
               "CURSOR_APP_VERSION","WINDSURF_APP_VERSION"):
        if os.environ.get(_k): return True

    # [6] Windows parent process chain (fallback)
    if sys.platform == "win32" and _win_editor_in_parent_chain(): return True

    # [7] stdin payload path check
    if raw:
        try:
            p = json.loads(raw.decode("utf-8", errors="replace"))
            if isinstance(p, dict):
                if _eg_scan(p): return True
                for _k2 in ("transcript_path","cwd","workspace_path","project_path"):
                    _v = p.get(_k2)
                    if isinstance(_v, str):
                        _s = _v.replace("\\", "/").lower()
                        if any(_m in _s for _m in (".cursor/",".windsurf/","/.trae/")):
                            return True
        except Exception:
            pass

    # [8] Explicit CLI whitelist
    if cep in ("cli", "terminal", "tui"): return False

    return False


def main():
    if len(sys.argv) < 2:
        print("usage: python _editor_hook_launcher.py <hook.py> [args...]", file=sys.stderr)
        sys.exit(2)
    target = os.path.abspath(sys.argv[1])
    if not os.path.isfile(target):
        print("launcher: not found: " + target, file=sys.stderr)
        sys.exit(2)
    raw = b""
    try:
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
    except Exception:
        pass
    if should_skip_editor(raw):
        try:
            sys.stdout.write('{"continue":true}\n')
            sys.stdout.flush()
        except Exception:
            pass
        sys.exit(0)
    proc = subprocess.run([sys.executable, target] + sys.argv[2:], input=raw if raw else None)
    sys.exit(proc.returncode if proc.returncode is not None else 1)


if __name__ == "__main__":
    main()
'@

function Write-Ok   { param($m) Write-Host "  [OK]  $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  [!!]  $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "  [XX]  $m" -ForegroundColor Red }
function Write-Fix  { param($m) Write-Host "  [FIX] $m" -ForegroundColor DarkCyan }
function Write-Info { param($m) Write-Host "  >> $m"    -ForegroundColor Cyan }

function IsLink {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $false }
    return [bool]((Get-Item $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Read-Json {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try { return Get-Content $Path -Raw -Encoding utf8 | ConvertFrom-Json } catch {}
    try { return Get-Content $Path -Raw -Encoding unicode | ConvertFrom-Json } catch {}
    return $null
}

function Write-Json {
    param([string]$Path, $Obj)
    # Depth 100：写回编辑器 settings 时保留深层 workbench/编辑器 JSON
    $json = $Obj | ConvertTo-Json -Depth 100
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.Encoding]::UTF8)
}

# header
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Claude Code 编辑器 Hook 修复脚本 v5.0" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
if ($Restore) {
    Write-Host "  [还原] 将 Hook 命令恢复为直接调用 python" -ForegroundColor Yellow
} elseif (-not $Fix) {
    Write-Host "  [诊断] 只读模式。追加 -Fix 后才会写盘修改。" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================
# S1: Launcher status
# ==============================================================
Write-Info "S1: Launcher 状态"
Write-Host ""

if (-not (Test-Path $HOOKS_DIR)) {
    Write-Fail "未找到 hooks/ 目录: $HOOKS_DIR"
} else {
    if (Test-Path $LAUNCHER_PATH) {
        $lc = Get-Content $LAUNCHER_PATH -Raw -Encoding utf8 -EA SilentlyContinue
        if ($lc -match "GetConsoleWindow") {
            Write-Ok "Launcher v2.0 已就绪（含 GetConsoleWindow 检测）"
        } elseif ($lc -match "_editor_hook_launcher") {
            Write-Warn "Launcher 存在但为旧版（缺少 GetConsoleWindow），需执行 -Fix 更新"
        } else {
            Write-Warn "Launcher 文件存在但内容异常"
        }
    } else {
        Write-Warn "未找到 Launcher，执行 -Fix 时将创建"
    }
}
Write-Host ""

# ==============================================================
# S2: settings.json hook command format
# ==============================================================
Write-Info "S2: settings.json 中 Hook 命令格式"
Write-Host ""

$settingsObj = Read-Json $SETTINGS
$hookCount = 0
$launcherCount = 0
$directCount = 0

if ($settingsObj -and $settingsObj.hooks) {
    $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue |
            Select-Object -ExpandProperty Name
    foreach ($cat in $cats) {
        foreach ($entry in $settingsObj.hooks.$cat) {
            foreach ($h in $entry.hooks) {
                $hookCount++
                if ([string]$h.command -match "_editor_hook_launcher") {
                    $launcherCount++
                } else {
                    $directCount++
                    Write-Warn "仍为直连格式（未经 launcher）: $(Split-Path ([string]$h.command) -Leaf)"
                }
            }
        }
    }
    Write-Host "  Hook 总数: $hookCount  |  经 launcher: $launcherCount  |  直连: $directCount" -ForegroundColor White
    if ($launcherCount -eq $hookCount -and $hookCount -gt 0) {
        Write-Ok "全部 Hook 已使用 launcher 格式"
    }
} else {
    Write-Warn "settings.json 无 hooks 段或无法解析"
}
Write-Host ""

# ==============================================================
# S3: CLAUDE_IN_EDITOR in editor settings
# ==============================================================
Write-Info "S3: 各编辑器 settings 中的 CLAUDE_IN_EDITOR"
Write-Host ""

foreach ($editor in $ALL_EDITORS) {
    $editorDir = Join-Path $env:USERPROFILE ".$editor"
    if (-not (Test-Path $editorDir)) { continue }
    $esPath = Join-Path $editorDir "settings.json"
    if (-not (Test-Path $esPath)) { Write-Warn "缺少 .$editor/settings.json"; continue }
    $es = Read-Json $esPath
    $val = if ($es -and $es.env) { $es.env.'CLAUDE_IN_EDITOR' } else { $null }
    if ($val) {
        Write-Ok ".$editor/settings.json  CLAUDE_IN_EDITOR=$val"
    } else {
        Write-Warn ".$editor/settings.json  未设置 CLAUDE_IN_EDITOR"
    }
}
Write-Host ""

# ==============================================================
# S4: Stale hooks/ symlinks
# ==============================================================
Write-Info "S4: 各编辑器目录下陈旧的 hooks/ 软链接"
Write-Host ""

foreach ($editor in $ALL_EDITORS) {
    $ep = Join-Path (Join-Path $env:USERPROFILE ".$editor") "hooks"
    if (Test-Path $ep) {
        if (IsLink $ep) {
            Write-Fail ".$editor/hooks/ 为软链接，必须删除（请用 -Fix）"
        } else {
            Write-Ok ".$editor/hooks/ 为实体目录（正常）"
        }
    } else {
        Write-Ok ".$editor/hooks/ 不存在（正常）"
    }
}
Write-Host ""

# ==============================================================
# Exit if diagnosis only
# ==============================================================
if (-not $Fix -and -not $Restore) {
    Write-Host "  执行以下命令应用全部修复:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File fix.ps1 -Fix" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# ==============================================================
# RESTORE: Revert hook commands to direct format
# ==============================================================
if ($Restore) {
    Write-Info "还原: 从 Hook 命令中移除 launcher"
    Write-Host ""

    if ($settingsObj -and $settingsObj.hooks) {
        $modified = $false
        $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue |
                Select-Object -ExpandProperty Name
        foreach ($cat in $cats) {
            foreach ($entry in $settingsObj.hooks.$cat) {
                foreach ($h in $entry.hooks) {
                    $cmd = [string]$h.command
                    if ($cmd -match "_editor_hook_launcher\.py\s+(.+\.py)") {
                        $realHook = $Matches[1].Trim()
                        $h.command = "python $realHook"
                        $modified = $true
                        Write-Fix "已恢复为: python $(Split-Path $realHook -Leaf)"
                    }
                }
            }
        }
        if ($modified) {
            $bak = $SETTINGS + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $SETTINGS $bak -Force
            Write-Json -Path $SETTINGS -Obj $settingsObj
            Write-Fix "settings.json 已还原（备份: $(Split-Path $bak -Leaf)）"
        } else {
            Write-Ok "未发现 launcher 命令，已是直连格式"
        }
    }
    Write-Host ""
    Write-Ok "还原完成。请重启各编辑器。"
    Write-Host ""
    exit 0
}

# ==============================================================
# FIX A: Deploy updated launcher v2.0 to hooks directory
# ==============================================================
Write-Info "FIX A: 部署 _editor_hook_launcher.py v2.0"
Write-Host ""

if (-not (Test-Path $HOOKS_DIR)) {
    Write-Fail "未找到 hooks/: $HOOKS_DIR"
    Write-Host "  运行 fix 前须已存在 hooks/ 目录。" -ForegroundColor Yellow
    exit 1
}

# Backup old launcher if exists
if (Test-Path $LAUNCHER_PATH) {
    $bak = $LAUNCHER_PATH + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $LAUNCHER_PATH $bak -Force
    Write-Fix "已备份旧 launcher: $(Split-Path $bak -Leaf)"
}

[System.IO.File]::WriteAllText($LAUNCHER_PATH, $LAUNCHER_CONTENT, [System.Text.Encoding]::UTF8)
Write-Fix "已部署 _editor_hook_launcher.py v2.0（主判定 GetConsoleWindow）"

# Verify it was written correctly
$verify = Get-Content $LAUNCHER_PATH -Raw -Encoding utf8 -EA SilentlyContinue
if ($verify -match "GetConsoleWindow") {
    Write-Ok "校验通过: 已写入的 launcher 含 GetConsoleWindow 检测"
} else {
    Write-Fail "校验失败: launcher 可能未正确写入"
}

# ==============================================================
# FIX B: Update settings.json hook commands to use launcher
# ==============================================================
Write-Host ""
Write-Info "FIX B: 将 settings.json 中 Hook 改为经 launcher 调用"
Write-Host ""

$settingsObj = Read-Json $SETTINGS
if ($null -eq $settingsObj) {
    Write-Fail "无法读取 settings.json: $SETTINGS"
} elseif (-not $settingsObj.hooks) {
    Write-Warn "settings.json 无 hooks 段，无需转换"
} else {
    $modified = $false
    $converted = 0

    $cats = $settingsObj.hooks | Get-Member -MemberType NoteProperty -EA SilentlyContinue |
            Select-Object -ExpandProperty Name

    foreach ($cat in $cats) {
        foreach ($entry in $settingsObj.hooks.$cat) {
            foreach ($h in $entry.hooks) {
                $cmd = [string]$h.command
                # Skip if already using launcher
                if ($cmd -match "_editor_hook_launcher") { continue }
                # Skip if not a python hook
                if ($cmd -notmatch "^python\s+(.+\.py)") { continue }

                $hookPath = $Matches[1].Trim()
                $newCmd = "python $LAUNCHER_PATH $hookPath"
                $h.command = $newCmd
                $modified = $true
                $converted++
                Write-Fix "[$cat] $(Split-Path $hookPath -Leaf)"
            }
        }
    }

    if ($modified) {
        $bak = $SETTINGS + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $SETTINGS $bak -Force
        Write-Json -Path $SETTINGS -Obj $settingsObj
        Write-Fix "settings.json 已更新（$converted 个 Hook 已改为 launcher 格式）"
    } else {
        Write-Ok "Hook 已全部使用 launcher 格式（或未找到可转换的 python Hook）"
    }
}

# ==============================================================
# FIX C: Set CLAUDE_IN_EDITOR in editor settings (belt+suspenders)
# ==============================================================
Write-Host ""
Write-Info "FIX C: 写入各编辑器 settings 中的 CLAUDE_IN_EDITOR"
Write-Host ""

foreach ($editor in $ALL_EDITORS) {
    $editorDir = Join-Path $env:USERPROFILE ".$editor"
    if (-not (Test-Path $editorDir)) { continue }
    $esPath = Join-Path $editorDir "settings.json"

    $fileExists = Test-Path $esPath
    $es = $null
    if ($fileExists) {
        $es = Read-Json $esPath
        if ($null -eq $es) {
            Write-Warn ".$editor/settings.json 解析失败，文件未修改（保留字体/主题/界面配置）。请修正 JSON 或手动设置 env.CLAUDE_IN_EDITOR。"
            continue
        }
    } else {
        $es = [PSCustomObject]@{}
    }

    if (-not $es.PSObject.Properties.Match('env').Count) {
        $es | Add-Member -MemberType NoteProperty -Name 'env' -Value ([PSCustomObject]@{})
    }

    $changed = $false
    if (-not $es.env.PSObject.Properties.Match('CLAUDE_IN_EDITOR').Count) {
        $es.env | Add-Member -MemberType NoteProperty -Name 'CLAUDE_IN_EDITOR' -Value $editor -Force
        $changed = $true
    } elseif ($es.env.CLAUDE_IN_EDITOR -ne $editor) {
        $es.env.CLAUDE_IN_EDITOR = $editor
        $changed = $true
    }

    if ($changed) {
        if ($fileExists) {
            Copy-Item $esPath ($esPath + ".bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')") -Force
        }
        Write-Json -Path $esPath -Obj $es
        Write-Fix ".$editor/settings.json  env.CLAUDE_IN_EDITOR=$editor"
    } else {
        Write-Ok ".$editor/settings.json  CLAUDE_IN_EDITOR 已正确"
    }
}

# ==============================================================
# FIX D: Remove stale hooks/ symlinks
# ==============================================================
Write-Host ""
Write-Info "FIX D: 删除各编辑器下陈旧的 hooks/ 软链接"
Write-Host ""

foreach ($editor in $ALL_EDITORS) {
    $ep = Join-Path (Join-Path $env:USERPROFILE ".$editor") "hooks"
    if ((Test-Path $ep) -and (IsLink $ep)) {
        Remove-Item $ep -Force
        Write-Fix "已删除 .$editor/hooks/ 软链接"
    }
}
Write-Ok "软链接清理完成"

# ==============================================================
# FIX E: Update editor ignore files
# ==============================================================
Write-Host ""
Write-Info "FIX E: 更新各编辑器 ignore 文件"
Write-Host ""

foreach ($editor in $ALL_EDITORS) {
    $editorDir = Join-Path $env:USERPROFILE ".$editor"
    if (-not (Test-Path $editorDir)) { continue }
    $ign = Join-Path $editorDir ".${editor}ignore"
    "# Claude Code internal dirs`nhooks/`nplugins/`nbackups/`nlogs/`nexperiences/`nplans/" |
        Out-File -FilePath $ign -Encoding utf8
    Write-Fix "已更新 .${editor}ignore"
}

# ==============================================================
# Summary
# ==============================================================
Write-Host ""
Write-Host "  =====================================================" -ForegroundColor DarkGray
Write-Host "  Fix v5.0 已完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  已应用变更:" -ForegroundColor White
Write-Host "    已部署 _editor_hook_launcher.py v2.0" -ForegroundColor DarkGray
Write-Host "      主规则: GetConsoleWindow()==0 → 编辑器内跳过 Hook" -ForegroundColor DarkGray
Write-Host "      无控制台 ≈ Cursor 扩展宿主等编辑器上下文" -ForegroundColor DarkGray
Write-Host "    ~/.claude/settings.json 中 Hook 已改为经 launcher 调用" -ForegroundColor DarkGray
Write-Host "    各编辑器 settings.json 已写入 env.CLAUDE_IN_EDITOR" -ForegroundColor DarkGray
Write-Host "    已清理陈旧的 hooks/ 软链接" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Cursor Hooks 执行日志预期:" -ForegroundColor White
Write-Host "    修复前: preToolUse 约 2000–6700ms（跑完整 Hook）" -ForegroundColor DarkGray
Write-Host "    修复后: preToolUse 约 30–60ms（launcher 识别编辑器后立即退出）" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  后续步骤:" -ForegroundColor Yellow
Write-Host "    1. 完全退出并重启 Cursor（不要仅 Reload 窗口）" -ForegroundColor White
Write-Host "    2. 设置 → Hooks → 查看执行记录耗时" -ForegroundColor White
Write-Host "    3. 各 Hook 条目应约为几十毫秒量级" -ForegroundColor White
Write-Host ""
Write-Host "  CLI 中 Hook 仍会全量执行（终端有控制台，hwnd!=0）" -ForegroundColor DarkGray
Write-Host "  若需在任意环境强制跑全量 Hook: 设置 CLAUDE_HOOK_FORCE_CLI=1" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  撤销: powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore" -ForegroundColor DarkGray
Write-Host ""
