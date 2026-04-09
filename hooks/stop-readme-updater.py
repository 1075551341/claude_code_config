#!/usr/bin/env python3
"""
Stop Hook: README 自动生成/更新器
会话结束后分析项目变更，使用本地模板生成 README.md

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: subprocess 列表参数 + TimeoutExpired 显式捕获
- FIX: 路径处理改用 os.path.join（修复 Windows 混合分隔符）
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


def run_git(args: list, cwd=None) -> tuple[int, str]:
    try:
        r = subprocess.run(
            ["git"] + args, capture_output=True, text=True, timeout=30, cwd=cwd,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, ""
    except FileNotFoundError:
        return -1, ""
    except Exception:
        return -1, ""


def find_project_root(start: str = None) -> str | None:
    try:
        directory = os.path.abspath(start or os.getcwd())
        markers = ["package.json", "pyproject.toml", "Cargo.toml", ".git", "go.mod", "pom.xml"]
        for _ in range(8):
            if any(os.path.exists(os.path.join(directory, m)) for m in markers):
                return directory
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None


def get_git_changes(project_root: str) -> dict:
    result = {"changed_files": [], "added_files": [], "summary": ""}

    for diff_args in (
        ["diff", "--name-status", "HEAD"],
        ["diff", "--cached", "--name-status"],
    ):
        _, status = run_git(diff_args, cwd=project_root)
        if status:
            for line in status.splitlines():
                parts = line.split("\t", 1)
                if len(parts) < 2:
                    continue
                flag, path = parts[0].strip(), parts[1].strip()
                if flag == "A" and path not in result["added_files"]:
                    result["added_files"].append(path)
                elif flag in ("M", "D", "R", "C") and path not in result["changed_files"]:
                    result["changed_files"].append(path)

    total = len(result["changed_files"]) + len(result["added_files"])
    result["summary"] = (
        f"变更 {len(result['changed_files'])} 个文件，"
        f"新增 {len(result['added_files'])} 个文件（共 {total} 个）"
    )
    return result


def has_significant_changes(changes: dict) -> bool:
    ignore_patterns = [
        r"\.log$", r"\.lock$", r"\.claude[\\/]", r"node_modules[\\/]",
        r"__pycache__", r"\.pyc$", r"dist[\\/]", r"build[\\/]", r"README\.md$",
    ]
    all_files = changes["changed_files"] + changes["added_files"]
    significant = [
        f for f in all_files
        if not any(re.search(p, f) for p in ignore_patterns)
    ]
    return len(significant) >= 2


def read_project_info(project_root: str) -> dict:
    info = {
        "name": os.path.basename(project_root),
        "type": "unknown",
        "description": "",
        "scripts": {},
        "dependencies": [],
        "structure": [],
    }

    pkg_path = os.path.join(project_root, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                pkg = json.load(f)
            info["name"]        = pkg.get("name", info["name"])
            info["description"] = pkg.get("description", "")
            info["type"]        = "nodejs"
            info["scripts"]     = pkg.get("scripts", {})
            info["dependencies"] = list(pkg.get("dependencies", {}).keys())[:12]
        except Exception:
            pass

    pyproject_path = os.path.join(project_root, "pyproject.toml")
    if info["type"] == "unknown" and os.path.exists(pyproject_path):
        info["type"] = "python"
        try:
            with open(pyproject_path, encoding="utf-8") as f:
                content = f.read()
            m = re.search(r'name\s*=\s*"([^"]+)"', content)
            if m:
                info["name"] = m.group(1)
            m = re.search(r'description\s*=\s*"([^"]+)"', content)
            if m:
                info["description"] = m.group(1)
        except Exception:
            pass

    try:
        entries = []
        for entry in sorted(os.scandir(project_root), key=lambda e: e.name):
            if not entry.name.startswith(".") and entry.name not in (
                "node_modules", "__pycache__", "dist", "build", ".git", "vendor",
            ):
                prefix = "📁 " if entry.is_dir() else "📄 "
                entries.append(prefix + entry.name)
        info["structure"] = entries[:15]
    except Exception:
        pass

    return info


def read_latest_plan(project_root: str) -> str:
    latest = os.path.join(project_root, ".claude", "plans", "latest.md")
    try:
        if os.path.exists(latest):
            with open(latest, encoding="utf-8") as f:
                content = f.read()
            match = re.search(r"## 📋 任务分析\n\n(.+?)(?=\n---|\n##)", content, re.DOTALL)
            if match:
                return match.group(1).strip()
    except Exception:
        pass
    return ""


def generate_readme(project_info: dict, changes: dict, plan_summary: str) -> str:
    name = project_info["name"]
    desc = project_info.get("description") or f"{name} 项目"
    project_type = project_info.get("type", "unknown")

    if project_type == "nodejs":
        scripts      = project_info.get("scripts", {})
        dev_script   = next((k for k in scripts if "dev" in k), "dev")
        build_script = next((k for k in scripts if "build" in k), "build")
        install_cmd  = "npm install"
        dev_cmd      = f"npm run {dev_script}"
        build_cmd    = f"npm run {build_script}"
    elif project_type == "python":
        install_cmd = "pip install -r requirements.txt"
        dev_cmd     = "python main.py"
        build_cmd   = "python -m build"
    else:
        install_cmd = "# 根据项目类型选择安装命令"
        dev_cmd     = "# 根据项目类型选择启动命令"
        build_cmd   = "# 根据项目类型选择构建命令"

    deps          = ", ".join(project_info.get("dependencies", [])[:8]) or "见配置文件"
    structure     = "\n".join(project_info.get("structure", []))
    all_changed   = (changes["changed_files"] + changes["added_files"])[:10]
    changed_files = "\n".join(f"- {f}" for f in all_changed)
    plan_section  = f"\n本次开发说明：{plan_summary}\n" if plan_summary else ""

    return f"""# {name}

