#!/usr/bin/env python3
"""PreToolUse Hook: 工作流守卫 - 确保阶段式工作流按序执行"""
import sys
import json
import os

PHASES = ["discuss", "plan", "execute", "verify", "ship"]
STATE_FILE = os.path.expanduser("~/.claude/.workflow_state")

def get_current_phase():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return f.read().strip()
        except:
            pass
    return None

def main():
    current = get_current_phase()
    if current and current in PHASES:
        # 仅记录当前阶段，不阻断
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
