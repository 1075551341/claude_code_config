#!/usr/bin/env python3
"""beforeSubmitPrompt: 问题指纹追踪（v10.17.0）。
同问题重复出现时注入「先查上轮结论，禁止从头重做」提醒。soft 注入，永不阻断。

指纹算法与状态文件 SSOT: ~/.claude/hooks/_lib/issue_state.py
（与 Claude Code 的 pre-userprompt-issue-tracker.py 共用同一份状态，
v10.17 起两端不再各写各的 state，跨编辑器重复提问才能被识别）。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from session_handoff import extract_session_id as handoff_session_id


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        issue_state = import_claude_lib(cfg["sync"]["claude_home"], "issue_state")
        merge_config = issue_state.merge_config
        min_prompt_len = issue_state.min_prompt_len
        record = issue_state.record

        it_cfg = merge_config(cfg.get("issue_tracker", {}))
        if not it_cfg["enabled"]:
            return

        prompt = str(data.get("prompt", ""))
        if len(prompt.strip()) < min_prompt_len(prompt, it_cfg):
            return

        session_id = handoff_session_id(data) or "unknown"
        # cwd 参与指纹：Cursor 传 cwd 但不传 workspace_roots 时，旧写法因三元运算符优先级
        # 直接落成空串，导致同一问题在 Cursor 与 Claude Code 下指纹不同、跨编辑器去重失效
        roots = data.get("workspace_roots") or []
        cwd = str(data.get("cwd") or (roots[0] if roots else ""))

        inject = record(prompt, cwd, session_id, it_cfg)
        if inject:
            write_json({"agent_message": inject})
    except Exception as e:
        print(f"issue_tracker: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
