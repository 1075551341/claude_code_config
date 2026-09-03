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

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    prompt = str(data.get("prompt", ""))
    cwd = str(data.get("cwd") or "")
    transcript_path = str(data.get("transcript_path") or "")

    scenario_inject = None
    try:
        from scenario_router import inject_for_prompt

        scenario_inject = inject_for_prompt(
            prompt, session_id=session_id, transcript_path=transcript_path
        )
    except Exception as e:  # noqa: BLE001 — 显式报出后继续（R16）
        print(f"issue-tracker: scenario inject failed: {e}", file=sys.stderr)

    if not cfg["enabled"]:
        if scenario_inject:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": scenario_inject,
                }
            }
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        sys.exit(0)

    if len(prompt.strip()) < min_prompt_len(prompt, cfg) and not scenario_inject:
        sys.exit(0)

    inject = None
    if len(prompt.strip()) >= min_prompt_len(prompt, cfg):
        inject = record(prompt, cwd, session_id, cfg)

    # v11.4 需求指纹留存：与问题指纹同点捕获，供 Stop 门 R20 实质比对（失败不阻断）
    try:
        from req_fingerprint import save_requirements

        save_requirements(session_id, prompt)
    except Exception as e:  # noqa: BLE001 — 显式报出后继续（R16，禁止裸吞）
        print(f"issue-tracker: req fingerprint failed: {e}", file=sys.stderr)

    parts = [p for p in (inject, scenario_inject) if p]
    if parts:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n\n".join(parts),
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
