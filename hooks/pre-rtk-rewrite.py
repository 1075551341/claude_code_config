#!/usr/bin/env python3
"""RTK PreToolUse hook — delegates to `rtk hook claude` for bash rewrite."""
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


def main() -> int:
    stdin_data = sys.stdin.read()
    rtk = rtk_path()
    if not rtk:
        passthrough()
        return 0

    try:
        result = subprocess.run(
            [rtk, "hook", "claude"],
            input=stdin_data,
            capture_output=True,
            text=True,
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
