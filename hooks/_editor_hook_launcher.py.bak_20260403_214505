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