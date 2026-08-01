#!/usr/bin/env python3
"""门控注入文本共享读取器（v10.13.0）。
SSOT: <claude_home>/hooks/_lib/gate_messages.md，Claude Code 与 Cursor Guard 双端共读。"""
from __future__ import annotations

import sys
from pathlib import Path

SECTIONS = {
    "p0": ("## P0分类门", "## 完成验证门"),
    "verify": ("## 完成验证门", "## 变更影响门"),
    "impact": ("## 变更影响门", None),
}

FALLBACKS = {
    "p0": (
        "【门控 · 会话开始必做】\n"
        "第一轮回复前必须按 task-triage 分类：Phase0 盘点 → "
        "[简单(关联需改≤2+白名单+六维全低+模型匹配+attempt=1) | "
        "非简单(需改>2/黑名单/六维含中高/模型不足/持续处理执行升档)]\n"
        "Read ~/.claude/skills/task-triage/SKILL.md 后按使用类型路由执行。"
    ),
    "verify": (
        "【门控 · 完成前必做】\n"
        "Read ~/.claude/skills/verification-before-completion/SKILL.md，"
        "实际运行验证命令并贴出证据后方可声称完成（R1）。"
    ),
    "impact": (
        "【门控 · 本会话首次编辑前必做】\n"
        "1. codegraph_explore 目标 blast-radius；2. Grep 全项目引用；"
        "3. 配置类改动查 MANIFEST depends_on。范围不明不修改。"
    ),
}


def load_gate(name: str, claude_home: Path) -> str:
    """读取指定门控段；失败返回内置兜底（R16 不静默，stderr 留痕）。"""
    fallback = FALLBACKS[name]
    start_mark, end_mark = SECTIONS[name]
    gate_file = Path(claude_home) / "hooks" / "_lib" / "gate_messages.md"
    try:
        content = gate_file.read_text(encoding="utf-8")
        start = content.index(start_mark) + len(start_mark)
        end = content.index(end_mark) if end_mark else len(content)
        section = content[start:end].strip()
        return section if section else fallback
    except (OSError, ValueError) as e:
        print(f"gate_messages: read {name} failed: {e}", file=sys.stderr)
        return fallback
