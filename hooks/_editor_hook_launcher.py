# -*- coding: utf-8 -*-
"""
_editor_hook_launcher.py v3.0
跨编辑器安全的 Hook 启动器 - 防止 hooks 在 IDE 中干扰模型正常调用

设计原则：
1. 优先检测环境变量，快速退出
2. 使用原生 API 检测控制台/TTY，无需第三方依赖
3. 支持所有主流编辑器：VS Code / Cursor / Windsurf / Trae / Qoder / Zed / Codex / Copilot CLI

检测优先级：
  1. 环境变量强制覆盖
  2. Windows 控制台检测（最快）
  3. Unix TTY 检测
  4. VS Code / Electron 环境标记
  5. 编辑器 CWD 检测
  6. 父进程链检测

使用方式：
  python _editor_hook_launcher.py <real_hook.py> [args...]

编辑器环境：输出 {"continue": true, "skipped": true} 并退出
CLI 环境：执行真实 hook 脚本
"""
from __future__ import annotations
import json
import os
import subprocess
import sys

# ─────────────────────────────────────────────────────────────────────────────
# 编辑器检测配置
# ─────────────────────────────────────────────────────────────────────────────

_EDITOR_PATH_PATTERNS = (
    ".cursor/", "/.cursor", "cursor/projects", "roaming/cursor",
    ".windsurf", "/.windsurf/", "/.trae/", "/qoder/", ".vscode/",
    ".codex/", "/.opencode/", ".zed/",
    ".cursor/rules", ".windsurf/rules", ".trae/rules",
    "agent-transcripts", "workspacestorage", "cursor_version",
)

_EDITOR_EXE_PATTERNS = (
    "cursor", "windsurf", "trae", "qoder", "code.exe", "zed",
    "codex", "opencode", "github-copilot",
)

_VSCODE_ENV_MARKERS = (
    "VSCODE_PID", "VSCODE_IPC_HOOK", "VSCODE_NLS_CONFIG", "VSCODE_CWD",
    "VSCODE_CODE_CACHE_PATH", "ELECTRON_RUN_AS_NODE",
    "VSCODE_HANDLES_UNCAUGHT_ERRORS", "VSCODE_ESM_ENTRYPOINT",
    "CURSOR_CHANNEL", "CURSOR_APP_VERSION", "WINDSURF_APP_VERSION",
    "TRAe_APP_VERSION", "QODER_VERSION",
)

_FORCE_HOOKS_ENV = ("cli", "terminal", "tui", "headless", "ci", "batch")


# ─────────────────────────────────────────────────────────────────────────────
# 编辑器检测函数
# ─────────────────────────────────────────────────────────────────────────────

def _check_env_override():
    """检查环境变量覆盖设置。返回 (force_enable, force_skip)"""
    force_val = (os.environ.get("CLAUDE_HOOK_FORCE_CLI") or "").strip().lower()
    if force_val in ("1", "true", "yes", "on"):
        return True, False

    skip_val = (os.environ.get("CLAUDE_HOOK_SKIP") or "").strip().lower()
    if skip_val in ("1", "true", "yes", "on"):
        return False, True

    entrypoint = (os.environ.get("CLAUDE_CODE_ENTRYPOINT") or "").strip().lower()
    if entrypoint in _FORCE_HOOKS_ENV:
        return True, False

    return False, False


def _has_vscode_env():
    """检测 VS Code / Electron 环境标记"""
    return any(os.environ.get(marker) for marker in _VSCODE_ENV_MARKERS)


def _win_has_no_console():
    """Windows: 检测是否有控制台窗口"""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleWindow() == 0
    except Exception:
        return False


def _unix_has_no_tty():
    """Unix/Linux/macOS: 检测 stdin 是否连接到 TTY"""
    if sys.platform == "win32":
        return False
    try:
        return not os.isatty(0)
    except Exception:
        return False


def _is_editor_cwd():
    """检测当前工作目录是否包含编辑器路径特征"""
    try:
        cwd = os.getcwd().replace("\\", "/").lower()
        return any(p in cwd for p in _EDITOR_PATH_PATTERNS)
    except Exception:
        return False


def should_skip_editor(raw=b""):
    """
    主检测函数：判断是否在编辑器环境中，应跳过 hooks

    返回 True 表示在编辑器环境中，应跳过 hooks
    返回 False 表示在 CLI 环境中，应正常执行 hooks
    """
    # 环境变量覆盖（最高优先级）
    force_enable, force_skip = _check_env_override()
    if force_enable:
        return False
    if force_skip:
        return True

    # Windows 控制台检测（最快路径）
    if sys.platform == "win32" and _win_has_no_console():
        return True

    # Unix TTY 检测 + VS Code 环境
    if sys.platform != "win32" and _unix_has_no_tty():
        if _has_vscode_env():
            return True

    # VS Code / Electron 环境标记
    if _has_vscode_env():
        return True

    # 编辑器 CWD 检测
    if _is_editor_cwd():
        return True

    # 默认：执行 hooks（CLI 环境）
    return False


def get_skip_response():
    """获取跳过 hooks 时的标准响应"""
    return json.dumps({"continue": True, "skipped": True, "reason": "editor_context"})


def main():
    """主入口：安全地执行 hook 或跳过"""
    if len(sys.argv) < 2:
        print("usage: python _editor_hook_launcher.py <hook.py> [args...]", file=sys.stderr)
        sys.exit(2)

    target = os.path.abspath(sys.argv[1])
    if not os.path.isfile(target):
        print(f"launcher: not found: {target}", file=sys.stderr)
        sys.exit(2)

    # 读取 stdin
    raw = b""
    try:
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.read()
        else:
            raw = sys.stdin.read().encode("utf-8")
    except Exception:
        pass

    # 编辑器环境：立即跳过
    if should_skip_editor(raw):
        sys.stdout.write(get_skip_response() + "\n")
        sys.stdout.flush()
        sys.exit(0)

    # CLI 环境：执行真实 hook
    proc = subprocess.run(
        [sys.executable, target] + sys.argv[2:],
        input=raw if raw else None
    )
    sys.exit(proc.returncode if proc.returncode is not None else 1)


if __name__ == "__main__":
    main()
