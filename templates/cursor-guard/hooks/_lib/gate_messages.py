#!/usr/bin/env python3
"""门控注入文本读取器（v11.3.4）。优先 Claude 侧 gate_reader，失败则本地兜底。"""
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
        "有未验证编辑时才执行（仅 Claude Stop / 人工 Read；Cursor 不注入本段）。\n"
        "贴观察输出；R20 六行（满足须承认/反驳/弃权；漏改含文档或无文档影响；"
        "原功能含证据；影响范围含 CRG/IMPACT/blast）。\n"
        "有代码改动：change-implementer 修改后 eng-reviewer 只找问题。"
        "干净 PASS 即停。审查一次找齐后清单齐再集中改；每轮全新开审（禁止 resume），最多 3 轮；禁止边审边改、禁止审查者改文件。"
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
        "codegraph 或 Grep 残留=0。禁止只验当前文件。"
    ),
}


def _local_load(name: str, claude_home: Path) -> str:
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


def load_gate(name: str, claude_home: Path) -> str:
    """读取指定门控段；优先 Claude hooks/_lib/gate_reader.py。"""
    try:
        from hook_io import import_claude_lib

        reader = import_claude_lib(claude_home, "gate_reader")
        return reader.load_gate(name, claude_home)
    except Exception as e:
        print(f"gate_messages: gate_reader unavailable, local fallback: {e}", file=sys.stderr)
        return _local_load(name, claude_home)
