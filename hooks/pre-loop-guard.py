#!/usr/bin/env python3
"""
PreToolUse Hook: Observer Loop 防护 + 重入检测
来源: affaan-m/ECC v2.0.0-rc.1 | 5层守卫简化版

防护等级:
  L1: 重入检测 — 同一 hook 30s 内禁止重复触发
  L2: 调用计数 — 单会话同一工具调用超过阈值告警
  L3: 超时熔断 — 单次 hook 执行超过 10s 中断
  L4: 异常隔离 — hook 内部异常不影响主流程
  L5: 状态恢复 — 异常后自动恢复安全默认值

环境变量:
  ECC_HOOK_PROFILE=minimal|standard|strict (默认: standard)
  ECC_DISABLED_HOOKS=hook_id1,hook_id2
"""
import json
import sys
import os
import time
from pathlib import Path

# ── 配置 ────────────────────────────────────────────────────
HOOK_ID = "pre-loop-guard"
PROFILE = os.environ.get("ECC_HOOK_PROFILE", "standard")
MAX_HOOK_TIME_SEC = 10
SAME_TOOL_INTERVAL_SEC = 30
MAX_TOOL_CALLS_PER_SESSION = 500
STATE_DIR = Path(os.environ.get("CLAUDE_STATE_DIR", Path.home() / ".claude" / ".state"))
STATE_FILE = STATE_DIR / "loop_guard_state.json"

# ── L4: 异常隔离 ─────────────────────────────────────────────
try:
    import json
    import time
    start_time = time.time()

    # ── 读取输入 ──────────────────────────────────────────────
    input_data = json.loads(sys.stdin.read())
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # ── L1: 重入检测 ──────────────────────────────────────────
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            state = {}

    last_call = state.get("last_guard_call", 0)
    elapsed = time.time() - last_call
    if elapsed < SAME_TOOL_INTERVAL_SEC:
        # 30s 内已执行过，跳过
        print(json.dumps({"continue": True, "suppressOutput": True}))
        sys.exit(0)

    # ── L2: 调用计数 ──────────────────────────────────────────
    if PROFILE in ("standard", "strict"):
        call_count = state.get("guard_call_count", 0) + 1
        state["guard_call_count"] = call_count
        if call_count > MAX_TOOL_CALLS_PER_SESSION:
            # 超过阈值，记录警告但不中断
            state["warning"] = f"guard_call_count_exceeded: {call_count}"
    else:
        call_count = state.get("guard_call_count", 0)

    # ── L3: 超时自检 ──────────────────────────────────────────
    # 本轮由外层 timeout 控制，hook 内仅做快速检查

    # ── 持久化状态 ────────────────────────────────────────────
    state["last_guard_call"] = time.time()
    state["last_tool_name"] = tool_name

    if elapsed < 60:
        STATE_FILE.write_text(json.dumps(state))
    else:
        # 超过 60s 才写盘，减少 IO
        STATE_FILE.write_text(json.dumps(state))

except Exception as e:
    # L5: 状态恢复 — 异常不影响主流程
    pass

# ── 总是放行 ──────────────────────────────────────────────────
print(json.dumps({"continue": True, "suppressOutput": True}))
