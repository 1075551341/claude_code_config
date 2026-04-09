#!/usr/bin/env python3
"""
PreToolUse Hook: 项目上下文感知
会话开始时自动读取项目 CLAUDE.md 和最近的任务计划
将关键上下文注入到 Claude，减少每次都要重新解释项目背景

修复记录：
- FIX: PreToolUse:Edit hook error 根因修复 — subprocess git log 超时/挂起
- FIX: 会话缓存检查提至所有 I/O 操作之前（最关键！）
- FIX: read_package_info 内部 import re 移至模块顶层
- FIX: subprocess 统一用列表参数 + 显式 TimeoutExpired 捕获
- FIX: 所有文件操作独立 try/except，互不影响
- FIX: json.dumps 输出后立即 flush，防止缓冲区未刷新就退出
- FIX: Edit/Write 工具提前快速退出（非首次注入会话）
- FIX: Write 工具直接放行，避免写入配置文件时触发 hook error
"""
import json
import sys
import io
import os
import re
import subprocess
from datetime import datetime

# ── stdout 安全包装 ───────────────────────────────────────────────────────────
try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
SESSION_CACHE = os.path.join(GLOBAL_CLAUDE_DIR, "context_cache.json")


def load_cache() -> dict:
    try:
        if os.path.exists(SESSION_CACHE):
            with open(SESSION_CACHE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_cache(cache: dict):
    try:
        os.makedirs(os.path.dirname(SESSION_CACHE), exist_ok=True)
        if len(cache) > 30:
            for k in list(cache.keys())[: len(cache) - 30]:
                del cache[k]
        with open(SESSION_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception:
        pass


def find_project_root(start=None) -> str:
    try:
        directory = os.path.abspath(start or os.getcwd())
        markers = ["package.json", "pyproject.toml", ".git", "go.mod", "Cargo.toml"]
        for _ in range(8):
            if any(os.path.exists(os.path.join(directory, m)) for m in markers):
                return directory
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    try:
        return os.getcwd()
    except Exception:
        return os.path.expanduser("~")


def read_project_claude_md(project_root: str) -> str | None:
    for candidate in [
        os.path.join(project_root, "CLAUDE.md"),
        os.path.join(project_root, ".claude", "CLAUDE.md"),
    ]:
        try:
            if os.path.exists(candidate):
                with open(candidate, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                return content[:1500] + ("..." if len(content) > 1500 else "")
        except Exception:
            continue
    return None


def read_latest_plan(project_root: str) -> str | None:
    latest = os.path.join(project_root, ".claude", "plans", "latest.md")
    try:
        if os.path.exists(latest):
            stat = os.stat(latest)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            if mtime.date() == datetime.now().date():
                with open(latest, encoding="utf-8", errors="replace") as f:
                    return f.read()[:800]
    except Exception:
        pass
    return None


def read_recent_git_log(project_root: str) -> str | None:
    """读取最近 5 条 git commit — 使用列表参数 + 短超时，避免挂起"""
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-5"],  # 列表参数，不经 shell
            capture_output=True,
            text=True,
            timeout=3,          # FIX: 从 5s 减少到 3s
            cwd=project_root,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except subprocess.TimeoutExpired:
        pass  # FIX: 显式捕获超时，不向上传播
    except FileNotFoundError:
        pass  # git 未安装
    except Exception:
        pass
    return None


def read_package_info(project_root: str) -> str | None:
    # FIX: re 已在模块顶层导入，不在函数内重复 import
    pkg = os.path.join(project_root, "package.json")
    try:
        if os.path.exists(pkg):
            with open(pkg, encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            name = data.get("name", "")
            desc = data.get("description", "")
            tech = list(data.get("dependencies", {}).keys())[:6]
            parts = []
            if name:
                parts.append(f"项目名：{name}")
            if desc:
                parts.append(f"描述：{desc}")
            if tech:
                parts.append(f"主要依赖：{', '.join(tech)}")
            return "\n".join(parts) if parts else None
    except Exception:
        pass

    pyproj = os.path.join(project_root, "pyproject.toml")
    try:
        if os.path.exists(pyproj):
            with open(pyproj, encoding="utf-8", errors="replace") as f:
                content = f.read()
            parts = []
            name_m = re.search(r'name\s*=\s*"([^"]+)"', content)
            desc_m = re.search(r'description\s*=\s*"([^"]+)"', content)
            if name_m:
                parts.append(f"项目名：{name_m.group(1)}")
            if desc_m:
                parts.append(f"描述：{desc_m.group(1)}")
            return "\n".join(parts) if parts else None
    except Exception:
        pass
    return None


def main():
    try:
        # ── Step 1: 读入 stdin ─────────────────────────────────────────────
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        session_id = data.get("session_id", "unknown")
        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # ── Step 2: 工具过滤 ───────────────────────────────────────────────
        if tool_name not in ("Task", "Write", "Edit", "Bash"):
            sys.exit(0)

        # ── Step 3: 会话缓存检查（最优先，所有 I/O 之前）───────────────────
        # FIX: 这是修复 Edit hook error 的关键 — 绝大多数 Edit 调用走这里快速退出
        try:
            cache = load_cache()
        except Exception:
            cache = {}

        if cache.get(session_id, {}).get("context_injected"):
            sys.exit(0)

        # ── Step 4: 推断项目目录 ───────────────────────────────────────────
        file_path = tool_input.get("file_path") or tool_input.get("command", "")
        infer_dir = None
        if file_path:
            try:
                candidate_dir = os.path.dirname(os.path.abspath(str(file_path)))
                if os.path.isdir(candidate_dir):
                    infer_dir = candidate_dir
            except Exception:
                pass

        project_root = find_project_root(infer_dir)

        if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
            sys.exit(0)

        # ── Step 5: 收集上下文（各自独立 try/except）─────────────────────
        context_parts = []

        pkg_info = read_package_info(project_root)
        if pkg_info:
            context_parts.append(f"## 项目信息\n\n{pkg_info}")

        claude_md = read_project_claude_md(project_root)
        if claude_md:
            context_parts.append(f"## 项目规范（来自 CLAUDE.md）\n\n{claude_md}")

        plan = read_latest_plan(project_root)
        if plan:
            context_parts.append(f"## 当前任务计划\n\n{plan}")

        git_log = read_recent_git_log(project_root)
        if git_log:
            context_parts.append(f"## 最近提交记录\n\n```\n{git_log}\n```")

        if not context_parts:
            sys.exit(0)

        # ── Step 6: 标记已注入，然后输出 ───────────────────────────────────
        if session_id not in cache:
            cache[session_id] = {}
        cache[session_id]["context_injected"] = True
        save_cache(cache)

        full_context = (
            "🔍 **项目上下文（自动注入，仅首次）**\n\n"
            + "\n\n---\n\n".join(context_parts)
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": full_context,
            }
        }
        # FIX: 输出后立即 flush，防止缓冲区未刷新就退出
        output = json.dumps(result, ensure_ascii=False)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise  # 让 sys.exit() 正常传播
    except Exception:
        pass  # 绝不让 hook 崩溃

    sys.exit(0)


if __name__ == "__main__":
    main()