> {desc}
{plan_section}
## ✨ 功能特性

- 请根据实际功能补充

## 🛠️ 技术栈

{deps}

## 🚀 快速开始

### 安装依赖

```bash
{install_cmd}
```

### 启动开发服务

```bash
{dev_cmd}
```

### 构建

```bash
{build_cmd}
```

## 📁 项目结构

```
{structure}
```

## 📝 开发指南

### 代码规范

- 提交信息遵循 Conventional Commits 规范
- 代码变更须通过 Lint 和类型检查

### 提交规范

```
feat(scope): 新增功能
fix(scope): 修复问题
docs: 文档更新
chore: 构建/配置变更
```

## 📋 最近更新

{changed_files}

## 📄 许可证

MIT License

---

> 此 README 由 Claude Code 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


def write_readme(project_root: str, content: str) -> str:
    readme_path = os.path.join(project_root, "README.md")
    if os.path.exists(readme_path):
        backup_dir = os.path.join(project_root, ".claude", "readme_backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            with open(readme_path, encoding="utf-8") as f:
                old_content = f.read()
            with open(os.path.join(backup_dir, f"README_{ts}.md"), "w", encoding="utf-8") as f:
                f.write(old_content)
        except Exception:
            pass

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    return readme_path


def session_had_plan(session_id: str, project_root: str) -> bool:
    cf = os.path.join(project_root, ".claude", "plan_cache.json")
    try:
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                cache = json.load(f)
            return cache.get(session_id) is True
    except Exception:
        pass
    return False


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            data = {}

        session_id  = data.get("session_id", "unknown")
        stop_reason = data.get("stop_reason", "")

        if stop_reason not in ("end_turn", "stop_sequence", ""):
            sys.exit(0)

        project_root = find_project_root()
        if not project_root:
            sys.exit(0)

        if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
            sys.exit(0)

        if not session_had_plan(session_id, project_root):
            sys.exit(0)

        changes = get_git_changes(project_root)
        if not has_significant_changes(changes):
            sys.exit(0)

        plan_summary = read_latest_plan(project_root)
        project_info = read_project_info(project_root)

        try:
            readme_content = generate_readme(project_info, changes, plan_summary)
            readme_path    = write_readme(project_root, readme_content)
        except Exception:
            sys.exit(0)

        result = {
            "reason": (
                f"✅ README.md 已自动更新：{readme_path}\n"
                f"📊 本次变更：{changes['summary']}\n"
                f"旧版已备份至 .claude/readme_backups/"
            )
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
