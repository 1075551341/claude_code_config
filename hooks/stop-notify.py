#!/usr/bin/env python3
"""
Stop Hook: 任务完成 Windows 桌面通知
Claude 完成响应时弹出系统通知
"""
import json
import sys
import io
import subprocess
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def windows_notify(title, message):
    """使用 PowerShell 发送 Windows Toast 通知"""
    # 截断消息避免通知过长
    message = message[:200] if len(message) > 200 else message
    # 转义单引号
    title   = title.replace("'", "`'")
    message = message.replace("'", "`'")

    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipIcon  = 'Info'
$notify.BalloonTipTitle = '{title}'
$notify.BalloonTipText  = '{message}'
$notify.Visible = $true
$notify.ShowBalloonTip(4000)
Start-Sleep -Seconds 5
$notify.Dispose()
"""
    try:
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden",
             "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
    except Exception:
        pass

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    stop_reason = data.get("stop_reason", "")

    # 仅在正常完成时通知（非超时/中断）
    if stop_reason in ("end_turn", "stop_sequence", ""):
        # 获取最后一条消息摘要（如果有）
        message = "任务已完成，请查看结果。"

        windows_notify("✅ Claude Code 完成", message)

    sys.exit(0)

if __name__ == "__main__":
    main()
