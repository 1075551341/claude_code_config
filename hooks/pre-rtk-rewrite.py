#!/usr/bin/env python3
"""RTK PreToolUse hook — delegates to `rtk hook claude` for bash rewrite."""
# source: rtk-ai/rtk
import json
import os
import shutil
import subprocess
import sys


def rtk_path() -> str | None:
    candidates = [
        os.path.join(os.environ.get("USERPROFILE", ""), ".local", "bin", "rtk.exe"),
        os.path.join(os.environ.get("HOME", ""), ".local", "bin", "rtk"),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return shutil.which("rtk")


def passthrough() -> None:
    print(json.dumps({"continue": True, "note": "rtk not installed, passthrough"}))


_PROTOCOL_BY_PLATFORM = {
    # rtk hook 子命令：claude | cursor | gemini | copilot | droid。
    # Codex 的 hook 契约（permission/user_message/agent_message/updated_input）与 Cursor 一致。
    "codex": "cursor",
    "cursor": "cursor",
    "trae": "cursor",
    "opencode": "cursor",
}


def hook_protocol(stdin_data: str) -> str:
    """按载荷 platform 选择 rtk 输出协议；未知平台保持 claude。"""
    try:
        parsed = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError):
        return "claude"
    if not isinstance(parsed, dict):
        return "claude"
    platform = str(parsed.get("platform") or "").strip().lower()
    return _PROTOCOL_BY_PLATFORM.get(platform, "claude")


def main() -> int:
    stdin_data = sys.stdin.read()
    rtk = rtk_path()
    if not rtk:
        passthrough()
        return 0

    try:
        result = subprocess.run(
            [rtk, "hook", hook_protocol(stdin_data)],
            input=stdin_data,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        passthrough()
        return 0

    output = (result.stdout or "").strip()
    if output:
        print(output)
        return 0 if result.returncode in (0, None) else result.returncode

    passthrough()
    return 0


if __name__ == "__main__":
    sys.exit(main())
