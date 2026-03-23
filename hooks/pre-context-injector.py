#!/usr/bin/env python3
"""
PreToolUse Hook: 项目上下文感知
会话开始时自动读取项目 CLAUDE.md 和最近的任务计划
将关键上下文注入到 Claude，减少每次都要重新解释项目背景
"""
import json
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
SESSION_CACHE = os.path.join(GLOBAL_CLAUDE_DIR, "context_cache.json")

def load_cache():
    try:
        if os.path.exists(SESSION_CACHE):
            with open(SESSION_CACHE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_cache(cache):
    try:
        os.makedirs(os.path.dirname(SESSION_CACHE), exist_ok=True)
        with open(SESSION_CACHE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass

def find_project_root(start=None):
    directory = os.path.abspath(start or os.getcwd())
    for _ in range(8):
        if any(os.path.exists(os.path.join(directory, m))
               for m in ["package.json", "pyproject.toml", ".git", "go.mod"]):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return os.getcwd()

def read_project_claude_md(project_root):
    """读取项目级 CLAUDE.md"""
    claude_md = os.path.join(project_root, "CLAUDE.md")
    if os.path.exists(claude_md):
        try:
            with open(claude_md, encoding="utf-8") as f:
                content = f.read()
            # 只取前 1500 字符避免过长
            return content[:1500] + ("..." if len(content) > 1500 else "")
        except Exception:
            pass
    return None

def read_latest_plan(project_root):
    """读取最新任务计划摘要"""
    latest = os.path.join(project_root, ".claude", "plans", "latest.md")
    if os.path.exists(latest):
        try:
            stat = os.stat(latest)
            # 只读取今天的计划
            mtime = datetime.fromtimestamp(stat.st_mtime)
            if mtime.date() == datetime.now().date():
                with open(latest, encoding="utf-8") as f:
                    return f.read()[:800]
        except Exception:
            pass
    return None

def read_recent_git_log(project_root):
    """读取最近 5 条 git commit"""
    import subprocess
    try:
        r = subprocess.run(
            "git log --oneline -5",
            shell=True, capture_output=True, text=True,
            timeout=5, cwd=project_root
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 只在会话第一次 Task 或第一次 Write/Edit 时注入上下文
    cache = load_cache()
    if cache.get(session_id, {}).get("context_injected"):
        sys.exit(0)

    # 仅在有意义的首次操作时触发
    if tool_name not in ("Task", "Write", "Edit", "Bash"):
        sys.exit(0)

    # 获取操作路径来推断项目目录
    file_path = (
        tool_input.get("file_path") or
        tool_input.get("command", "")
    )
    project_root = find_project_root(
        os.path.dirname(file_path) if file_path and os.path.exists(os.path.dirname(file_path))
        else None
    )

    if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
        sys.exit(0)

    context_parts = []

    # 1. 项目 CLAUDE.md
    claude_md = read_project_claude_md(project_root)
    if claude_md:
        context_parts.append(f"## 项目规范（来自 CLAUDE.md）\n\n{claude_md}")

    # 2. 今日任务计划
    plan = read_latest_plan(project_root)
    if plan:
        context_parts.append(f"## 当前任务计划\n\n{plan}")

    # 3. 最近提交记录
    git_log = read_recent_git_log(project_root)
    if git_log:
        context_parts.append(f"## 最近提交记录\n\n```\n{git_log}\n```")

    if not context_parts:
        sys.exit(0)

    # 标记已注入
    if session_id not in cache:
        cache[session_id] = {}
    cache[session_id]["context_injected"] = True
    # 只保留最近 30 个会话
    if len(cache) > 30:
        del cache[list(cache.keys())[0]]
    save_cache(cache)

    full_context = (
        "🔍 **项目上下文（自动注入）**\n\n" +
        "\n\n---\n\n".join(context_parts)
    )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": full_context
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
