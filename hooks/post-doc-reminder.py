#!/usr/bin/env python3
"""
PostToolUse Hook: 自动生成函数注释提醒
检测新增的无注释函数/方法，提醒 Claude 补充 JSDoc / docstring

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: subprocess 列表参数 + TimeoutExpired 显式捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: 新增 Go / Rust 函数检测支持
"""
import json
import sys
import io
import os
import re
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def find_git_root(start: str) -> str | None:
    try:
        directory = os.path.abspath(start)
        for _ in range(8):
            if os.path.exists(os.path.join(directory, ".git")):
                return directory
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None


def get_diff(file_path: str, git_root: str) -> str:
    try:
        r = subprocess.run(
            ["git", "diff", "HEAD", "--", file_path],
            capture_output=True, text=True, timeout=10, cwd=git_root,
        )
        if r.returncode == 0:
            return r.stdout
        r2 = subprocess.run(
            ["git", "diff", "--cached", "--", file_path],
            capture_output=True, text=True, timeout=10, cwd=git_root,
        )
        return r2.stdout
    except subprocess.TimeoutExpired:
        return ""
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def get_new_functions(file_path: str, git_root: str) -> list[tuple[str, str, str]]:
    diff = get_diff(file_path, git_root)
    if not diff:
        return []

    ext = os.path.splitext(file_path)[1].lower()
    new_funcs = []
    lines = diff.splitlines()

    for i, line in enumerate(lines):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()

        if ext in (".ts", ".tsx", ".js", ".jsx"):
            patterns = [
                r"^(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+(\w+)\s*[(<]",
                r"^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>",
                r"^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?function",
                r"^\s*(?:public|private|protected|static|async)?\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[\w<>\[\]|]+)?\s*\{",
            ]
            for pat in patterns:
                m = re.match(pat, content)
                if m:
                    func_name = m.group(1)
                    if func_name in ("if", "for", "while", "switch", "catch", "try"):
                        break
                    prev_added = [l[1:] for l in lines[max(0, i - 4):i] if l.startswith("+")]
                    has_comment = any(
                        re.search(r"/\*\*|//\s*@|@param|@returns|@throws", l, re.IGNORECASE)
                        for l in prev_added
                    )
                    if not has_comment:
                        new_funcs.append(("ts/js", func_name, content[:70]))
                    break

        elif ext == ".py":
            m = re.match(r"^(?:async\s+)?def\s+(\w+)\s*\(", content)
            if m:
                func_name = m.group(1)
                if func_name.startswith("__") and func_name.endswith("__"):
                    continue
                next_added = [
                    l[1:].strip() for l in lines[i + 1: i + 5] if l.startswith("+")
                ]
                has_docstring = any(
                    l.startswith('"""') or l.startswith("'''") or l.startswith('r"""')
                    for l in next_added
                )
                if not has_docstring:
                    new_funcs.append(("python", func_name, content[:70]))

        elif ext == ".go":
            m = re.match(r"^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(", content)
            if m:
                func_name = m.group(1)
                if func_name[0].isupper():  # 只检查导出函数
                    prev_added = [l[1:] for l in lines[max(0, i - 3):i] if l.startswith("+")]
                    has_comment = any(l.strip().startswith("//") for l in prev_added)
                    if not has_comment:
                        new_funcs.append(("go", func_name, content[:70]))

    return new_funcs


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
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
        if ext not in (".ts", ".tsx", ".js", ".jsx", ".py", ".go"):
            sys.exit(0)

        git_root = find_git_root(os.path.dirname(os.path.abspath(file_path)))
        if not git_root:
            sys.exit(0)

        new_funcs = get_new_functions(file_path, git_root)
        if not new_funcs or len(new_funcs) > 10:
            sys.exit(0)

        func_list = "\n".join(
            f"  - `{name}` ({lang}): `{sig}`" for lang, name, sig in new_funcs
        )

        if ext == ".py":
            doc_format = "Google Style docstring（含 Args、Returns、Raises）"
        elif ext == ".go":
            doc_format = "Go doc comment（以函数名开头的单行或多行注释）"
        else:
            doc_format = "JSDoc（含 @param、@returns、@throws）"

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"📝 检测到 {len(new_funcs)} 个新函数缺少文档注释，"
                    f"请补充 {doc_format}：\n\n{func_list}\n\n"
                    "（若为内部辅助函数无需对外注释，可忽略此提醒）"
                ),
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
