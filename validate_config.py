#!/usr/bin/env python3
"""validate_config.py — .claude config consistency check v3.0"""

import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home() / ".claude"
ERRORS = []

def check(desc, ok):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {desc}")
    if not ok:
        ERRORS.append(desc)

def count_skill_dirs():
    p = HOME / "skills"
    return len([d for d in p.iterdir() if d.is_dir()]) if p.exists() else 0

def count_skill_md_entries():
    p = HOME / "skills" / "SKILL.md"
    if not p.exists(): return -1
    text = p.read_text(encoding="utf-8")
    count = 0
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Skill"):
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line and line.strip() != "|":
            count += 1
        elif in_table and not line.startswith("|"):
            in_table = False
    return count

def count_agent_files():
    p = HOME / "agents"
    return len([f for f in p.iterdir() if f.suffix == ".md" and f.stem != "README"]) if p.exists() else 0

def count_agent_yaml_entries():
    p = HOME / "agent.yaml"
    if not p.exists(): return -1
    text = p.read_text(encoding="utf-8")
    count = 0
    for line in text.splitlines():
        if line.strip().startswith("- ") and not line.strip().startswith("- _"):
            count += 1
    return count

def count_hook_py_files():
    p = HOME / "hooks"
    if not p.exists(): return 0
    return len([f for f in p.iterdir() if f.suffix == ".py" and not f.name.startswith("_")])

def count_settings_hooks():
    p = HOME / "settings.json"
    if not p.exists(): return -1
    data = json.loads(p.read_text(encoding="utf-8"))
    hooks = data.get("hooks", {})
    count = 0
    for event, groups in hooks.items():
        for group in groups:
            count += len(group.get("hooks", []))
    return count

def count_rules_files():
    p = HOME / "rules"
    return len([f for f in p.iterdir() if f.suffix == ".md" and f.stem not in ("README",)]) if p.exists() else 0

def claude_md_lines():
    p = HOME / "CLAUDE.md"
    return len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else -1

def check_mcp_consistency():
    mcp = HOME / ".mcp.json"
    srv = HOME / "mcp" / "servers.json"
    if not mcp.exists() or not srv.exists():
        return set(), set(), {}
    mcp_data = json.loads(mcp.read_text(encoding="utf-8"))
    srv_data = json.loads(srv.read_text(encoding="utf-8"))
    mcp_servers = set(mcp_data.get("mcpServers", {}).keys())
    toolsets = srv_data.get("toolsets", {})
    srv_servers = set()
    for group in toolsets.values():
        srv_servers.update(group)
    return mcp_servers, srv_servers, toolsets

def check_validator_excludes():
    manifest = HOME / "MANIFEST.yaml"
    validator = HOME / "hooks" / "pre-manifest-validator.py"
    if not manifest.exists() or not validator.exists():
        return {}, {}

    mtext = manifest.read_text(encoding="utf-8")
    vtext = validator.read_text(encoding="utf-8")

    # Parse MANIFEST excludes
    manifest_excludes = {}
    current_concern = None
    for line in mtext.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Top-level concern key (no leading space, ends with colon)
        if not line.startswith(" ") and ":" in stripped:
            key = stripped.split(":")[0].strip()
            if key not in ("version", "updated", "pillars", "phases", "concerns",
                          "p0_skills", "global_skills_max", "global_agents_max"):
                current_concern = key
        if "excludes:" in stripped and current_concern:
            bracket_match = re.search(r'\[(.*?)\]', stripped)
            if bracket_match:
                items = set(re.findall(r'[\w-]+/[\w-]+', bracket_match.group(1)))
                if items:
                    manifest_excludes[current_concern] = items

    # Parse validator EXCLUDES
    validator_excludes = {}
    vmatch = re.search(r'EXCLUDES.*?\{(.*?)\}', vtext, re.DOTALL)
    if vmatch:
        block = vmatch.group(1)
        for entry_match in re.finditer(r'"(\w+)"\s*:\s*\{(.*?)\}', block):
            key = entry_match.group(1)
            vals = set(re.findall(r'"([\w/-]+)"', entry_match.group(2)))
            validator_excludes[key] = vals

    return manifest_excludes, validator_excludes


def main():
    print("=" * 60)
    print("  .claude config validation v3.0")
    print("=" * 60)

    # 1. Skills
    print("\n[1] Skills consistency")
    skill_dirs = count_skill_dirs()
    skill_md = count_skill_md_entries()
    check(f"skills/ dirs: {skill_dirs}", skill_dirs > 0)
    check(f"SKILL.md entries: {skill_md}", skill_md > 0)
    check(f"Counts match ({skill_dirs} == {skill_md})", skill_dirs == skill_md)

    # 2. Agents
    print("\n[2] Agents consistency")
    agent_files = count_agent_files()
    agent_yaml = count_agent_yaml_entries()
    check(f"agents/ files: {agent_files}", agent_files > 0)
    check(f"agent.yaml entries: {agent_yaml}", agent_yaml > 0)
    check(f"agents/ count in range (<=22): {agent_files}", agent_files <= 22)

    # 3. Hooks
    print("\n[3] Hooks consistency")
    hook_py = count_hook_py_files()
    settings_hooks = count_settings_hooks()
    check(f"hooks/ .py files (core): {hook_py}", hook_py > 0)
    check(f"settings.json registered: {settings_hooks}", settings_hooks > 0)
    check(f"Hooks count match ({hook_py} == {settings_hooks})", hook_py == settings_hooks)

    # 4. Rules
    print("\n[4] Rules consistency")
    rule_files = count_rules_files()
    check(f"rules/ file count: {rule_files}", 8 <= rule_files <= 12)

    # 5. CLAUDE.md
    print("\n[5] CLAUDE.md line count")
    cl_lines = claude_md_lines()
    check(f"Lines: {cl_lines} (limit: 300)", cl_lines <= 300)

    # 6. MCP
    print("\n[6] MCP consistency")
    mcp_s, srv_s, toolsets = check_mcp_consistency()
    extra_in_servers = srv_s - mcp_s
    missing_in_servers = mcp_s - srv_s
    check(f".mcp.json servers: {len(mcp_s)}", len(mcp_s) > 0)
    check(f"servers.json all in .mcp.json", len(extra_in_servers) == 0)
    if extra_in_servers:
        print(f"    WARN servers.json extras: {extra_in_servers}")
    if missing_in_servers:
        print(f"    WARN servers.json missing: {missing_in_servers}")

    # 7. MANIFEST <-> Validator
    print("\n[7] MANIFEST <-> validator excludes sync")
    mex, vex = check_validator_excludes()
    all_ok = True
    for concern, excludes in mex.items():
        if concern in vex:
            if excludes != vex[concern]:
                print(f"    WARN {concern}: MANIFEST={excludes} vs validator={vex[concern]}")
                all_ok = False
        else:
            print(f"    WARN {concern}: MANIFEST has excludes={excludes} but validator missing")
            all_ok = False
    for concern in vex:
        if concern not in mex:
            print(f"    WARN {concern}: validator has but MANIFEST missing")
            all_ok = False
    check("All MANIFEST excludes synced with validator", all_ok)

    # Summary
    print("\n" + "=" * 60)
    if ERRORS:
        print(f"  FAIL: {len(ERRORS)} checks failed")
        for e in ERRORS:
            print(f"    - {e}")
        sys.exit(1)
    else:
        print("  PASS: All checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
