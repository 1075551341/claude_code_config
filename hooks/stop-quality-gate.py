#!/usr/bin/env python3
"""Stop Hook: 质量门检查 - 在会话结束时检查schema drift和范围缩减"""
import sys
import json
import os

def check_quality_gates():
    issues = []
    
    # 检查1: Schema Drift（简化版 - 检查是否有ORM文件变更但无migration）
    # 实际实现需要结合项目结构
    
    # 检查2: 范围缩减（简化版 - 检查计划vs实现）
    plan_cache = os.path.expanduser("~/.claude/plan_cache.json")
    if os.path.exists(plan_cache):
        try:
            with open(plan_cache, 'r') as f:
                plans = json.load(f)
            if plans:
                issues.append("ℹ️ 存在活跃计划，建议在ship前执行quality-gate技能验证")
        except:
            pass
    
    return issues

def main():
    issues = check_quality_gates()
    for issue in issues:
        print(issue, file=sys.stderr)
    sys.exit(0)

if __name__ == "__main__":
    main()
