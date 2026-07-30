#!/usr/bin/env python3
"""
UserPromptSubmit Hook: 完成验证门（v10.7.0）
prompt 命中完成类关键词时注入 verification-before-completion 强制指令。
幂等无状态；永不阻断（exit 0）。
"""
import json
import sys
import io
import os

KEYWORDS = ["完成", "修好", "测试通过", "done", "搞定", "fixed"]

FALLBACK = (
    "【门控 · 完成前必做】\n"
    "Read ~/.claude/skills/verification-before-completion/SKILL.md，"
    "实际运行验证命令并贴出证据后方可声称完成（R1）。"
)


def load_gate_message() -> str:
    gate_file = os.path.join(os.path.dirname(__file__), "_lib", "gate_messages.md")
    try:
        with open(gate_file, "r", encoding="utf-8") as f:
            content = f.read()
        start = content.index("## 完成验证门")
        end = content.index("## 变更影响门")
        section = content[start:end].replace("## 完成验证门", "").strip()
        return section if section else FALLBACK
    except (OSError, ValueError) as e:
        print(f"pre-userprompt-verify-gate: gate_messages read failed: {e}", file=sys.stderr)
        return FALLBACK


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"pre-userprompt-verify-gate: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"pre-userprompt-verify-gate: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    prompt = str(data.get("prompt", "")).lower()
    if not any(k.lower() in prompt for k in KEYWORDS):
        sys.exit(0)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": load_gate_message(),
        }
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
