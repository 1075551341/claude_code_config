#!/usr/bin/env python3
"""门控注入文本读取器（v11.5.0）。SSOT: hooks/_lib/gate_messages.md。"""
from __future__ import annotations

import json
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
        "贴出验证证据并输出七维 R20（含问题是否解决）后方可声称完成。"
        "审查前刷图；全新只读独立审查最多 {{review_max_rounds}} 轮。"
    ),
    "impact": (
        "【门控 · 每个文件首次编辑前必做】\n"
        "1. 有 CRG 图：get_minimal_context + get_impact_radius（有 git diff 再 detect_changes）；"
        "叠加 codegraph_explore blast-radius；2. Grep 全项目引用；"
        "3. 配置类改动查 MANIFEST depends_on。范围不明不修改。"
    ),
    "first_edit": (
        "【门控 · 每个文件首次编辑后必做】\n"
        "对照本文件及其 blast-radius 全部相关项逐条核对："
        "需求 / 错改 / 漏改（文档或无文档影响）/ 原功能证据 / "
        "codegraph 或 Grep 残留=0。禁止只验当前文件、禁止「应该没影响」。"
    ),
}


def _review_max_rounds(claude_home: Path) -> int:
    path = claude_home / "config" / "quality_gates.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return int((data.get("verification_gate") or {}).get("review_max_rounds") or 5)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"gate_reader: review_max_rounds fallback 5: {exc}", file=sys.stderr)
        return 5


def fill_placeholders(text: str, claude_home: Path | None = None) -> str:
    home = claude_home or Path(__file__).resolve().parents[2]
    return (text or "").replace("{{review_max_rounds}}", str(_review_max_rounds(home)))


def load_gate(name: str, claude_home: str | Path | None = None) -> str:
    """读取指定门控段；失败返回内置兜底（R16 不静默，stderr 留痕）。"""
    fallback = FALLBACKS[name]
    start_mark, end_mark = SECTIONS[name]
    if claude_home is None:
        gate_dir = Path(__file__).resolve().parent
        home = gate_dir.parent.parent
        gate_file = gate_dir / "gate_messages.md"
    else:
        home = Path(claude_home)
        gate_file = home / "hooks" / "_lib" / "gate_messages.md"
    try:
        content = gate_file.read_text(encoding="utf-8")
        start = content.index(start_mark) + len(start_mark)
        end = content.index(end_mark) if end_mark else len(content)
        section = content[start:end].strip()
        raw = section if section else fallback
    except (OSError, ValueError) as e:
        print(f"gate_reader: read {name} failed: {e}", file=sys.stderr)
        raw = fallback
    return fill_placeholders(raw, home)
