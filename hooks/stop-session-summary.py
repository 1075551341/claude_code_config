#!/usr/bin/env python3
"""
Stop Hook: Session Summary
在会话结束时持久化会话状态

exit 0 = 正常结束
"""
# source: thedotmack/claude-mem
import json
import sys
import io
import os
from datetime import datetime

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        # 检查是否有 transcript 路径
        transcript_path = data.get("transcript_path")
        if not transcript_path:
            sys.exit(0)

        # 保存会话摘要
        summary_dir = os.path.expanduser("~/.claude/sessions")
        os.makedirs(summary_dir, exist_ok=True)

        summary_file = os.path.join(summary_dir, f"summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "transcript_path": transcript_path,
            "tool_calls": data.get("tool_calls", []),
            "event": "session_end"
        }

        # v10.10: skill/agent 真实触发日志（「配置驱动」可测量性；usage-audit 下一轮数据源）
        try:
            skill_triggers = []
            if transcript_path and os.path.exists(transcript_path):
                from collections import Counter
                counter = Counter()
                with open(transcript_path, "r", encoding="utf-8", errors="replace") as tf:
                    for line in tf:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        msg = rec.get("message") or {}
                        if msg.get("type") != "assistant":
                            continue
                        for block in (msg.get("content") or []):
                            if not isinstance(block, dict):
                                continue
                            if block.get("type") == "tool_use" and block.get("name") in ("Skill", "Task"):
                                tool_input = block.get("input") or {}
                                name = tool_input.get("skill") or tool_input.get("subagent_type") or block.get("name")
                                if name:
                                    counter[str(name)] += 1
                skill_triggers = [{"name": k, "count": v} for k, v in counter.most_common()]
                summary["skill_triggers"] = skill_triggers
                log_dir = os.path.expanduser("~/.claude/logs")
                os.makedirs(log_dir, exist_ok=True)
                with open(os.path.join(log_dir, "skill-triggers.jsonl"), "a", encoding="utf-8") as lf:
                    lf.write(json.dumps({
                        "ts": datetime.utcnow().isoformat(),
                        "cwd": os.getcwd(),
                        "skill_triggers": skill_triggers,
                    }, ensure_ascii=False) + "\n")
        except Exception as e:
            # fail-open：触发日志失败不影响会话结束，但显式报告（R16）
            print(f"skill-triggers log skipped (non-fatal): {e}", file=sys.stderr)

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
