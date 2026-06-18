#!/usr/bin/env python3
"""
Stop Hook: GateGuard 上下文监控（ECC 升级版）
检测：上下文阈值 / tool loop / scope creep / 成本警告

环境变量:
  ECC_CONTEXT_MONITOR_COST_WARNINGS=off  — 关闭成本警告
  ECC_HOOK_PROFILE=minimal|standard|strict
"""
import json
import os
import sys
import io
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_lib"))
from context_thresholds import ctx_force_pct, ctx_warn_pct, estimate_usage_pct  # noqa: E402

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"stop-context-monitor: stdout setup failed: {e}", file=sys.stderr)

STATE_DIR = Path(os.environ.get("CLAUDE_STATE_DIR", Path.home() / ".claude" / ".state"))
MONITOR_FILE = STATE_DIR / "context_monitor.json"
COUNTER_FILE = Path.home() / ".claude" / "tool-call-counter.json"
PROFILE = os.environ.get("ECC_HOOK_PROFILE", "standard")
COST_WARNINGS = os.environ.get("ECC_CONTEXT_MONITOR_COST_WARNINGS", "on") != "off"


def load_json(path: Path, default=None):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"stop-context-monitor: read {path} failed: {e}", file=sys.stderr)
    return default if default is not None else {}


def save_json(path: Path, data: dict):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"stop-context-monitor: write {path} failed: {e}", file=sys.stderr)


def detect_tool_loop(tool_history: list) -> bool:
    if len(tool_history) < 4:
        return False
    recent = tool_history[-4:]
    if len(set(recent)) == 1:
        return True
    from collections import Counter
    counts = Counter(recent)
    return any(c >= 3 for c in counts.values())


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print(f"stop-context-monitor: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    if PROFILE == "minimal":
        sys.exit(0)

    monitor = load_json(MONITOR_FILE, {"tool_history": [], "warnings": []})
    counter = load_json(COUNTER_FILE, {"count": 0, "est_tokens": 0})

    est_tokens = counter.get("est_tokens", 0)
    est_pct = estimate_usage_pct(est_tokens)

    warnings = []

    if est_pct >= ctx_force_pct():
        warnings.append(f"🔴 上下文≥{ctx_force_pct():.0f}%（预估{est_pct:.0f}%）— 下次会话前必须 /compact")
    elif est_pct >= ctx_warn_pct():
        warnings.append(f"⚠️ 上下文≥{ctx_warn_pct():.0f}%（预估{est_pct:.0f}%）— 择机 /compact")

    tool_history = monitor.get("tool_history", [])
    if detect_tool_loop(tool_history):
        warnings.append("⚠️ Tool loop 检测：相同工具连续调用≥3次 — 换策略或委派子 Agent")

    repeat_warns = monitor.get("repeat_tool_warns", 0)
    if repeat_warns >= 2:
        warnings.append("⚠️ Scope creep：多次偏离原始任务 — 确认是否仍在目标范围内")

    if COST_WARNINGS and counter.get("count", 0) >= 40:
        warnings.append(f"💰 高成本会话：{counter.get('count')} 次工具调用 — 考虑拆分子任务")

    if warnings and PROFILE in ("standard", "strict"):
        output = {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": "GateGuard 监控:\n" + "\n".join(warnings),
            }
        }
        sys.stdout.write(json.dumps(output, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    monitor["last_stop_pct"] = est_pct
    monitor["last_warnings"] = warnings
    save_json(MONITOR_FILE, monitor)

    sys.exit(0)


if __name__ == "__main__":
    main()
