#!/usr/bin/env python3
"""
PreCompact Hook: Pre-Compact State
在上下文压缩前保存状态

exit 0 = 正常结束
"""
# source: open-gsd/gsd-core (原 gsd-build/get-shit-done 已归档)
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

        # 保存当前会话状态
        state_dir = os.path.expanduser("~/.claude/state")
        os.makedirs(state_dir, exist_ok=True)
        
        state_file = os.path.join(state_dir, "pre-compact-state.json")
        
        # 收集 openspec/ 状态快照
        openspec_state = {}
        openspec_dir = os.path.join(os.getcwd(), "openspec", "changes")
        try:
            if os.path.isdir(openspec_dir):
                for change_id in os.listdir(openspec_dir):
                    change_path = os.path.join(openspec_dir, change_id)
                    if os.path.isdir(change_path):
                        tasks_file = os.path.join(change_path, "tasks.md")
                        openspec_state[change_id] = {
                            "has_tasks": os.path.exists(tasks_file),
                            "files": os.listdir(change_path)[:10],
                        }
        except Exception as e:
            print(f"⚠️ {e}", file=sys.stderr)

        planning_state = {}
        planning_dir = os.path.join(os.getcwd(), ".planning", "phases")
        try:
            if os.path.isdir(planning_dir):
                for phase in os.listdir(planning_dir)[:20]:
                    phase_path = os.path.join(planning_dir, phase)
                    if os.path.isdir(phase_path):
                        state_md = os.path.join(phase_path, "STATE.md")
                        planning_state[phase] = os.path.exists(state_md)
        except Exception as e:
            print(f"⚠️ planning snapshot: {e}", file=sys.stderr)

        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "event": "pre_compact",
            "current_task_summary": data.get("summary") or data.get("current_task") or "见 openspec/planning 快照",
            "in_progress_files": data.get("in_progress_files", []),
            "pending_decisions": data.get("pending_decisions", []),
            "last_verified_checkpoint": data.get("last_checkpoint") or "pre-compact auto-save",
            "openspec_snapshot": openspec_state,
            "planning_snapshot": planning_state,
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        root_state = os.path.expanduser("~/.claude/state.json")
        with open(root_state, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
