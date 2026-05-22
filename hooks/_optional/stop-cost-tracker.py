#!/usr/bin/env python3
"""
Stop Hook: Cost Tracker
发出运行成本遥测标记

exit 0 = 正常结束
"""
import json
import sys
import io
import os
from datetime import datetime

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        # 记录成本信息
        cost_dir = os.path.expanduser("~/.claude/costs")
        os.makedirs(cost_dir, exist_ok=True)
        
        cost_file = os.path.join(cost_dir, f"cost-{datetime.now().strftime('%Y%m%d')}.json")
        
        # 简单的成本估算（基于工具调用次数）
        tool_calls = data.get("tool_calls", [])
        estimated_cost = len(tool_calls) * 0.001  # 假设每次调用成本
        
        cost_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_call_count": len(tool_calls),
            "estimated_cost": estimated_cost,
            "cwd": os.getcwd()
        }
        
        # 读取现有成本记录
        existing_costs = []
        if os.path.exists(cost_file):
            try:
                with open(cost_file, "r", encoding="utf-8") as f:
                    existing_costs = json.load(f)
            except:
                existing_costs = []
        
        existing_costs.append(cost_entry)
        
        with open(cost_file, "w", encoding="utf-8") as f:
            json.dump(existing_costs, f, indent=2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
