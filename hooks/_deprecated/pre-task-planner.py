#!/usr/bin/env python3
"""
PreToolUse Hook: 复杂任务计划生成器

功能：检测到复杂任务时自动生成计划文档到项目 .claude/plans/ 目录
触发：Task / Bash 工具（Write 工具直接放行）

修复记录：
- v1.1: Write 工具直接放行，避免 hook error
"""
import json
import sys
import io
import os
import re
from datetime import datetime

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
PLAN_DIR_NAME = os.path.join(".claude", "plans")

COMPLEX_KEYWORDS = [
    "重构", "refactor", "迁移", "migrate", "migration",
    "架构", "architecture", "设计", "design",
    "新功能", "feature", "implement", "实现",
    "接入", "集成", "integrate", "integration",
    "优化", "optimize", "performance",
    "开发", "develop", "build", "create",
    "模块", "module", "系统", "system",
    "项目", "project", "全栈", "fullstack",
    "部署", "deploy", "容器", "docker",
    "数据库", "database", "schema",
    "认证", "auth", "鉴权", "permission",
    "websocket", "实时", "realtime",
    "爬虫", "scraper", "crawler",
    "算法", "algorithm",
]

SKIP_KEYWORDS = [
    "查看", "查询", "check", "list", "show", "view",
    "状态", "status", "ping", "test connection",
    "格式化", "format", "lint",
    "git status", "git log", "git diff", "git pull",
    "安装", "install", "版本", "version",
    "帮助", "help", "说明", "explain",
    "echo ", "cat ", "ls ", "pwd", "whoami",
]


def is_complex_task(text: str) -> bool:
    lower = text.lower()
    for kw in SKIP_KEYWORDS:
        if kw.lower() in lower:
            return False
    for kw in COMPLEX_KEYWORDS:
        if kw.lower() in lower:
            return True
    return False


def find_project_root(start_path: str = None) -> str:
    try:
        directory = os.path.abspath(start_path or os.getcwd())
        markers = ["package.json", "pyproject.toml", "Cargo.toml",
                   ".git", "go.mod", "pom.xml", "build.gradle"]
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


def generate_plan(task_description: str) -> dict:
    title = task_description[:30].strip()
    text_lower = task_description.lower()
    steps = ["分析现有代码结构和相关文件"]

    if any(kw in text_lower for kw in ["前端", "frontend", "组件", "component", "页面", "page", "ui"]):
        steps.extend([
            "设计组件结构和数据流",
            "实现核心组件逻辑",
            "添加样式和响应式适配",
            "编写组件测试",
        ])
    elif any(kw in text_lower for kw in ["后端", "backend", "api", "接口", "服务", "server"]):
        steps.extend([
            "设计 API 路由和数据模型",
            "实现核心业务逻辑",
            "添加参数校验和错误处理",
            "编写接口测试",
        ])
    elif any(kw in text_lower for kw in ["数据库", "database", "迁移", "migration", "schema"]):
        steps.extend([
            "设计表结构和索引策略",
            "编写 Migration 脚本（含回滚方案）",
            "验证数据完整性约束",
            "更新 ORM 模型和类型定义",
        ])
    elif any(kw in text_lower for kw in ["全栈", "fullstack", "项目", "project"]):
        steps.extend([
            "设计系统架构和技术选型",
            "搭建前后端项目骨架",
            "实现核心功能模块",
            "前后端联调和集成测试",
            "部署配置和文档完善",
        ])
    else:
        steps.extend([
            "设计技术方案，确认实现路径",
            "按模块逐步实现，每步完成后验证",
            "运行测试，修复发现的问题",
            "更新相关文档",
        ])

    return {
        "title": title,
        "analysis": f"任务：{task_description}\n\n需先确认任务范围、技术选型和预期产出。",
        "steps": steps,
        "risks": [
            "可能影响现有功能：实施前备份，实施后回归测试",
            "依赖变更：检查所有依赖方是否需要同步更新",
        ],
        "acceptance": [
            "功能按预期工作，无新增错误",
            "代码通过 Lint 和类型检查",
            "相关测试全部通过",
            "README.md 已更新（如有必要）",
        ],
    }


def format_plan_doc(plan: dict, trigger: str, session_id: str) -> str:
    steps_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan.get("steps", [])))
    risks_md = "\n".join(f"- {r}" for r in plan.get("risks", []))
    accept_md = "\n".join(f"- [ ] {a}" for a in plan.get("acceptance", []))

    return f"""# 任务计划：{plan.get('title', '未命名任务')}

**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**会话 ID**：{session_id[:8]}
**触发命令**：`{trigger[:100]}`

---

## 📋 任务分析

{plan.get('analysis', '')}

---

## 🎯 实施步骤

{steps_md}

---

## ⚠️ 风险与注意事项

{risks_md}

---

## ✅ 完成标准

{accept_md}

---

> 此文档由 Claude Code 自动生成，执行过程中会自动更新。
"""


def save_plan(content: str, title: str, project_root: str) -> str:
    plan_dir = os.path.join(project_root, PLAN_DIR_NAME)
    os.makedirs(plan_dir, exist_ok=True)
    safe_title = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', title)[:30]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(plan_dir, f"{ts}_{safe_title}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    latest = os.path.join(plan_dir, "latest.md")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def get_cache_file(project_root: str) -> str:
    return os.path.join(project_root, ".claude", "plan_cache.json")


def load_cache(project_root: str) -> dict:
    try:
        cf = get_cache_file(project_root)
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_cache(project_root: str, cache: dict):
    try:
        cf = get_cache_file(project_root)
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        keys = list(cache.keys())
        if len(keys) > 50:
            for k in keys[:len(keys) - 50]:
                del cache[k]
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass


def main():
    try:
        # ── Step 1: 读 stdin ───────────────────────────────────────────────
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        session_id = data.get("session_id", "unknown")

        # ── Step 2: 仅处理 Task/Bash，其他立即放行 ────────────────────────
        # FIX: Edit/Write 不触发计划，直接 exit(0)，彻底避免 hook error
        if tool_name not in ("Task", "Bash"):
            sys.exit(0)

        project_root = find_project_root()

        if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
            sys.exit(0)

        # ── Step 3: 会话计划缓存（防止重复生成）────────────────────────────
        cache = load_cache(project_root)
        if cache.get(session_id) is True:
            sys.exit(0)

        # ── Step 4: 任务复杂度判断 ────────────────────────────────────────
        tool_input = data.get("tool_input", {})
        if tool_name == "Bash":
            task_desc = tool_input.get("command", "")
        else:
            task_desc = tool_input.get("description", "")

        if not task_desc or not is_complex_task(task_desc):
            sys.exit(0)

        cache[session_id] = True
        save_cache(project_root, cache)

        # ── Step 5: 生成并保存计划 ────────────────────────────────────────
        try:
            plan = generate_plan(task_desc)
            content = format_plan_doc(plan, task_desc, session_id)
            plan_path = save_plan(content, plan.get("title", "task"), project_root)
        except Exception:
            sys.exit(0)

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    f"📋 任务计划已自动生成：{plan_path}\n\n"
                    f"**计划概要**\n{plan.get('analysis', '')}\n\n"
                    f"**实施步骤**\n"
                    + "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan.get("steps", [])))
                    + "\n\n请按此计划执行，完成后运行测试并更新 README。"
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
