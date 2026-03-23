#!/usr/bin/env python3
"""
PreToolUse Hook: 复杂任务计划生成器
检测到复杂任务时自动生成计划文档到项目 .claude/plans/ 目录
使用本地模板生成（不依赖外部 API），确保零延迟
"""
import json
import sys
import io
import os
import re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))

PLAN_DIR_NAME = ".claude/plans"

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
    "认证", "auth", "鉴权",
    "websocket", "实时", "realtime",
]

SKIP_KEYWORDS = [
    "查看", "查询", "check", "list", "show", "view",
    "状态", "status", "ping", "test connection",
    "格式化", "format", "lint",
    "git status", "git log", "git diff",
    "安装", "install", "版本", "version",
    "帮助", "help", "说明", "explain",
]


def is_complex_task(command: str, description: str = "") -> bool:
    """判断是否为需要生成计划的复杂任务"""
    text = (command + " " + description).lower()
    for kw in SKIP_KEYWORDS:
        if kw.lower() in text:
            return False
    for kw in COMPLEX_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def find_project_root(start_path: str = None) -> str:
    """查找项目根目录"""
    if start_path is None:
        start_path = os.getcwd()
    directory = os.path.abspath(start_path)
    for _ in range(8):
        markers = [
            "package.json", "pyproject.toml", "Cargo.toml",
            ".git", "go.mod", "pom.xml", "build.gradle",
        ]
        if any(os.path.exists(os.path.join(directory, m)) for m in markers):
            return directory
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return os.getcwd()


def generate_plan(task_description: str) -> dict:
    """根据任务描述生成本地计划模板（零延迟，不调用外部 API）"""
    title = task_description[:30].strip()

    text_lower = task_description.lower()
    steps = ["分析现有代码结构和相关文件"]

    if any(kw in text_lower for kw in ["前端", "frontend", "组件", "component", "页面", "page"]):
        steps.extend([
            "设计组件结构和数据流",
            "实现核心组件逻辑",
            "添加样式和响应式适配",
            "编写组件测试",
        ])
    elif any(kw in text_lower for kw in ["后端", "backend", "api", "接口", "服务"]):
        steps.extend([
            "设计 API 路由和数据模型",
            "实现核心业务逻辑",
            "添加参数校验和错误处理",
            "编写接口测试",
        ])
    elif any(kw in text_lower for kw in ["数据库", "database", "迁移", "migration"]):
        steps.extend([
            "设计表结构和索引策略",
            "编写 Migration 脚本（支持回滚）",
            "验证数据完整性",
            "更新 ORM 模型",
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
            "README.md 已更新",
        ],
    }


def format_plan_doc(plan: dict, trigger: str, session_id: str) -> str:
    """格式化计划文档"""
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
    """保存计划文档到项目目录"""
    plan_dir = os.path.join(project_root, PLAN_DIR_NAME)
    os.makedirs(plan_dir, exist_ok=True)

    safe_title = re.sub(r'[^\w\u4e00-\u9fff-]', '_', title)[:30]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{safe_title}.md"
    filepath = os.path.join(plan_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    latest = os.path.join(plan_dir, "latest.md")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def get_task_description(data: dict) -> str:
    """从 hook 数据中提取任务描述"""
    tool_input = data.get("tool_input", {})
    tool_name = data.get("tool_name", "")

    if tool_name == "Bash":
        return tool_input.get("command", "")
    elif tool_name in ("Write", "Edit"):
        return f"编辑文件 {tool_input.get('file_path', '')}"
    elif tool_name == "Task":
        return tool_input.get("description", "")
    return ""


def get_cache_file(project_root: str) -> str:
    """缓存文件存放在项目的 .claude/ 目录下"""
    return os.path.join(project_root, ".claude", "plan_cache.json")


def load_cache(project_root: str) -> dict:
    cache_file = get_cache_file(project_root)
    try:
        if os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_cache(project_root: str, cache: dict):
    cache_file = get_cache_file(project_root)
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        keys = list(cache.keys())
        if len(keys) > 50:
            for k in keys[:len(keys) - 50]:
                del cache[k]
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass


def is_global_config_dir(path: str) -> bool:
    """判断是否为全局 ~/.claude/ 配置目录，避免污染"""
    return os.path.normpath(path) == GLOBAL_CLAUDE_DIR


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    session_id = data.get("session_id", "unknown")

    if tool_name not in ("Task", "Bash", "Write", "Edit"):
        sys.exit(0)

    project_root = find_project_root()

    if is_global_config_dir(project_root):
        sys.exit(0)

    cache = load_cache(project_root)
    if cache.get(session_id):
        sys.exit(0)

    task_desc = get_task_description(data)
    if not task_desc or not is_complex_task(task_desc):
        sys.exit(0)

    cache[session_id] = True
    save_cache(project_root, cache)

    plan = generate_plan(task_desc)
    content = format_plan_doc(plan, task_desc, session_id)
    plan_path = save_plan(content, plan.get("title", "task"), project_root)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"任务计划已自动生成：{plan_path}\n\n"
                f"**计划概要**\n{plan.get('analysis', '')}\n\n"
                f"**实施步骤**\n"
                + "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan.get("steps", [])))
                + "\n\n请按此计划执行，完成后运行测试并更新 README。"
            ),
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
