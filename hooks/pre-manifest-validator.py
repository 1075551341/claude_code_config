#!/usr/bin/env python3
# source: local (built from MANIFEST.yaml anti-conflict pattern)
"""pre-manifest-validator: PreToolUse MANIFEST 归属校验，防左右手互博

读取 MANIFEST.yaml，解析当前调用 intent，校验 owner 与 excludes。
阻断互博场景，非互博场景放行。
v10.2: TOOL_INTENT_MAP 全覆盖 63 skills+agents + excludes 动态读取 MANIFEST

退出码: 0=allow, 2=block
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MANIFEST_PATH = Path.home() / ".claude" / "MANIFEST.yaml"

# intent → MANIFEST concern key — 全覆盖 63 skills+agents（v10.2）
TOOL_INTENT_MAP: dict[str, str] = {
    # P0 路由集 (5)
    "skill/using-superpowers": "bootstrap",
    "skill/change-impact-analysis": "change_impact",
    "skill/brainstorming": "brainstorming",
    "skill/verification-before-completion": "verification",
    "skill/systematic-debugging": "debugging",
    # L2 门控 (8)
    "skill/writing-plans": "planning",
    "skill/spec-validation": "spec_review",
    "skill/executing-plans": "execution",
    "skill/subagent-driven-development": "multi_agent",
    "skill/test-driven-development": "tdd",
    "skill/requesting-code-review": "code_review_request",
    "skill/receiving-code-review": "code_review_receive",
    "skill/triage": "triage",
    # L3 信号 (10)
    "skill/deep-research": "deep_research",
    "skill/adr-management": "adr",
    "skill/workstream-management": "workstreams",
    "skill/claude-to-deerflow": "deer_flow_bridge",
    "skill/git-workflow": "git_workflow",
    "skill/pr-workflow": "pr_workflow",
    "skill/claude-mem-maintenance": "claude_mem_maintenance",
    "skill/autoplan": "autoplan",
    "skill/ship": "ship_pipeline",
    "skill/office-hours": "office_hours",
    # Supplement (14)
    "skill/understand-anything": "concept_navigation",
    "skill/context-engineering": "context_engineering",
    "skill/memory-compression": "context_rot",
    "skill/caveman-compress": "output_token",
    "skill/instinct-learning": "instinct_v2",
    "skill/improve-codebase-architecture": "architecture_improvement",
    "skill/design-pipeline": "design_pipeline",
    "skill/taste-memory": "taste_memory",
    "skill/browser-qa": "gstack_qa",
    "skill/onboarding-guide": "onboarding",
    "skill/karpathy-guidelines": "coding_philosophy",
    "skill/finishing-a-development-branch": "ship_pipeline",
    "skill/using-git-worktrees": "workstreams",
    "skill/writing-skills": "planning",
    "skill/structured-artifacts": "gsd_context",
    # Agents — 核心 7
    "agent/planner": "planning",
    "agent/code-explorer": "multi_agent",
    "agent/code-reviewer": "code_review_receive",
    "agent/build-error-resolver": "debugging",
    "agent/architect": "brainstorming",
    "agent/spec-reviewer": "spec_review",
    "agent/agentic-orchestrator": "multi_agent",
    # Agents — gstack 审查 (6)
    "agent/eng-reviewer": "gstack_eng",
    "agent/ceo-reviewer": "gstack_ceo",
    "agent/designer": "gstack_designer",
    "agent/dx-reviewer": "gstack_dx",
    "agent/qa": "gstack_qa",
    "agent/security-reviewer": "gstack_security",
    # Agents — gstack 补全 + v0.19 (9)
    "agent/cso": "gstack_cso",
    "agent/sre": "gstack_sre",
    "agent/release-engineer": "land_and_deploy",
    "agent/product-manager": "office_hours",
    "agent/design-engineer": "gstack_designer",
    "agent/performance-engineer": "gstack_eng",
    "agent/doc-writer": "gstack_eng",
    "agent/design-shotgun": "design_pipeline",
    "agent/pair-agent": "agentic_orchestrator",
    "agent/land-and-deploy": "land_and_deploy",
    "agent/ios-specialist": "gstack_ios",
    "agent/codex-reviewer": "gstack_codex",
    # MCP
    "mcp/codegraph": "code_exploration",
    "plugin/understand-anything": "concept_navigation",
}

# 动态 excludes 缓存
_EXCLUDES_CACHE: dict[str, set[str]] | None = None
_MANIFEST_MTIME: float = 0.0


def load_excludes():
    """动态读取 MANIFEST.yaml concerns.*.excludes，mtime 缓存"""
    global _EXCLUDES_CACHE, _MANIFEST_MTIME
    try:
        mtime = os.path.getmtime(str(MANIFEST_PATH))
        if _EXCLUDES_CACHE is not None and mtime == _MANIFEST_MTIME:
            return _EXCLUDES_CACHE

        import yaml
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        excludes = {}
        for name, concern in manifest.get("concerns", {}).items():
            if isinstance(concern, dict) and "excludes" in concern:
                excludes[name] = set(concern["excludes"])

        _EXCLUDES_CACHE = excludes
        _MANIFEST_MTIME = mtime
        return excludes
    except ImportError:
        print("pre-manifest-validator: PyYAML not installed — security gate disabled. "
              "Install: pip install pyyaml", file=sys.stderr)
        _EXCLUDES_CACHE = None
        return {}
    except (FileNotFoundError, OSError) as e:
        print(f"pre-manifest-validator: MANIFEST read failed: {e}", file=sys.stderr)
        _EXCLUDES_CACHE = None  # clear stale cache on file access errors
        return {}


# plugin vs skill 互斥检测
PLUGIN_SKILL_CONFLICTS: dict[str, str] = {
    "security-guidance": "security-reviewer 已覆盖安全审查",
    "code-review": "requesting-code-review + code-reviewer 已覆盖",
}


def load_stdin() -> dict:
    raw = sys.stdin.read() or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def resolve_concern(tool_name: str, tool_input: dict) -> str | None:
    """从 tool_name + tool_input 推断当前 intent 归属的 concern。"""
    if tool_name == "Agent" and "subagent_type" in tool_input:
        st = tool_input["subagent_type"]
        return TOOL_INTENT_MAP.get(f"agent/{st}")

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

    # 双向检查：被调实体是否被任何 concern 的 excludes 排除
    excludes = load_excludes()
    for blocking_concern, blocked_entities in excludes.items():
        if current_entity in blocked_entities:
            print(
                json.dumps({
                    "continue": False,
                    "reason": (
                        f"[MANIFEST] {current_entity} 被 {blocking_concern} 排除。"
                        f"冲突实体: {blocked_entities}. 请使用 MANIFEST.yaml 指定的 owner。"
                    ),
                })
            )
            sys.exit(2)  # block

    sys.exit(0)


if __name__ == "__main__":
    main()
