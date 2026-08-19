#!/usr/bin/env python3
"""
UserPromptSubmit Hook: 完成验证门（v10.15.0）
prompt 命中完成类关键词 **或** 状态显示本轮有未验证编辑时，注入 verification-before-completion 强制指令。
修复关键词盲区（模型连续工具调用后自行声称完成，UserPromptSubmit 未命中关键词）。
幂等无状态；永不阻断（exit 0）。硬门在 stop-verification-gate.py 兜底。
"""
import json
import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

KEYWORDS = ["完成", "修好", "测试通过", "done", "搞定", "fixed"]
STATE_FILE = os.path.expanduser("~/.claude/.state/verification-gate.json")

def load_gate_message() -> str:
    from gate_reader import load_gate

    return load_gate("verify")


def has_unverified_edits(session_id: str) -> bool:
    """状态检查：本轮是否有代码编辑但无验证命令记录。"""
    try:
        if not os.path.exists(STATE_FILE):
            return False
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        entry = state.get(session_id)
        from r20_replay import has_unverified_edits as _unverified

        return _unverified(entry or {})
    except (OSError, json.JSONDecodeError, ImportError) as e:
        print(f"pre-userprompt-verify-gate: state read failed: {e}", file=sys.stderr)
        return False


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

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    prompt = str(data.get("prompt", "")).lower()

    keyword_hit = any(k.lower() in prompt for k in KEYWORDS)
    unverified = has_unverified_edits(session_id)

    # 命中关键词 或 本轮有未验证编辑 → 注入（修复盲区）
    if not keyword_hit and not unverified:
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
