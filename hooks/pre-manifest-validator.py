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
import time
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
    "skill/claude-to-deerflow": "deer_flow_bridge",  # v11 降级 catalog，映射保留

    "skill/git-workflow": "git_workflow",
    "skill/pr-workflow": "pr_workflow",
    "skill/claude-mem-maintenance": "claude_mem_maintenance",
    "skill/autoplan": "autoplan",
    "skill/ship": "ship_pipeline",
    "skill/office-hours": "office_hours",  # v11 降级 catalog，映射保留
    # Supplement（v11: context-engineering 已删；catalog 降级技能保留映射——项目内复制启用时仍受归属校验）
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
    "skill/skill-creator": "planning",  # v11: writing-skills 并入 skill-creator
    "skill/structured-artifacts": "gsd_context",
    # Agents — 核心 7
    "agent/planner": "planning",
    "agent/build-error-resolver": "debugging",
    "agent/spec-reviewer": "spec_review",
    "agent/agentic-orchestrator": "multi_agent",
    # Agents — gstack 审查 (6)
    "agent/eng-reviewer": "gstack_eng",
    "agent/ceo-reviewer": "gstack_ceo",
    "agent/designer": "gstack_designer",
    "agent/dx-reviewer": "gstack_dx",
    "agent/qa": "gstack_qa",
    "agent/security-reviewer": "gstack_security",
    # Agents — gstack 补全 + 低频变体（v12：sre/doc-writer 已删，映射仅防回潮拷贝）
    "agent/sre": "gstack_sre",
    "agent/doc-writer": "gstack_eng",
    "agent/codex-reviewer": "gstack_codex",
    "agent/performance-engineer": "gstack_eng",
    "agent/design-shotgun": "design_pipeline",
    "agent/pair-agent": "agentic_orchestrator",
    "agent/land-and-deploy": "land_and_deploy",
    "agent/ios-specialist": "gstack_ios",
    # MCP
    "mcp/codegraph": "code_exploration",
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
    "code-review": "requesting-code-review + eng-reviewer 已覆盖",
}


def load_stdin() -> dict:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


# ── 会话状态：excludes 语义 = 同会话互博边界（非全局禁用）────────────────────
# MANIFEST 注释自证：design_pipeline excludes brainstorming 但注记「不互博」；
# autoplan 注记「先 brainstorming…autoplan 在 verify 阶段」。
# 正确语义：本会话已用 concern X，则 excludes[X] 中的实体后续禁用（exit 2）。
STATE_DIR = Path.home() / ".claude" / ".state"
STATE_FILE = STATE_DIR / "manifest-validator.json"
STALE_SECONDS = 7 * 24 * 3600


def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"pre-manifest-validator: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"pre-manifest-validator: state write failed: {e}", file=sys.stderr)


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

    # 会话感知检查：当前实体被本会话「已使用 concern」的 excludes 排除才阻断
    session_id = str(data.get("session_id") or "unknown")
    state = load_state()
    used_concerns = set(state.get(session_id, {}).get("used_concerns", []))

    excludes = load_excludes()
    for blocking_concern in used_concerns:
        blocked_entities = excludes.get(blocking_concern, set())
        if current_entity in blocked_entities:
            print(
                json.dumps({
                    "continue": False,
                    "reason": (
                        f"[MANIFEST] {current_entity} 与本会话已使用的 {blocking_concern} 互博。"
                        f"冲突实体: {blocked_entities}. 请使用 MANIFEST.yaml 指定的 owner。"
                    ),
                })
            )
            sys.exit(2)  # block

    # 放行并记录本会话已用 concern
    if concern:
        used_concerns.add(concern)
        state[session_id] = {"used_concerns": sorted(used_concerns), "ts": time.time()}
        save_state(state)
    sys.exit(0)


if __name__ == "__main__":
    main()
