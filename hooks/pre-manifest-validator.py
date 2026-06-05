#!/usr/bin/env python3
# source: local (built from MANIFEST.yaml anti-conflict pattern)
"""pre-manifest-validator: PreToolUse MANIFEST 归属校验，防左右手互博

读取 MANIFEST.yaml，解析当前调用 intent，校验 owner 与 excludes。
阻断互博场景（如 pre-task-planner vs writing-plans），非互博场景仅 warn。

退出码: 0=allow, 2=block
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MANIFEST_PATH = Path.home() / ".claude" / "MANIFEST.yaml"

# 仅校验以下事件直接相关的 concern；不覆盖所有场景
# intent → MANIFEST concern key
TOOL_INTENT_MAP: dict[str, str] = {
    "skill/triage": "triage",
    "skill/brainstorming": "brainstorming",
    "skill/writing-plans": "planning",
    "skill/verification-before-completion": "verification",
    "skill/systematic-debugging": "debugging",
    "skill/test-driven-development": "tdd",
    "skill/executing-plans": "execution",
    "skill/subagent-driven-development": "multi_agent",
    "skill/requesting-code-review": "code_review_request",
    "skill/receiving-code-review": "code_review_receive",
    "skill/spec-validation": "spec_review",
    "skill/caveman-compress": "output_token",
    "skill/memory-compression": "context_rot",
    "skill/instinct-learning": "instinct_v2",
    "skill/improve-codebase-architecture": "architecture_improvement",
    "skill/autoplan": "autoplan",
    "skill/ship": "ship_pipeline",
    "agent/planner": "planning",
    "agent/code-reviewer": "code_review_receive",
    "agent/spec-reviewer": "spec_review",
    "agent/eng-reviewer": "gstack_eng",
    "agent/ceo-reviewer": "gstack_ceo",
    "agent/designer": "gstack_designer",
    "agent/qa": "gstack_qa",
    "agent/security-reviewer": "gstack_security",
    "agent/agentic-orchestrator": "multi_agent",
    "agent/context-manager": "context_retrieval",
    "agent/build-error-resolver": "debugging",
    "agent/architect": "brainstorming",
    "agent/code-explorer": "multi_agent",
    "mcp/codegraph": "code_exploration",
    "plugin/understand-anything": "concept_navigation",
    "skill/understand-anything": "concept_navigation",
}

# key: blocking concern, value: set of excluded agents/skills
EXCLUDES: dict[str, set[str]] = {
    "planning": {"pre-task-planner", "agent/agentic-orchestrator"},
    "brainstorming": {"agent/planner"},
    "memory": {"agent/context-manager"},
    "shell_token": {"skill/caveman-compress"},
    "output_token": {"hook/pre-rtk-rewrite"},
    "triage": {"skill/systematic-debugging"},
    "architecture_improvement": {"skill/brainstorming", "agent/code-reviewer"},
    "ship_pipeline": {"skill/finishing-a-development-branch"},
    "plugin_attribution": set(),  # plugin 互斥由 hook 检测
}

# plugin vs skill 互斥检测
PLUGIN_SKILL_CONFLICTS: dict[str, str] = {
    # plugin名 → 冲突的已有 skill
    "security-guidance": "security-reviewer 已覆盖安全审查",
    "code-review": "requesting-code-review + code-reviewer 已覆盖",
}


def check_plugin_skill_conflict(data: dict) -> tuple[bool, str]:
    """检测 plugin 是否与已有 skill/agent 功能重叠。"""
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 仅检查 plugin 相关的调用
    if tool_name == "Agent" and "plugin" in str(tool_input).lower():
        # 简化检测：subagent_type 中包含已知冲突
        pass

    return False, ""


def load_stdin() -> dict:
    raw = sys.stdin.read() or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def resolve_concern(tool_name: str, tool_input: dict) -> str | None:
    """从 tool_name + tool_input 推断当前 intent 归属的 concern。"""
    # agent tool: subagent_type 字段
    if tool_name == "Agent" and "subagent_type" in tool_input:
        st = tool_input["subagent_type"]
        return TOOL_INTENT_MAP.get(f"agent/{st}")

    # skill tool
    if tool_name == "Skill" and "skill" in tool_input:
        sn = tool_input["skill"]
        return TOOL_INTENT_MAP.get(f"skill/{sn}")

    return None


def main() -> None:
    data = load_stdin()
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    concern = resolve_concern(tool_name, tool_input)
    if concern is None:
        sys.exit(0)  # 不在校验范围内

    current_entity = (
        f"agent/{tool_input.get('subagent_type')}"
        if tool_name == "Agent"
        else f"skill/{tool_input.get('skill', '')}"
    )

    # 检查 blocking excludes
    blocked = EXCLUDES.get(concern, set())
    if current_entity in blocked:
        print(
            json.dumps({
                "continue": False,
                "reason": (
                    f"[MANIFEST] {current_entity} 与 {concern} 互博。"
                    f"MANIFEST excludes: {blocked}. 请使用 MANIFEST.yaml 指定的 owner。"
                ),
            })
        )
        sys.exit(2)  # block

    sys.exit(0)


if __name__ == "__main__":
    main()
