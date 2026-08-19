#!/usr/bin/env python3
"""beforeSubmitPrompt: 完成验证门（v11.3.4）。
prompt 命中完成类关键词 **或** 状态显示本轮有未验证编辑时，注入 verification-before-completion 强制指令。
修复关键词盲区（模型连续工具调用后自行声称完成）。幂等无状态；本 hook 永不阻断。
硬门：Cursor stop → verification_stop.py 的 followup_message（enforce_mode=followup）；
Claude Code → stop-verification-gate.py exit 2。"""
from __future__ import annotations

import json
import os
import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_prompt,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from gate_messages import load_gate

DEFAULT_KEYWORDS = ["完成", "修好", "测试通过", "done", "搞定", "fixed"]
STATE_FILE = "%USERPROFILE%/.claude/.state/verification-gate.json"


def _state_path(claude_home: str) -> str:
    raw = claude_home or os.path.expanduser("~/.claude")
    return os.path.join(raw, ".state", "verification-gate.json")


def has_unverified_edits(data: dict, claude_home: str) -> bool:
    """状态检查：本轮是否有代码编辑但无验证命令记录。"""
    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    path = _state_path(claude_home)
    try:
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        entry = state.get(session_id)
        try:
            from hook_io import import_claude_lib

            r20 = import_claude_lib(claude_home, "r20_replay")
            return r20.has_unverified_edits(entry or {})
        except Exception as e:
            print(f"verification_gate: r20_replay unavailable: {e}", file=sys.stderr)
            return bool((entry or {}).get("edited_files"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_gate: state read failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["verification"]["enabled"]:
            return
        keywords = [k.lower() for k in cfg["verification"].get("prompt_keywords", DEFAULT_KEYWORDS)]
        prompt = extract_prompt(data).lower()
        keyword_hit = bool(prompt) and any(k in prompt for k in keywords)
        unverified = has_unverified_edits(data, cfg["sync"]["claude_home"])
        # 命中关键词 或 本轮有未验证编辑 → 注入（修复盲区）
        if not keyword_hit and not unverified:
            return
        write_json(
            {"additional_context": load_gate("verify", cfg["sync"]["claude_home"])}
        )
    except Exception as e:
        print(f"verification_gate: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
