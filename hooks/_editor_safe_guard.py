# -*- coding: utf-8 -*-
"""
_editor_safe_guard.py v3.0
跨编辑器安全守护 - 防止 hooks 在 IDE 中干扰模型正常调用

设计原则：
1. 检测优先级：环境变量 > 进程检测 > 父进程链 > CWD 检测
2. 零依赖：不依赖 psutil 等第三方库
3. 快速退出：检测到编辑器环境立即返回，不执行实际 hook 逻辑

支持的编辑器：
- VS Code / Cursor / Windsurf / Trae / Qoder / Zed / OpenCode / Codex CLI / Copilot CLI
"""
from __future__ import annotations
import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# 编辑器检测模式
# ─────────────────────────────────────────────────────────────────────────────

# 编辑器路径特征（用于 CWD 和路径检测）
_EDITOR_PATH_PATTERNS = (
    ".cursor/", "/.cursor", "cursor/projects", "roaming/cursor",
    ".windsurf", "/.windsurf", "/.trae/", "/qoder/", ".vscode/",
    ".codex/", "/.opencode/", ".zed/", ".cursor/rules",
    ".windsurf/rules", ".trae/rules", ".cc-switch/",
    "agent-transcripts", "workspacestorage", "cursor_version",
    "claude/global",  # Claude Code 全局目录（避免自我干扰）
)

# 编辑器可执行文件名
_EDITOR_EXE_PATTERNS = (
    "cursor", "windsurf", "trae", "qoder", "code.exe",
    "zed", "codex", "opencode", "github-copilot",
)

# VS Code / Electron 环境标记
_VSCODE_ENV_MARKERS = (
    "VSCODE_PID", "VSCODE_IPC_HOOK", "VSCODE_NLS_CONFIG",
    "VSCODE_CWD", "VSCODE_CODE_CACHE_PATH", "ELECTRON_RUN_AS_NODE",
    "VSCODE_HANDLES_UNCAUGHT_ERRORS", "VSCODE_ESM_ENTRYPOINT",
    "CURSOR_CHANNEL", "CURSOR_APP_VERSION", "WINDSURF_APP_VERSION",
    "TRAe_APP_VERSION", "QODER_VERSION",
)

# 强制启用 hooks 的环境（CI/终端）
_FORCE_HOOKS_ENV = ("cli", "terminal", "tui", "headless", "ci", "batch")

# 强制跳过 hooks 的环境（编辑器明确标记）
_SKIP_HOOKS_ENV = ("editor", "ide", "vscode", "cursor")


# ─────────────────────────────────────────────────────────────────────────────
# 核心检测函数
# ─────────────────────────────────────────────────────────────────────────────

def _has_vscode_env() -> bool:
    """检测 VS Code / Electron 环境标记"""
    return any(os.environ.get(marker) for marker in _VSCODE_ENV_MARKERS)


def _is_editor_cwd() -> bool:
    """检测当前工作目录是否包含编辑器路径特征"""
    try:
        cwd = os.getcwd().replace("\\", "/").lower()
        return any(pattern in cwd for pattern in _EDITOR_PATH_PATTERNS)
    except Exception:
        return False


def _check_env_override() -> tuple[bool, bool]:
    """
    检查环境变量覆盖设置
    返回: (强制启用, 强制跳过)
    """
    # 强制启用 hooks
    force_val = (os.environ.get("CLAUDE_HOOK_FORCE_CLI") or "").strip().lower()
    if force_val in ("1", "true", "yes", "on"):
        return True, False

    # 强制跳过 hooks（编辑器明确标记）
    skip_val = (os.environ.get("CLAUDE_HOOK_SKIP") or "").strip().lower()
    if skip_val in ("1", "true", "yes", "on", "editor", "ide"):
        return False, True

    # Claude Code 入口点检测
    entrypoint = (os.environ.get("CLAUDE_CODE_ENTRYPOINT") or "").strip().lower()
    if entrypoint in _FORCE_HOOKS_ENV:
        return True, False
    if entrypoint in ("editor", "ide"):
        return False, True

    return False, False


