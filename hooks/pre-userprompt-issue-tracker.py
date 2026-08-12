#!/usr/bin/env python3
"""
UserPromptSubmit Hook: 问题指纹追踪（v10.17.0）— 治「同问题重复处理」。
对 prompt 归一化生成指纹（关键名词/错误信息/文件路径 + cwd），命中历史指纹时注入
「先查上轮结论，禁止从头重做」提醒。永不阻断（exit 0）。
指纹算法与状态文件均在 `hooks/_lib/issue_state.py`（与 Cursor Guard 共用同一份，
跨编辑器重复提问才能识别）。状态 ~/.claude/.state/issue-tracker.json，默认 30 天清理。
配置 SSOT：~/.claude/config/quality_gates.json → issue_tracker。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from issue_state import merge_config, min_prompt_len, record  # noqa: E402

CONFIG_FILE = os.path.expanduser("~/.claude/config/quality_gates.json")


def load_config() -> dict:
    user_cfg = {}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f).get("issue_tracker", {})
    except (OSError, json.JSONDecodeError) as e:
        print(f"issue-tracker: config read failed: {e}", file=sys.stderr)
    return merge_config(user_cfg)


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except (OSError, ValueError) as e:
        print(f"issue-tracker: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"issue-tracker: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    cfg = load_config()
    if not cfg["enabled"]:
        sys.exit(0)

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    prompt = str(data.get("prompt", ""))
    cwd = str(data.get("cwd") or "")

    if len(prompt.strip()) < min_prompt_len(prompt, cfg):
        sys.exit(0)

    inject = record(prompt, cwd, session_id, cfg)

    if inject:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": inject,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
