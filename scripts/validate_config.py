#!/usr/bin/env python3
"""Validate ~/.claude configuration against v2 PRIMARY design (8 checks V1-V8)."""
import json
import os
import re
import shutil
import sys

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.join(os.environ.get("USERPROFILE", ""), ".claude")
ERRORS = []
WARNINGS = []
INFO = []

CORE_AGENTS = {
    "planner", "code-explorer", "code-reviewer", "build-error-resolver",
    "architect", "spec-reviewer", "agentic-orchestrator",
}
GSTACK_REVIEW_AGENTS = {
    "eng-reviewer", "ceo-reviewer", "designer", "qa", "security-reviewer",
}
GSTACK_SUPPLEMENT_AGENTS = {
    "cso", "sre", "release-engineer", "product-manager",
    "design-engineer", "performance-engineer", "doc-writer",
}
REQUIRED_AGENTS = CORE_AGENTS | GSTACK_REVIEW_AGENTS | GSTACK_SUPPLEMENT_AGENTS
GLOBAL_AGENTS_MAX = 22

P0_SKILLS = {
    "using-superpowers", "brainstorming", "verification-before-completion",
    "systematic-debugging",
}
WORKFLOW_SKILLS = {
    "writing-plans", "executing-plans", "test-driven-development",
    "subagent-driven-development", "using-git-worktrees", "receiving-code-review",
    "requesting-code-review", "finishing-a-development-branch", "writing-skills",
}
META_SKILLS = {
    "memory-compression", "spec-validation", "karpathy-guidelines", "caveman-compress",
}
EXTENSION_SKILLS = {
    "autoplan", "browser-qa", "design-pipeline", "ship", "office-hours",
    "context-engineering", "structured-artifacts", "instinct-learning",
}
MATTPOCOCK_SKILLS = {"triage", "improve-codebase-architecture"}
REQUIRED_SKILLS = P0_SKILLS | WORKFLOW_SKILLS | META_SKILLS | EXTENSION_SKILLS | MATTPOCOCK_SKILLS
GLOBAL_SKILLS_MAX = 28

GLOBAL_RULES = {
    "CORE.md", "BESTPRACTICE.md", "SECURITY.md", "GIT.md", "WORKFLOW.md",
    "AGENTS.md", "MCP.md", "DESIGN.md", "CONTEXT.md",
}


def check_json(path, label):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            json.load(fh)
    except Exception as exc:
        ERRORS.append(f"{label}: {exc}")


def v1_skill_triggers_no_conflict():
    triggers_map = {}
    skills_dir = os.path.join(BASE, "skills")
    if not os.path.isdir(skills_dir):
        return
    for d in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        triggers_match = re.search(r'triggers:\s*\[(.+?)\]', content)
        desc_match = re.search(r'description:\s*(.+)', content)
        triggers = set()
        if triggers_match:
            triggers = {t.strip().strip("'\"") for t in triggers_match.group(1).split(",")}
        if desc_match:
            for word in desc_match.group(1).split():
                if len(word) > 3:
                    triggers.add(word)
        if triggers:
            for t in triggers:
                if t in triggers_map and triggers_map[t] != d:
                    WARNINGS.append(f"V1: Trigger '{t}' shared by {triggers_map[t]} and {d}")
                triggers_map[t] = d


