#!/usr/bin/env python3
"""Validate ~/.claude configuration against v2 PRIMARY design."""
import json
import os
import shutil
import sys

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.join(os.environ.get("USERPROFILE", ""), ".claude")
ERRORS = []
WARNINGS = []

CORE_AGENTS = {
    "planner", "code-explorer", "code-reviewer", "build-error-resolver",
    "architect", "spec-reviewer", "context-manager", "agentic-orchestrator",
}
CORE_SKILLS = {
    "using-superpowers", "brainstorming", "writing-plans", "executing-plans",
    "verification-before-completion", "systematic-debugging", "test-driven-development",
    "subagent-driven-development", "using-git-worktrees", "receiving-code-review",
    "requesting-code-review", "finishing-a-development-branch", "writing-skills",
    "memory-compression", "spec-validation", "karpathy-guidelines", "caveman-compress",
}
GLOBAL_RULES = {
    "CORE.md", "SECURITY.md", "GIT.md", "WORKFLOW.md",
    "AGENTS.md", "MCP.md", "DESIGN.md",
}


def check_json(path, label):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            json.load(fh)
    except Exception as exc:
        ERRORS.append(f"{label}: {exc}")


def main():
    if not os.path.isdir(BASE):
        ERRORS.append(f"Base dir missing: {BASE}")
        report()
        return 1

    for fname in ("settings.json", ".mcp.json", "config.json", ".claude.json"):
        check_json(os.path.join(BASE, fname), fname)

    agents_dir = os.path.join(BASE, "agents")
    agent_names = {
        f.replace(".md", "")
        for f in os.listdir(agents_dir)
        if f.endswith(".md") and f != "README.md"
    }
    missing_agents = CORE_AGENTS - agent_names
    if missing_agents:
        ERRORS.append(f"Missing core agents: {sorted(missing_agents)}")
    if len(agent_names) > 15:
        ERRORS.append(f"Too many agents: {len(agent_names)} > 15")

    skills_dir = os.path.join(BASE, "skills")
    skill_names = {
        d for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d)) and d != "README.md"
    }
    missing_skills = CORE_SKILLS - skill_names
    if missing_skills:
        ERRORS.append(f"Missing core skills: {sorted(missing_skills)}")
    if len(skill_names) > 20:
        ERRORS.append(f"Too many global skills: {len(skill_names)} > 20")

    rules_dir = os.path.join(BASE, "rules")
    rule_files = {f for f in os.listdir(rules_dir) if f.endswith(".md") and f != "README.md"}
    missing_rules = GLOBAL_RULES - rule_files
    if missing_rules:
        ERRORS.append(f"Missing global rules: {sorted(missing_rules)}")
    stale = {f for f in rule_files if f.startswith("RULES_")}
    if stale:
        ERRORS.append(f"Stale RULES_* files remain: {sorted(stale)}")

    claude_path = os.path.join(BASE, "CLAUDE.md")
    if os.path.exists(claude_path):
        with open(claude_path, "r", encoding="utf-8") as fh:
            claude_md = fh.read()
        line_count = claude_md.count("\n") + 1
        if line_count > 200:
            ERRORS.append(f"CLAUDE.md too long: {line_count} lines > 200")
        if "mcp0_" in claude_md or "mcp1_" in claude_md:
            ERRORS.append("CLAUDE.md has hardcoded mcp0/mcp1 prefixes")
    else:
        ERRORS.append("CLAUDE.md missing")

    manifest_path = os.path.join(BASE, "MANIFEST.yaml")
    if not os.path.exists(manifest_path):
        ERRORS.append("MANIFEST.yaml missing")
    elif yaml:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh)
        if not manifest.get("concerns"):
            WARNINGS.append("MANIFEST.yaml has no concerns")

    for tpl in (
        "templates/openspec/proposal.md",
        "templates/planning/phase-SPEC.md",
        "templates/spec/spec.md",
        "templates/DESIGN.md",
    ):
        if not os.path.exists(os.path.join(BASE, tpl.replace("/", os.sep))):
            WARNINGS.append(f"Missing template: {tpl}")

    for cfg in ("mcp-configs/core.json", "mcp-configs/dev.json", "mcp-configs/ops.json"):
        if not os.path.exists(os.path.join(BASE, cfg.replace("/", os.sep))):
            WARNINGS.append(f"Missing: {cfg}")

    rtk_exe = os.path.join(os.environ.get("USERPROFILE", ""), ".local", "bin", "rtk.exe")
    rtk_found = os.path.isfile(rtk_exe) or shutil.which("rtk")
    if not rtk_found:
        WARNINGS.append("RTK not installed (~/.local/bin/rtk.exe)")
    elif not os.path.exists(os.path.join(BASE, "RTK.md")):
        WARNINGS.append("RTK.md missing (run: rtk init -g --no-patch)")

    settings_path = os.path.join(BASE, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as fh:
            settings_text = fh.read()
        if rtk_found and "pre-rtk-rewrite" not in settings_text:
            ERRORS.append("pre-rtk-rewrite hook not registered in settings.json")
        if "pre-task-planner" in settings_text:
            ERRORS.append("pre-task-planner hook conflicts with writing-plans — remove from settings.json")
        for required_hook in (
            "session-start-bootstrap",
            "pre-compact-state",
            "stop-quality-gate",
            "stop-pattern-extraction",
        ):
            if required_hook not in settings_text:
                ERRORS.append(f"Required hook not registered: {required_hook}")
        if '"claude-mem@thedotmack": true' not in settings_text.replace(" ", ""):
            if "claude-mem@thedotmack" not in settings_text:
                WARNINGS.append("claude-mem plugin not enabled in settings.json")

    catalog_skills = os.path.join(BASE, "catalog", "skills")
    if os.path.isdir(catalog_skills):
        catalog_count = len(
            [d for d in os.listdir(catalog_skills) if os.path.isdir(os.path.join(catalog_skills, d))]
        )
        if catalog_count < 50:
            WARNINGS.append(f"catalog/skills count low: {catalog_count}")

    report(
        agents=len(agent_names),
        skills=len(skill_names),
        rules=len(rule_files),
        claude_lines=line_count if os.path.exists(claude_path) else 0,
    )
    return 1 if ERRORS else 0


def report(agents=0, skills=0, rules=0, claude_lines=0):
    print("=== .claude v2 VALIDATION ===")
    print(f"Agents: {agents} (max 15, core 8)")
    print(f"Skills: {skills} (max 20)")
    print(f"Rules:  {rules} (global 7 + README)")
    print(f"CLAUDE.md lines: {claude_lines} (max 200)")
    print()
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  ~ {w}")
    if ERRORS:
        print(f"ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"  x {e}")
    else:
        print("ALL CHECKS PASSED")


if __name__ == "__main__":
    sys.exit(main())
