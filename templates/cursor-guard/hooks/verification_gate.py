#!/usr/bin/env python3
"""beforeSubmitPrompt: 完成验证门（v11.4.7）。

仅在存在未验证编辑时注入。裸词「完成」不再命中。
计划等待 / 门控回灌 / 无编辑 → 不注入。永不阻断。
"""
from __future__ import annotations

import json
import os
import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_prompt,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from gate_messages import load_gate
from session_handoff import extract_session_id as handoff_session_id

def _state_path(claude_home: str) -> str:
    raw = claude_home or os.path.expanduser("~/.claude")
    return os.path.join(raw, ".state", "verification-gate.json")


def _load_entry(claude_home: str, session_id: str) -> dict:
    if not session_id:
        return {}
    path = _state_path(claude_home)
    try:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get(session_id) or {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_gate: state read failed: {e}", file=sys.stderr)
        return {}


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["verification"]["enabled"]:
            return
        claude_home = cfg["sync"]["claude_home"]
        prompt = extract_prompt(data)
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
        except Exception as e:
            print(f"verification_gate: r20_replay unavailable: {e}", file=sys.stderr)
            r20 = None

        if r20 is not None and r20.is_gate_echo(prompt):
            return

        session_id = handoff_session_id(data)
        entry = _load_entry(claude_home, session_id)
        if r20 is not None and r20.is_awaiting_plan(entry, data):
            return

        unverified = False
        if r20 is not None:
            unverified = r20.has_unverified_edits(entry)
        else:
            unverified = bool(entry.get("edited_files"))

        if not unverified:
            return
        write_json(
            {"additional_context": load_gate("verify", claude_home)}
        )
    except Exception as e:
        print(f"verification_gate: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