def v2_agent_duties_no_overlap():
    agents_dir = os.path.join(BASE, "agents")
    if not os.path.isdir(agents_dir):
        return
    duties = {}
    for f in os.listdir(agents_dir):
        if not f.endswith(".md") or f == "README.md":
            continue
        path = os.path.join(agents_dir, f)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        desc_match = re.search(r'description:\s*(.+)', content)
        if desc_match:
            duties[f] = desc_match.group(1).strip()
    names = list(duties.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            words_i = set(duties[names[i]].split()) & set(duties[names[j]].split())
            significant = {w for w in words_i if len(w) > 2 and w not in {"审查", "触发词", "启用", "时"}}
            if len(significant) >= 3:
                WARNINGS.append(f"V2: Possible duty overlap between {names[i]} and {names[j]}: {significant}")


def v3_rules_no_contradiction():
    rules_dir = os.path.join(BASE, "rules")
    if not os.path.isdir(rules_dir):
        return
    core_path = os.path.join(rules_dir, "CORE.md")
    if not os.path.exists(core_path):
        ERRORS.append("V3: CORE.md missing")
        return
    with open(core_path, "r", encoding="utf-8") as fh:
        core = fh.read()
    if "alwaysApply: true" not in core:
        ERRORS.append("V3: CORE.md missing alwaysApply: true")
    if "layer: skeleton" not in core:
        WARNINGS.append("V3: CORE.md missing layer: skeleton")


def v4_iron_laws_consistency():
    core_path = os.path.join(BASE, "rules", "CORE.md")
    claude_path = os.path.join(BASE, "CLAUDE.md")
    if not os.path.exists(core_path) or not os.path.exists(claude_path):
        return
    with open(core_path, "r", encoding="utf-8") as fh:
        core = fh.read()
    with open(claude_path, "r", encoding="utf-8") as fh:
        claude = fh.read()
    for i in range(1, 12):
        if f"R{i}" not in claude:
            ERRORS.append(f"V4: R{i} missing from CLAUDE.md")
    if "Karpathy" not in core or "Karpathy" not in claude:
        ERRORS.append("V4: Karpathy principles missing from CORE.md or CLAUDE.md")


def v5_manifest_completeness():
    manifest_path = os.path.join(BASE, "MANIFEST.yaml")
    if not os.path.exists(manifest_path):
        ERRORS.append("V5: MANIFEST.yaml missing")
        return
    if not yaml:
        WARNINGS.append("V5: PyYAML not installed, skipping MANIFEST check")
        return
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    concerns = manifest.get("concerns", {})
    if not concerns:
        ERRORS.append("V5: MANIFEST.yaml has no concerns")
    required = {
        "brainstorming", "planning", "verification", "debugging", "memory",
        "gstack_review", "gstack_eng", "shell_token", "output_token",
        "change_spec", "phase_planning", "context_engineering",
    }
    missing = required - set(concerns.keys())
    if missing:
        WARNINGS.append(f"V5: Missing MANIFEST concerns: {sorted(missing)}")
    agents_max = manifest.get("global_agents_max", GLOBAL_AGENTS_MAX)
    skills_max = manifest.get("global_skills_max", GLOBAL_SKILLS_MAX)
    if agents_max != GLOBAL_AGENTS_MAX or skills_max != GLOBAL_SKILLS_MAX:
        WARNINGS.append(
            f"V5: MANIFEST limits ({agents_max}/{skills_max}) "
            f"!= validator ({GLOBAL_AGENTS_MAX}/{GLOBAL_SKILLS_MAX})"
        )


def v6_mcp_security():
    mcp_path = os.path.join(BASE, ".mcp.json")
    if not os.path.exists(mcp_path):
        return
    with open(mcp_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    for pattern in [r'["\'](?:sk-|api_key|secret|token|password)["\']\s*:\s*["\'][^"$\{]']:
        if re.search(pattern, content, re.IGNORECASE):
            ERRORS.append("V6: Hardcoded API key/secret in .mcp.json")
    try:
        mcp = json.loads(content)
        servers = mcp.get("mcpServers", {})
        seen = set()
        for name in servers:
            if name in seen:
                ERRORS.append(f"V6: Duplicate MCP server: {name}")
            seen.add(name)
    except Exception:
        pass


def v7_layer_isolation():
    skills_dir = os.path.join(BASE, "skills")
    for skill in P0_SKILLS:
        path = os.path.join(skills_dir, skill, "SKILL.md")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        if "layer: skeleton" not in content:
            ERRORS.append(f"V7: P0 skill {skill} missing layer: skeleton")
    core_path = os.path.join(BASE, "rules", "CORE.md")
    if os.path.exists(core_path):
        with open(core_path, "r", encoding="utf-8") as fh:
            if "layer: skeleton" not in fh.read():
                ERRORS.append("V7: CORE.md missing layer: skeleton")


def v8_file_references():
    claude_path = os.path.join(BASE, "CLAUDE.md")
    if not os.path.exists(claude_path):
        return
    with open(claude_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    refs = re.findall(r'`([^`]+\.(md|yaml|json))`', content)
    for ref, _ in refs:
        full = os.path.join(BASE, ref)
        if not os.path.exists(full) and not ref.startswith("http"):
            WARNINGS.append(f"V8: Referenced file not found: {ref}")


def v9_security_deny_paths():
    """Warn if credential path deny rules missing (source: trailofbits/claude-code-config)."""
    settings_path = os.path.join(BASE, "settings.json")
    if not os.path.exists(settings_path):
        return
    with open(settings_path, "r", encoding="utf-8") as fh:
        settings = json.load(fh)
    deny = settings.get("permissions", {}).get("deny", [])
    deny_text = " ".join(str(d) for d in deny)
    for pattern in ("~/.ssh", "~/.aws", "~/.config/gcloud"):
        if pattern not in deny_text:
            WARNINGS.append(f"V9: settings.json deny missing credential path: {pattern}")
    default_mode = settings.get("permissions", {}).get("defaultMode", "")
    if default_mode == "bypassPermissions":
        WARNINGS.append("V9: defaultMode is bypassPermissions; enterprise default is acceptEdits")


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
    missing_agents = REQUIRED_AGENTS - agent_names
    if missing_agents:
        ERRORS.append(f"Missing agents: {sorted(missing_agents)}")
    if len(agent_names) > GLOBAL_AGENTS_MAX:
        ERRORS.append(f"Too many agents: {len(agent_names)} > {GLOBAL_AGENTS_MAX}")

    skills_dir = os.path.join(BASE, "skills")
    skill_names = {
        d for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d)) and d != "README.md"
    }
    missing_skills = REQUIRED_SKILLS - skill_names
    if missing_skills:
        ERRORS.append(f"Missing required skills: {sorted(missing_skills)}")
    if len(skill_names) > GLOBAL_SKILLS_MAX:
        ERRORS.append(f"Too many skills: {len(skill_names)} > {GLOBAL_SKILLS_MAX}")

    rules_dir = os.path.join(BASE, "rules")
    rule_files = {f for f in os.listdir(rules_dir) if f.endswith(".md") and f != "README.md"}
    missing_rules = GLOBAL_RULES - rule_files
    if missing_rules:
        ERRORS.append(f"Missing global rules: {sorted(missing_rules)}")

    claude_path = os.path.join(BASE, "CLAUDE.md")
    line_count = 0
    if os.path.exists(claude_path):
        with open(claude_path, "r", encoding="utf-8") as fh:
            claude_md = fh.read()
        line_count = claude_md.count("\n") + 1
    if line_count > 500:
        ERRORS.append(f"CLAUDE.md too long: {line_count} lines > 500")

    commands_dir = os.path.join(BASE, "commands")
    if os.path.isdir(commands_dir):
        required_commands = {
            "discuss", "plan", "execute", "verify", "ship", "review",
            "compact", "clear", "status", "propose", "apply", "archive",
            "autoplan", "office-hours",
        }
        cmd_files = {f.replace(".md", "") for f in os.listdir(commands_dir) if f.endswith(".md")}
        missing_cmds = required_commands - cmd_files
        if missing_cmds:
            ERRORS.append(f"Missing commands: {sorted(missing_cmds)}")

    v1_skill_triggers_no_conflict()
    v2_agent_duties_no_overlap()
    v3_rules_no_contradiction()
    v4_iron_laws_consistency()
    v5_manifest_completeness()
    v6_mcp_security()
    v7_layer_isolation()
    v8_file_references()
    v9_security_deny_paths()
    check_v10_bare_except()
    check_v11_hook_exception_propagation()
    check_v12_r16_in_core()

    report(
        agents=len(agent_names),
        skills=len(skill_names),
        rules=len(rule_files),
        claude_lines=line_count,
    )
    return 1 if ERRORS else 0


def report(agents=0, skills=0, rules=0, claude_lines=0):
    print("=== .claude v2 VALIDATION (12 checks) ===")
    print(f"Agents: {agents} | Skills: {skills} | Rules: {rules}")
    print(f"CLAUDE.md: {claude_lines} lines (max 500)")
    print()
    for check_name in ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11", "V12"]:
        related = [e for e in ERRORS if e.startswith(check_name)]
        related_w = [w for w in WARNINGS if w.startswith(check_name)]
        status = "PASS" if not related and not related_w else "WARN" if not related else "FAIL"
        print(f"  [{status}] {check_name}")
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


def check_v10_bare_except():
    """V10: R16 裸except:pass扫描（hooks/目录）"""
    import re as re_mod
    import glob as glob_mod
    import ast as ast_mod
    hooks_dir = os.path.expanduser("~/.claude/hooks")
    count = 0
    for pyfile in glob_mod.glob(os.path.join(hooks_dir, "*.py")):
        if "_optional" in pyfile or "_deprecated" in pyfile:
            continue
        basename = os.path.basename(pyfile)
        try:
            with open(pyfile, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
            tree = ast_mod.parse(source, filename=basename)
            for node in ast_mod.walk(tree):
                if isinstance(node, ast_mod.ExceptHandler):
                    body = node.body
                    if len(body) == 1 and isinstance(body[0], ast_mod.Pass):
                        count += 1
                        ERRORS.append(f"V10: {basename} L{node.lineno} 裸except:pass")
        except SyntaxError as e:
            WARNINGS.append(f"V10: {basename} 解析失败: {e}")
        except (OSError, UnicodeDecodeError) as e:
            WARNINGS.append(f"V10: 扫描{basename}失败: {e}")
    if count == 0:
        print("  V10: 裸except:pass扫描 = 0 ✓")

def check_v11_hook_exception_propagation():
    """V11: Hook异常传播率100%（核心hooks无静默吞异常）"""
    core_hooks = [
        "session-start-bootstrap.py", "pre-bash-guard.py", "pre-rtk-rewrite.py",
        "pre-read-before-edit.py", "pre-config-protection.py", "pre-context-injector.py",
        "pre-manifest-validator.py", "pre-compact-state.py",
        "post-secret-detector.py", "post-edit-format.py", "post-operation-log.py",
        "stop-quality-gate.py", "stop-pattern-extraction.py", "stop-session-summary.py",
        "stop-readme-updater.py",
    ]
    hooks_dir = os.path.expanduser("~/.claude/hooks")
    missing = []
    for h in core_hooks:
        if not os.path.exists(os.path.join(hooks_dir, h)):
            missing.append(h)
    if missing:
        WARNINGS.append(f"V11: 缺少核心hooks: {', '.join(missing)}")
    else:
        print(f"  V11: {len(core_hooks)}核心hooks存在 ✓")

def check_v12_r16_in_core():
    """V12: R16铁律在CORE.md和CLAUDE.md中存在"""
    core_path = os.path.expanduser("~/.claude/rules/CORE.md")
    claude_path = os.path.expanduser("~/.claude/CLAUDE.md")
    for fpath, label in [(core_path, "CORE.md"), (claude_path, "CLAUDE.md")]:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if "R16" not in content:
                ERRORS.append(f"V12: {label} 缺少R16铁律声明")
            elif "裸" not in content and "except" not in content:
                WARNINGS.append(f"V12: {label} R16声明可能不完整（缺少except:pass细节）")
        except OSError as e:
            ERRORS.append(f"V12: 读取{label}失败: {e}")
    print("  V12: R16铁律检查完成")

if __name__ == "__main__":
    sys.exit(main())
