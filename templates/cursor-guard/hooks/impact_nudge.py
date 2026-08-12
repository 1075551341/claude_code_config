#!/usr/bin/env python3
"""preToolUse: 变更影响门（v10.17.0）。
**每个文件首次被编辑**时注入 change-impact-analysis 强制指令（v10.7–v10.16 每会话
只注入一次，之后所有编辑无门，是「遗漏关联文件」的成因）。
永不 deny（决策：注入提醒，不阻断流程）。
路径解析走 Claude 侧共享库 `_lib/tool_paths.py`，与验证追踪器同一套。"""
from __future__ import annotations

import json
import os
import sys
import time

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_file_path,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config, state_path
from gate_messages import load_gate
from session_handoff import extract_session_id as handoff_session_id

STATE_NAME = "impact_nudge.json"
STALE_SECONDS = 7 * 24 * 3600
MAX_TRACKED_FILES = 200


def _edited_paths(data: dict, claude_home: str) -> list[str]:
    """优先用共享解析器（覆盖 MCP 写工具入参）；不可用时退回 hook_io 单路径提取。"""
    cwd = str(data.get("cwd") or "")
    tool_input = data.get("tool_input") or data.get("input") or {}
    try:
        tool_paths = import_claude_lib(claude_home, "tool_paths")
        paths = tool_paths.extract_edit_paths(tool_input, cwd)
        if paths:
            return paths
        top_level = tool_paths.extract_edit_paths(data, cwd)
        if top_level:
            return top_level
    except Exception as e:
        print(f"impact_nudge: tool_paths unavailable: {e}", file=sys.stderr)
    single = extract_file_path(data)
    return [single] if single else []


def _load_state() -> dict:
    path = state_path(STATE_NAME)
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"impact_nudge: state read failed: {e}", file=sys.stderr)
    return {}


def _save_state(state: dict) -> None:
    path = state_path(STATE_NAME)
    try:
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        path.write_text(json.dumps(state, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"impact_nudge: state write failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["impact"]["enabled"]:
            return

        session_id = handoff_session_id(data) or "unknown"
        claude_home = cfg["sync"]["claude_home"]
        paths = _edited_paths(data, claude_home)

        state = _load_state()
        entry = state.setdefault(session_id, {"nudged": True, "ts": time.time(), "files": []})
        tracked = entry.setdefault("files", [])

        # 解析不出路径时退回会话级语义，避免完全失去门控
        targets = paths or ["__unknown__"]
        fresh = [p for p in targets if p not in tracked]
        if not fresh:
            return

        tracked.extend(fresh)
        del tracked[:-MAX_TRACKED_FILES]
        entry["ts"] = time.time()
        _save_state(state)

        message = load_gate("impact", claude_home)
        if len(tracked) > len(fresh):
            names = ", ".join(os.path.basename(p) for p in fresh)
            message = (
                f"{message}\n\n"
                f"（本会话新增编辑目标：{names} — 影响面须针对该文件重新评估，"
                "勿沿用上一个文件的分析结论）"
            )
        write_json({"agent_message": message})
    except Exception as e:
        print(f"impact_nudge: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
