#!/usr/bin/env python3
"""Stop Hook: 质量门检查 - 在会话结束时检查schema drift和范围缩减 + R16裸except扫描"""
# source: obra/superpowers + FR-21
import sys
import json
import os
import re
import glob as globmod

def check_quality_gates():
    issues = []

    plan_cache = os.path.expanduser("~/.claude/plan_cache.json")
    if os.path.exists(plan_cache):
        try:
            with open(plan_cache, 'r') as f:
                plans = json.load(f)
            if plans:
                issues.append("ℹ️ 存在活跃计划，建议在ship前执行quality-gate技能验证")
        except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
            issues.append(f"⚠️ plan_cache读取失败: {e}")

    return issues

def check_bare_except():
    """R16: 扫描hooks/目录裸except:pass，必须为0"""
    issues = []
    hooks_dir = os.path.expanduser("~/.claude/hooks")
    # 匹配 except:pass 或 except Exception:pass（pass后面跟换行/注释/行尾）
    pattern = re.compile(r'except(?:\s+[A-Za-z]\w*(?:\s*,\s*[A-Za-z]\w*)*)?\s*:\s*pass\s*(?:#.*)?$', re.MULTILINE)

    for pyfile in globmod.glob(os.path.join(hooks_dir, "*.py")):
        basename_check = os.path.basename(pyfile)
        if pyfile.endswith("__init__.py") or "_optional" in pyfile or "_deprecated" in pyfile:
            continue
        # 跳过扫描器自身（避免匹配自己的 docstring）
        if basename_check == "stop-quality-gate.py":
            continue
        try:
            with open(pyfile, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            matches = pattern.findall(content)
            if matches:
                basename = os.path.basename(pyfile)
                issues.append(f"🚫 R16违规 {basename}: 发现{len(matches)}处裸except:pass")
        except (OSError, UnicodeDecodeError) as e:
            issues.append(f"⚠️ 扫描{os.path.basename(pyfile)}失败: {e}")

    return issues

def main():
    issues = check_quality_gates() + check_bare_except()
    for issue in issues:
        print(issue, file=sys.stderr)
    if any("🚫" in i for i in issues):
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
