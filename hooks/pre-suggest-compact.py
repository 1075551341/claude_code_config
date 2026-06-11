#!/usr/bin/env python3
"""
PreToolUse Hook: 上下文压缩建议 + Token 预算预警
基于工具调用计数 + 上下文大小估算，三级预警

阈值对照: <70%正常 / 70%择机压缩 / 90%强制压缩 → rules/CORE.md
"""
import json
import sys
import io
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"pre-suggest-compact: stdout reconfigure failed: {e}", file=sys.stderr)

# 三级阈值（可通过环境变量覆盖）
WARN_COUNT = int(os.environ.get("CLAUDE_COMPACT_WARN", 20))       # 轻度提醒
CRITICAL_COUNT = int(os.environ.get("CLAUDE_COMPACT_CRITICAL", 35))  # 强烈建议
FORCE_COUNT = int(os.environ.get("CLAUDE_COMPACT_FORCE", 50))       # 紧急警告

# 上下文窗口估算 (基于 ~200K token 窗口)
CTX_WINDOW_TOKENS = 180000

# Token 消耗估算（每种工具大致的上下文消耗）
TOOL_COST = {
    "Agent": 50000, "Task": 30000, "Workflow": 40000,
    "WebFetch": 12000, "WebSearch": 15000,
    "Bash": 4000, "Write": 3000, "Edit": 2500, "Read": 1500,
    "Grep": 2500, "Glob": 2000, "LSP": 3000,
}
DEFAULT_COST = 3000

COUNTER_FILE = os.path.expanduser("~/.claude/tool-call-counter.json")
MONITOR_FILE = os.path.expanduser("~/.claude/.state/context_monitor.json")
LOOP_THRESHOLD = int(os.environ.get("ECC_TOOL_LOOP_THRESHOLD", "3"))


def load():
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("count", 0), d.get("est_tokens", 0)
    except (json.JSONDecodeError, OSError, IOError) as e:
        print(f"pre-suggest-compact: counter read failed: {e}", file=sys.stderr)
    return 0, 0


def save(count, est_tokens):
    try:
        os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            json.dump({"count": count, "est_tokens": est_tokens}, f, indent=2)
    except (OSError, IOError) as e:
        print(f"pre-suggest-compact: counter save failed: {e}", file=sys.stderr)


def update_tool_history(tool_name: str):
    try:
        os.makedirs(os.path.dirname(MONITOR_FILE), exist_ok=True)
        monitor = {"tool_history": [], "repeat_tool_warns": 0}
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, "r", encoding="utf-8") as f:
                monitor = json.load(f)
        history = monitor.get("tool_history", [])
        history.append(tool_name)
        monitor["tool_history"] = history[-20:]
        if len(history) >= LOOP_THRESHOLD and len(set(history[-LOOP_THRESHOLD:])) == 1:
            monitor["repeat_tool_warns"] = monitor.get("repeat_tool_warns", 0) + 1
        with open(MONITOR_FILE, "w", encoding="utf-8") as f:
            json.dump(monitor, f, indent=2)
        return monitor.get("repeat_tool_warns", 0)
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"pre-suggest-compact: monitor update failed: {e}", file=sys.stderr)
        return 0


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        tool_name = data.get("tool_name", "")
        if not tool_name:
            sys.exit(0)

        count, est_tokens = load()
        count += 1
        est_tokens += TOOL_COST.get(tool_name, DEFAULT_COST)
        est_pct = min(100, (est_tokens / CTX_WINDOW_TOKENS) * 100)
        loop_warns = update_tool_history(tool_name)

        result = None

        if count >= FORCE_COUNT or est_pct >= 70:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"🚨 上下文严重过载: {count}次调用 预估{est_pct:.0f}%\n"
                        f"🔴 强制要求: 立即执行 /compact 压缩上下文!\n"
                        f"当前工具: {tool_name}(+{TOOL_COST.get(tool_name, DEFAULT_COST)//1000}K)"
                    )
                }
            }
            count = 0
            est_tokens = 0

        elif count >= CRITICAL_COUNT or est_pct >= 50:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"⚠️ 上下文告警: {count}次调用 预估{est_pct:.0f}%\n"
                        f"🟡 强烈建议: 当前操作完成后执行 /compact\n"
                        f"当前工具: {tool_name}"
                    )
                }
            }

        elif count >= WARN_COUNT or est_pct >= 40:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"📊 上下文提醒: {count}次调用 预估{est_pct:.0f}%"
                    )
                }
            }

        if loop_warns >= 1 and result is None:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"⚠️ Tool loop: {tool_name} 连续调用≥{LOOP_THRESHOLD}次 — 换策略或委派子 Agent"
                    )
                }
            }

        if result:
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        save(count, est_tokens)

    except SystemExit:
        raise
    except Exception as e:
        print(f"pre-suggest-compact: unexpected error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
