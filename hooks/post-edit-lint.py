#!/usr/bin/env python3
"""
PostToolUse Hook: Lint + 类型检查
编辑 TS/JS 文件后自动运行 ESLint 和 tsc --noEmit
问题反馈给 Claude，让它自动修复
"""
import json
import sys
import io
import subprocess
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=60, cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except Exception:
        return -1, "", ""

def find_project_root(file_path):
    directory = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):
        if os.path.exists(os.path.join(directory, "package.json")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in (".ts", ".tsx", ".js", ".jsx"):
        sys.exit(0)

    project_root = find_project_root(file_path)
    if not project_root:
        sys.exit(0)

    issues = []

    # ── ESLint ──────────────────────────────────────────────
    local_eslint = os.path.join(project_root, "node_modules", ".bin", "eslint")
    if os.path.exists(local_eslint):
        code, stdout, stderr = run(
            f'"{local_eslint}" "{file_path}" --max-warnings 0 --format compact',
            cwd=project_root
        )
        if code != 0 and (stdout.strip() or stderr.strip()):
            output = (stdout + stderr).strip()
            # 只取前 20 行，避免输出过长
            lines = output.splitlines()[:20]
            issues.append("ESLint 问题:\n" + "\n".join(lines))

    # ── TypeScript 类型检查（仅 .ts/.tsx）────────────────────
    if ext in (".ts", ".tsx"):
        tsconfig = os.path.join(project_root, "tsconfig.json")
        if os.path.exists(tsconfig):
            code, stdout, stderr = run(
                "npx tsc --noEmit --pretty false 2>&1",
                cwd=project_root
            )
            if code != 0:
                output = (stdout + stderr).strip()
                lines = output.splitlines()[:15]
                issues.append("TypeScript 类型错误:\n" + "\n".join(lines))

    # 有问题时输出给 Claude（additionalContext）
    if issues:
        feedback = "\n\n".join(issues)
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"代码质量检查发现以下问题，请自动修复：\n\n{feedback}"
            }
        }
        print(json.dumps(result, ensure_ascii=False))

    sys.exit(0)

if __name__ == "__main__":
    main()
