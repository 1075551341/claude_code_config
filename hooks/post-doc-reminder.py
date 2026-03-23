#!/usr/bin/env python3
"""
PostToolUse Hook: 自动生成函数注释
检测新增的无注释函数/方法，提醒 Claude 补充 JSDoc / docstring
"""
import json
import sys
import io
import os
import re
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_new_functions(file_path, git_root):
    """获取本次新增的无注释函数"""
    try:
        result = subprocess.run(
            f'git diff HEAD "{file_path}"',
            shell=True, capture_output=True, text=True,
            timeout=15, cwd=git_root
        )
        diff = result.stdout
    except Exception:
        return []

    if not diff:
        return []

    ext  = os.path.splitext(file_path)[1].lower()
    new_funcs = []

    lines = diff.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("+") or line.startswith("+++"):
            continue

        content = line[1:].strip()

        # TypeScript/JavaScript 函数检测
        if ext in (".ts", ".tsx", ".js", ".jsx"):
            patterns = [
                r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
                r"^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(",
                r"^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?function",
                r"^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{",  # 类方法
            ]
            for pat in patterns:
                m = re.match(pat, content)
                if m:
                    func_name = m.group(1)
                    # 检查前一行是否有注释
                    prev_lines = [l[1:] for l in lines[max(0,i-3):i]
                                  if l.startswith("+")]
                    has_comment = any(
                        "/**" in l or "//" in l or "@" in l
                        for l in prev_lines
                    )
                    if not has_comment and func_name not in ("if", "for", "while"):
                        new_funcs.append(("ts/js", func_name, content[:60]))
                    break

        # Python 函数检测
        elif ext == ".py":
            m = re.match(r"^(?:async\s+)?def\s+(\w+)\s*\(", content)
            if m:
                func_name = m.group(1)
                # 跳过私有方法和魔术方法的自动注释提醒
                if not func_name.startswith("__"):
                    next_lines = [l[1:].strip() for l in lines[i+1:i+4]
                                  if l.startswith("+")]
                    has_docstring = any(
                        l.startswith('"""') or l.startswith("'''")
                        for l in next_lines
                    )
                    if not has_docstring:
                        new_funcs.append(("python", func_name, content[:60]))

    return new_funcs

def find_git_root(start):
    directory = os.path.abspath(start)
    for _ in range(8):
        if os.path.exists(os.path.join(directory, ".git")):
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

    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in (".ts", ".tsx", ".js", ".jsx", ".py"):
        sys.exit(0)

    git_root = find_git_root(os.path.dirname(file_path))
    if not git_root:
        sys.exit(0)

    new_funcs = get_new_functions(file_path, git_root)
    if not new_funcs or len(new_funcs) > 8:  # 超过 8 个跳过（避免干扰大型重构）
        sys.exit(0)

    func_list = "\n".join(
        f"  - `{name}` ({lang}): {sig}"
        for lang, name, sig in new_funcs
    )

    if ext == ".py":
        doc_format = 'Google Style docstring（包含 Args、Returns、Raises）'
    else:
        doc_format = 'JSDoc（包含 @param、@returns、@throws）'

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"📝 检测到 {len(new_funcs)} 个新函数缺少注释，请补充 {doc_format}：\n\n"
                f"{func_list}\n\n"
                "（如果这些是内部辅助函数不需要注释，可忽略此提醒）"
            )
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
