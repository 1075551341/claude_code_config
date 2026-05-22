#!/usr/bin/env python3
"""
PostToolUse Hook: 智能自动 Git 提交
累计 3+ 文件变更时自动提交，使用本地推断生成 commit message

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: subprocess 列表参数替代 shell=True（安全+跨平台）
- FIX: 路径处理改用 os.path.join
"""
import json
import sys
import io
import os
import re
import subprocess
from datetime import datetime

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
COMMIT_THRESHOLD = 3


def run_git(args: list, cwd=None) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30, cwd=cwd,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    except FileNotFoundError:
        return -1, "git not found"
    except Exception:
        return -1, ""


def find_git_root(start=None) -> str | None:
    try:
        directory = os.path.abspath(start or os.getcwd())
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


def get_counter_file(git_root: str) -> str:
    return os.path.join(git_root, ".claude", "commit_counter.json")


def load_counter(session_id: str, git_root: str) -> dict:
    try:
        cf = get_counter_file(git_root)
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
            return data.get(session_id, {"count": 0, "files": []})
    except Exception:
        pass
    return {"count": 0, "files": []}


def save_counter(session_id: str, counter: dict, git_root: str):
    try:
        cf = get_counter_file(git_root)
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        data = {}
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
        data[session_id] = counter
        if len(data) > 20:
            for k in list(data.keys())[: len(data) - 20]:
                del data[k]
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def infer_commit_type(files: list[str]) -> str:
    all_files = " ".join(files).lower()
    if any(k in all_files for k in ["test", "spec", ".test.", ".spec."]):
        return "test"
    if any(k in all_files for k in ["readme", ".md", "docs/", "doc/"]):
        return "docs"
    if any(k in all_files for k in [
        "config", "setting", ".env", "webpack", "vite", "tsconfig",
        "package.json", "requirements", "dockerfile", "docker-compose",
        ".eslintrc", ".prettierrc", "tailwind.config",
    ]):
        return "chore"
    if any(k in all_files for k in ["style", ".css", ".scss", ".less"]):
        return "style"
    if any(k in all_files for k in ["fix", "bug", "patch", "hotfix", "error"]):
        return "fix"
    return "feat"


def infer_scope(files: list[str]) -> str:
    dirs: set[str] = set()
    for f in files:
        parts = f.replace("\\", "/").split("/")
        if len(parts) >= 2:
            top = parts[0]
            if top not in ("src", ".", ""):
                dirs.add(top)
            elif len(parts) >= 3:
                dirs.add(parts[1])
    return sorted(dirs)[0][:20] if dirs else ""


def infer_description(files: list[str]) -> str:
    ext_counts: dict[str, int] = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    top_ext = max(ext_counts, key=ext_counts.get) if ext_counts else ""
    ext_map = {
        ".tsx": "React 组件", ".jsx": "React 组件", ".vue": "Vue 组件",
        ".ts": "TypeScript 模块", ".js": "JavaScript 模块",
        ".py": "Python 模块", ".css": "样式", ".scss": "样式",
        ".sql": "数据库脚本", ".md": "文档",
        ".json": "配置", ".yaml": "配置", ".yml": "配置",
    }
    desc = ext_map.get(top_ext, "文件")
    return f"更新 {len(files)} 个{desc}"


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        session_id = data.get("session_id", "unknown")

        if tool_name not in ("Edit", "Write", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        skip_patterns = [
            r"\.log$", r"\.tmp$", r"\.claude[\\/]", r"node_modules[\\/]",
            r"__pycache__[\\/]", r"dist[\\/]", r"build[\\/]", r"\.pyc$",
            r"\.DS_Store$", r"Thumbs\.db$",
        ]
        if any(re.search(p, file_path, re.IGNORECASE) for p in skip_patterns):
            sys.exit(0)

        git_root = find_git_root(os.path.dirname(os.path.abspath(file_path)))
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

        try:
            run_git(["add", "-A"], cwd=git_root)
            _, staged_output = run_git(["diff", "--cached", "--name-only"], cwd=git_root)
            staged = [f for f in staged_output.splitlines() if f.strip()]
            if not staged:
                sys.exit(0)

            commit_type = infer_commit_type(staged)
            scope       = infer_scope(staged)
            scope_str   = f"({scope})" if scope else ""
            description = infer_description(staged)
            commit_msg  = f"{commit_type}{scope_str}: {description}"

            code, _ = run_git(["commit", "-m", commit_msg], cwd=git_root)

            if code == 0:
                save_counter(session_id, {"count": 0, "files": []}, git_root)
                result = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": (
                            f"✅ 已自动提交：{commit_msg}（{len(staged)} 个文件）"
                        ),
                    }
                }
                sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception:
            pass

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