def _win_has_no_console() -> bool:
    """
    Windows: 检测是否有控制台窗口
    编辑器扩展宿主没有控制台 -> 返回 True（应跳过 hooks）
    真实终端有控制台 -> 返回 False（应执行 hooks）
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleWindow() == 0
    except Exception:
        return False


def _unix_has_no_tty() -> bool:
    """
    Unix/Linux/macOS: 检测 stdin 是否连接到 TTY
    """
    if sys.platform == "win32":
        return False
    try:
        return not os.isatty(0)  # stdin not connected to terminal
    except Exception:
        return False


def _win_parent_chain_check(max_depth: int = 15) -> bool:
    """
    Windows: 遍历父进程链检测编辑器进程
    使用 Windows API 无需 psutil
    """
    if sys.platform != "win32":
        return False

    try:
        import ctypes
        from ctypes import wintypes

        TH32CS_SNAPPROCESS = 0x00000002

        # 32/64 位兼容
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            ptr_type = ctypes.c_uint64
        else:
            ptr_type = ctypes.c_uint32

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = (
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ptr_type),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_wchar * 260),
            )

        k32 = ctypes.windll.kernel32
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == ctypes.c_void_p(-1).value or snap == 0:
            return False

        try:
            pe = PROCESSENTRY32W()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)

            if not k32.Process32FirstW(snap, ctypes.byref(pe)):
                return False

            # 构建 PID -> (PPID, exe_name) 映射
            proc_map = {}
            while True:
                proc_map[pe.th32ProcessID] = (
                    pe.th32ParentProcessID,
                    (pe.szExeFile or "").lower()
                )
                if not k32.Process32NextW(snap, ctypes.byref(pe)):
                    break

            # 遍历父进程链
            pid = os.getppid()
            seen = set()

            for _ in range(max_depth):
                if pid <= 4 or pid in seen:  # 4 = System process on Windows
                    break
                seen.add(pid)

                row = proc_map.get(pid)
                if not row:
                    break

                ppid, exe_name = row
                if any(pat in exe_name for pat in _EDITOR_EXE_PATTERNS):
                    return True

                pid = ppid

        finally:
            k32.CloseHandle(snap)

    except Exception:
        pass

    return False


def _scan_payload_for_editor(raw_payload: bytes) -> bool:
    """
    扫描 stdin payload 中的路径特征
    """
    if not raw_payload:
        return False

    try:
        import json
        payload = json.loads(raw_payload.decode("utf-8", errors="replace"))

        def _scan_obj(obj, depth: int = 0) -> bool:
            if depth > 10:
                return False
            if isinstance(obj, str):
                s = obj.replace("\\", "/").lower()
                return any(pat in s for pat in _EDITOR_PATH_PATTERNS)
            if isinstance(obj, dict):
                return any(_scan_obj(v, depth + 1) for v in obj.values())
            if isinstance(obj, list):
                return any(_scan_obj(v, depth + 1) for v in obj)
            return False

        if _scan_obj(payload):
            return True

        # 检查特定字段
        for key in ("transcript_path", "cwd", "workspace_path", "project_path"):
            val = payload.get(key) if isinstance(payload, dict) else None
            if isinstance(val, str):
                s = val.replace("\\", "/").lower()
                if any(pat in s for pat in (".cursor/", ".windsurf/", "/.trae/")):
                    return True

    except Exception:
        pass

    return False


# ─────────────────────────────────────────────────────────────────────────────
# 主检测函数
# ─────────────────────────────────────────────────────────────────────────────

def should_skip_hooks(raw_payload: bytes = b"") -> bool:
    """
    主入口：检测是否应跳过 hooks 执行

    返回 True 表示在编辑器环境中，应跳过 hooks
    返回 False 表示在 CLI 环境中，应正常执行 hooks
    """

    # [1] 环境变量覆盖（最高优先级）
    force_enable, force_skip = _check_env_override()
    if force_enable:
        return False
    if force_skip:
        return True

    # [2] Windows 控制台检测（最快路径）
    if sys.platform == "win32" and _win_has_no_console():
        return True

    # [3] Unix TTY 检测
    if sys.platform != "win32" and _unix_has_no_tty():
        # 进一步检查是否是 Electron 环境
        if _has_vscode_env():
            return True

    # [4] VS Code / Electron 环境标记
    if _has_vscode_env():
        return True

    # [5] 编辑器 CWD 检测
    if _is_editor_cwd():
        return True

    # [6] Windows 父进程链检测
    if sys.platform == "win32" and _win_parent_chain_check():
        return True

    # [7] Payload 路径扫描
    if raw_payload and _scan_payload_for_editor(raw_payload):
        return True

    # 默认：执行 hooks
    return False


def get_skip_response() -> str:
    """获取跳过 hooks 时的标准响应"""
    import json
    return json.dumps({"continue": True, "skipped": True})


# ─────────────────────────────────────────────────────────────────────────────
# CLI 测试入口
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # 读取 stdin（如果有）
    raw = b""
    try:
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.read()
        else:
            raw = sys.stdin.read().encode("utf-8")
    except Exception:
        pass

    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=" * 60)
        print("编辑器安全守护检测测试")
        print("=" * 60)
        print(f"\n环境变量:")
        print(f"  CLAUDE_HOOK_FORCE_CLI = {os.environ.get('CLAUDE_HOOK_FORCE_CLI', '未设置')}")
        print(f"  CLAUDE_HOOK_SKIP = {os.environ.get('CLAUDE_HOOK_SKIP', '未设置')}")
        print(f"  CLAUDE_CODE_ENTRYPOINT = {os.environ.get('CLAUDE_CODE_ENTRYPOINT', '未设置')}")
        print(f"\nVS Code 标记:")
        for marker in _VSCODE_ENV_MARKERS[:5]:
            val = os.environ.get(marker)
            if val:
                print(f"  {marker} = {val[:50]}...")
        print(f"\n检测结果:")
        print(f"  Windows 无控制台: {_win_has_no_console()}")
        print(f"  Unix 无 TTY: {_unix_has_no_tty()}")
        print(f"  VS Code 环境: {_has_vscode_env()}")
        print(f"  编辑器 CWD: {_is_editor_cwd()}")
        print(f"  应跳过 hooks: {should_skip_hooks(raw)}")
        print("=" * 60)
        sys.exit(0)

    # 标准模式：输出检测结果
    result = {
        "should_skip": should_skip_hooks(raw),
        "cwd": os.getcwd(),
        "platform": sys.platform,
    }
    print(json.dumps(result, ensure_ascii=False))
