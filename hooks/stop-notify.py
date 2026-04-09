#!/usr/bin/env python3
"""
Stop Hook: 任务完成系统通知
Claude 完成响应时弹出系统通知（跨平台：Windows / macOS / Linux）

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: 通知失败静默处理，不影响主流程
- FIX: 输出 {} 替代 print("{}") 防止换行问题
"""
import json
import sys
import io
import subprocess
import platform

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def windows_notify(title: str, message: str):
    title   = title.replace("'", "`'")[:100]
    message = message.replace("'", "`'")[:200]
    ps_script = (
        f"Add-Type -AssemblyName System.Windows.Forms;"
        f"$n = New-Object System.Windows.Forms.NotifyIcon;"
        f"$n.Icon = [System.Drawing.SystemIcons]::Information;"
        f"$n.BalloonTipTitle = '{title}';"
        f"$n.BalloonTipText = '{message}';"
        f"$n.Visible = $true;"
        f"$n.ShowBalloonTip(4000);"
        f"Start-Sleep -Seconds 5;"
        f"$n.Dispose()"
    )
    try:
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            creationflags=0x08000000,
        )
    except Exception:
        pass


def macos_notify(title: str, message: str):
    try:
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{message[:200]}" with title "{title[:100]}"'],
            timeout=5, capture_output=True,
        )
    except Exception:
        pass


def linux_notify(title: str, message: str):
    try:
        subprocess.run(
            ["notify-send", "-t", "4000", title[:100], message[:200]],
            timeout=5, capture_output=True,
        )
    except Exception:
        pass


def send_notification(title: str, message: str):
    try:
        system = platform.system()
        if system == "Windows":
            windows_notify(title, message)
        elif system == "Darwin":
            macos_notify(title, message)
        elif system == "Linux":
            linux_notify(title, message)
    except Exception:
        pass


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            data = {}

        stop_reason = data.get("stop_reason", "")
        if stop_reason in ("end_turn", "stop_sequence", ""):
            send_notification("✅ Claude Code 完成", "任务已完成，请查看结果。")

        sys.stdout.write("{}\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception:
        try:
            sys.stdout.write("{}\n")
            sys.stdout.flush()
        except Exception:
            pass

    sys.exit(0)


if __name__ == "__main__":
    main()
