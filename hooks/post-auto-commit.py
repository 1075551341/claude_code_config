#!/usr/bin/env python3
"""
PostToolUse Hook: 智能自动 Git 提交
累计 3+ 文件变更时自动提交，使用本地推断生成 commit message
不依赖外部 API，确保零延迟
"""
import json
import sys
import io
import os
import re
import subprocess
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
COMMIT_THRESHOLD = 3


def run(cmd, cwd=None):
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30, cwd=cwd,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception:
        return -1, ""


def find_git_root(start=None):
    directory = os.path.abspath(start or os.getcwd())
    for _ in range(8):
        if os.path.exists(os.path.join(directory, ".git")):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def get_counter_file(git_root: str) -> str:
    """计数器存放在项目的 .claude/ 目录下"""
    return os.path.join(git_root, ".claude", "commit_counter.json")


def load_counter(session_id, git_root):
    counter_file = get_counter_file(git_root)
    try:
        if os.path.exists(counter_file):
            with open(counter_file, encoding="utf-8") as f:
                data = json.load(f)
            return data.get(session_id, {"count": 0, "files": []})
    except Exception:
        pass
    return {"count": 0, "files": []}


def save_counter(session_id, counter, git_root):
    counter_file = get_counter_file(git_root)
    try:
        os.makedirs(os.path.dirname(counter_file), exist_ok=True)
        data = {}
        if os.path.exists(counter_file):
            with open(counter_file, encoding="utf-8") as f:
                data = json.load(f)
        data[session_id] = counter
        if len(data) > 20:
            oldest = list(data.keys())[0]
            del data[oldest]
        with open(counter_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def infer_commit_type(files):
    """根据变更文件推断 commit 类型"""
    all_files = " ".join(files).lower()
    if any(k in all_files for k in ["test", "spec", ".test.", ".spec."]):
        return "test"
    if any(k in all_files for k in ["readme", ".md", "docs/", "doc/"]):
        return "docs"
    if any(k in all_files for k in [
        "config", "setting", ".env", "webpack", "vite", "tsconfig",
        "package.json", "requirements", "dockerfile", "docker-compose",
    ]):
        return "chore"
    if any(k in all_files for k in ["style", ".css", ".scss", ".less", ".tailwind"]):
        return "style"
    if any(k in all_files for k in ["fix", "bug", "patch", "hotfix"]):
        return "fix"
    return "feat"


def infer_scope(files):
    """从文件路径推断 scope"""
    dirs = set()
    for f in files:
        parts = f.replace("\\", "/").split("/")
        if len(parts) >= 2:
            top = parts[0]
            if top not in ("src", ".", ""):
                dirs.add(top)
            elif len(parts) >= 3:
                dirs.add(parts[1])
    if dirs:
        return sorted(dirs)[0][:20]
    return ""


def infer_description(files):
    """根据文件推断变更描述"""
    ext_counts = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    top_ext = max(ext_counts, key=ext_counts.get) if ext_counts else ""
    ext_map = {
        ".tsx": "React 组件",
        ".jsx": "React 组件",
        ".vue": "Vue 组件",
        ".ts": "TypeScript 模块",
        ".js": "JavaScript 模块",
        ".py": "Python 模块",
        ".css": "样式",
        ".scss": "样式",
        ".sql": "数据库脚本",
        ".md": "文档",
        ".json": "配置",
        ".yaml": "配置",
        ".yml": "配置",
    }
    desc = ext_map.get(top_ext, "文件")
    return f"更新 {len(files)} 个{desc}"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    skip_patterns = [
        r"\.log$", r"\.tmp$", r"\.claude/", r"node_modules/",
        r"__pycache__", r"dist/", r"build/", r"\.pyc$",
    ]
    if any(re.search(p, file_path) for p in skip_patterns):
        sys.exit(0)

    git_root = find_git_root(os.path.dirname(file_path))
    if not git_root:
        sys.exit(0)

    if os.path.normpath(git_root) == GLOBAL_CLAUDE_DIR:
        sys.exit(0)

    counter = load_counter(session_id, git_root)
    if file_path not in counter["files"]:
        counter["files"].append(file_path)
        counter["count"] += 1
    save_counter(session_id, counter, git_root)

    if counter["count"] < COMMIT_THRESHOLD:
        sys.exit(0)

    run("git add -A", cwd=git_root)
    _, staged_output = run("git diff --cached --name-only", cwd=git_root)
    staged = [f for f in staged_output.splitlines() if f.strip()]

    if not staged:
        sys.exit(0)

    commit_type = infer_commit_type(staged)
    scope = infer_scope(staged)
    scope_str = f"({scope})" if scope else ""
    description = infer_description(staged)
    commit_msg = f"{commit_type}{scope_str}: {description}"

    code, output = run(f'git commit -m "{commit_msg}"', cwd=git_root)

    if code == 0:
        counter = {"count": 0, "files": []}
        save_counter(session_id, counter, git_root)

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"✅ 已自动提交：{commit_msg}（{len(staged)} 个文件）",
            }
        }
        print(json.dumps(result, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
