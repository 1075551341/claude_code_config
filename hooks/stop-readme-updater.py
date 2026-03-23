#!/usr/bin/env python3
"""
Stop Hook: README 自动生成/更新器
会话结束后分析项目变更，使用本地模板生成 README.md
仅在检测到实质性代码变更且当前会话有任务计划时触发
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
PLAN_DIR_NAME = ".claude/plans"


def run(cmd, cwd=None) -> tuple:
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30, cwd=cwd,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception:
        return -1, ""


def find_project_root(start: str = None):
    directory = os.path.abspath(start or os.getcwd())
    for _ in range(8):
        markers = [
            "package.json", "pyproject.toml", "Cargo.toml",
            ".git", "go.mod", "pom.xml",
        ]
        if any(os.path.exists(os.path.join(directory, m)) for m in markers):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def get_git_changes(project_root: str) -> dict:
    """获取 git 变更摘要"""
    result = {"changed_files": [], "added_files": [], "summary": ""}
    _, status = run("git status --short", cwd=project_root)
    if not status:
        return result
    for line in status.splitlines():
        if not line.strip():
            continue
        flag = line[:2].strip()
        path = line[3:].strip()
        if flag in ("A", "??"):
            result["added_files"].append(path)
        else:
            result["changed_files"].append(path)
    total = len(result["changed_files"]) + len(result["added_files"])
    result["summary"] = f"变更 {len(result['changed_files'])} 个文件，新增 {len(result['added_files'])} 个文件（共 {total} 个）"
    return result


def has_significant_changes(changes: dict) -> bool:
    """判断是否有实质性变更"""
    ignore_patterns = [
        r"\.log$", r"\.lock$", r"\.claude/", r"node_modules/",
        r"__pycache__", r"\.pyc$", r"dist/", r"build/",
        r"README\.md$",
    ]
    all_files = changes["changed_files"] + changes["added_files"]
    significant = [
        f for f in all_files
        if not any(re.search(p, f) for p in ignore_patterns)
    ]
    return len(significant) >= 2


def read_project_info(project_root: str) -> dict:
    """读取项目基础信息"""
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
            info["name"] = pkg.get("name", info["name"])
            info["description"] = pkg.get("description", "")
            info["type"] = "nodejs"
            info["scripts"] = pkg.get("scripts", {})
            info["dependencies"] = list(pkg.get("dependencies", {}).keys())[:12]
        except Exception:
            pass

    pyproject_path = os.path.join(project_root, "pyproject.toml")
    if os.path.exists(pyproject_path):
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
        for entry in os.scandir(project_root):
            if not entry.name.startswith(".") and entry.name not in (
                "node_modules", "__pycache__", "dist", "build", ".git",
            ):
                prefix = "📁 " if entry.is_dir() else "📄 "
                entries.append(prefix + entry.name)
        info["structure"] = sorted(entries)[:15]
    except Exception:
        pass

    return info


def read_latest_plan(project_root: str) -> str:
    """读取最新任务计划"""
    latest = os.path.join(project_root, PLAN_DIR_NAME, "latest.md")
    if os.path.exists(latest):
        try:
            with open(latest, encoding="utf-8") as f:
                content = f.read()
            match = re.search(r"## 📋 任务分析\n\n(.+?)(?=\n---|\n##)", content, re.DOTALL)
            if match:
                return match.group(1).strip()
        except Exception:
            pass
    return ""


def generate_readme(project_info: dict, changes: dict, plan_summary: str) -> str:
    """本地生成 README 内容"""
    name = project_info["name"]
    desc = project_info.get("description") or f"{name} 项目"
    project_type = project_info.get("type", "unknown")

    if project_type == "nodejs":
        scripts = project_info.get("scripts", {})
        install_cmd = "npm install"
        dev_cmd = f"npm run {next((k for k in scripts if 'dev' in k), 'dev')}"
        build_cmd = f"npm run {next((k for k in scripts if 'build' in k), 'build')}"
    elif project_type == "python":
        install_cmd = "pip install -r requirements.txt"
        dev_cmd = "python main.py"
        build_cmd = "python -m build"
    else:
        install_cmd = "# 请根据项目类型选择安装命令"
        dev_cmd = "# 请根据项目类型选择启动命令"
        build_cmd = "# 请根据项目类型选择构建命令"

    deps = ", ".join(project_info.get("dependencies", [])[:8]) or "见配置文件"
    structure = "\n".join(project_info.get("structure", []))
    changed_files = "\n".join(
        f"- {f}" for f in (changes["changed_files"] + changes["added_files"])[:10]
    )
    plan_section = f"\n本次开发说明：{plan_summary}\n" if plan_summary else ""

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

- TypeScript 项目禁止使用 `any`
- 提交信息遵循 Conventional Commits 规范

### 提交规范

```
feat(scope): 新增功能描述
fix(scope): 修复问题描述
docs: 文档更新
```

## 📋 最近更新

{changed_files}

## 📄 许可证

MIT License

---

> 此 README 由 Claude Code 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


def write_readme(project_root: str, content: str) -> str:
    """写入 README.md，备份旧版本"""
    readme_path = os.path.join(project_root, "README.md")

    if os.path.exists(readme_path):
        backup_dir = os.path.join(project_root, ".claude", "readme_backups")
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(readme_path, encoding="utf-8") as f:
            old_content = f.read()
        with open(os.path.join(backup_dir, f"README_{ts}.md"), "w", encoding="utf-8") as f:
            f.write(old_content)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    return readme_path


def session_had_plan(session_id: str, project_root: str) -> bool:
    """从项目级 plan_cache.json 检查该会话是否生成过计划"""
    cache_file = os.path.join(project_root, ".claude", "plan_cache.json")
    try:
        if os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as f:
                cache = json.load(f)
            return cache.get(session_id, False)
    except Exception:
        pass
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
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
    readme_content = generate_readme(project_info, changes, plan_summary)
    readme_path = write_readme(project_root, readme_content)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"✅ README.md 已自动更新：{readme_path}\n"
                f"📊 本次变更摘要：{changes['summary']}\n"
                f"旧版 README 已备份到 .claude/readme_backups/ 目录。"
            ),
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
