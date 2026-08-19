#!/usr/bin/env python3
"""门控注入文本读取器（v11.3.4）。SSOT: hooks/_lib/gate_messages.md。"""
from __future__ import annotations

import sys
from pathlib import Path

SECTIONS = {
    "p0": ("## P0分类门", "## 完成验证门"),
    "verify": ("## 完成验证门", "## 变更影响门"),
    "impact": ("## 变更影响门", "## 初次修改验收门"),
    "first_edit": ("## 初次修改验收门", None),
}

FALLBACKS = {
    "p0": (
        "【门控 · 会话开始必做】\n"
        "Read ~/.claude/skills/task-triage/SKILL.md，输出分类契约后按使用类型路由。"
    ),
    "verify": (
        "【门控 · 完成前必做】\n"
        "Read ~/.claude/skills/verification-before-completion/SKILL.md，"
        "贴出验证证据并输出 R20（漏改含文档/无文档影响，原功能含证据；"
        "核对范围=影响面全部相关项）后方可声称完成。"
    ),
    "impact": (
        "【门控 · 每个文件首次编辑前必做】\n"
        "1. codegraph_explore 目标 blast-radius；2. Grep 全项目引用；"
        "3. 配置类改动查 MANIFEST depends_on。范围不明不修改。"
    ),
    "first_edit": (
        "【门控 · 每个文件首次编辑后必做】\n"
        "对照本文件及其 blast-radius 全部相关项逐条核对："
        "需求 / 错改 / 漏改（文档或无文档影响）/ 原功能证据 / "
        "codegraph 或 Grep 残留=0。禁止只验当前文件、禁止「应该没影响」。"
    ),
}


def load_gate(name: str, claude_home: str | Path | None = None) -> str:
    """读取指定门控段；失败返回内置兜底（R16 不静默，stderr 留痕）。"""
    fallback = FALLBACKS[name]
    start_mark, end_mark = SECTIONS[name]
    if claude_home is None:
        gate_file = Path(__file__).resolve().parent / "gate_messages.md"
    else:
        gate_file = Path(claude_home) / "hooks" / "_lib" / "gate_messages.md"
    try:
        content = gate_file.read_text(encoding="utf-8")
        start = content.index(start_mark) + len(start_mark)
        end = content.index(end_mark) if end_mark else len(content)
        section = content[start:end].strip()
        return section if section else fallback
    except (OSError, ValueError) as e:
        print(f"gate_reader: read {name} failed: {e}", file=sys.stderr)
        return fallback
