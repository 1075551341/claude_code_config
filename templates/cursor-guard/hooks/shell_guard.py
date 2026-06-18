#!/usr/bin/env python3
"""beforeShellExecution: Shell 危险命令守卫。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import ensure_hook_output, ensure_lib_path, read_stdin, setup_stdio, write_json

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from shell_patterns import (
    is_network_command,
    match_deny,
    match_git_commit,
    match_git_stash,
    match_warn,
)


def extract_command(data: dict) -> str:
    for key in ("command", "cmd"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["shell"]["enabled"]:
            return

        command = extract_command(data)
        if not command:
            return

        git_cfg = cfg.get("git", {})
        if git_cfg.get("forbid_stash") and match_git_stash(command):
            write_json(
                {
                    "permission": "deny",
                    "user_message": "已禁止 Agent 执行 git stash（请本地手动处理工作区）",
                    "agent_message": "【Cursor Guard】禁止 git stash。勿自动 stash；请用户本地处理或换用 worktree。",
                }
            )
            return

        if git_cfg.get("forbid_auto_commit") and match_git_commit(command):
            if git_cfg.get("commit_requires_ask"):
                write_json(
                    {
                        "permission": "ask",
                        "user_message": "Agent 拟执行 git commit — 仅在你本条消息已明确要求「提交」时批准",
                        "agent_message": "【Cursor Guard】禁止自动提交。用户未显式要求 commit 时不得执行。",
                    }
                )
                return
            write_json(
                {
                    "permission": "deny",
                    "user_message": "已禁止 Agent 执行 git commit（请本地手动提交）",
                    "agent_message": "【Cursor Guard】禁止 git commit。请用户本地执行。",
                }
            )
            return

        deny = match_deny(command)
        if deny:
            write_json(
                {
                    "permission": "deny",
                    "user_message": f"Shell 已拦截: {deny}",
                    "agent_message": f"【Cursor Guard】{deny}\n命令: {command[:200]}",
                }
            )
            return

        if cfg["shell"]["ask_network"] and is_network_command(command):
            write_json(
                {
                    "permission": "ask",
                    "user_message": "该命令可能访问网络，请确认后继续。",
                    "agent_message": f"网络命令需确认: {command[:200]}",
                }
            )
            return

        warn = match_warn(command)
        if warn:
            write_json(
                {
                    "permission": "allow",
                    "agent_message": f"【Cursor Guard · Shell 警告】{warn}",
                }
            )
    except Exception as e:
        print(f"shell_guard: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
