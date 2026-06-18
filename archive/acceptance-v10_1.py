#!/usr/bin/env python3
"""v10.1 acceptance simulation — Claude Code + Cursor sync compliance."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

try:
    import yaml
except ImportError:
    yaml = None
    print("WARN: PyYAML missing — MANIFEST checks skipped")

BASE = os.path.join(os.environ.get("USERPROFILE", ""), ".claude")
CUR = os.path.join(os.environ.get("USERPROFILE", ""), ".cursor")
DEV = os.path.join(BASE, ".devin", "rules")
results: list[tuple[str, str, str]] = []


def record(name: str, cond: bool, detail: str = "") -> bool:
    results.append(("PASS" if cond else "FAIL", name, detail))
    return cond


def main() -> int:
    # validate_config
    r = subprocess.run(
        [sys.executable, os.path.join(BASE, "scripts", "validate_config.py")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    record(
        "validate_config 16/16",
        r.returncode == 0 and "ALL CHECKS PASSED" in (r.stdout or ""),
        (r.stdout or r.stderr or "").strip().splitlines()[-1] if r.stdout or r.stderr else "",
    )

    # MANIFEST
    manifest_path = os.path.join(BASE, "MANIFEST.yaml")
    raw = open(manifest_path, encoding="utf-8").read()
    m = yaml.safe_load(raw) if yaml else {}
    record("MANIFEST version 10.1", m.get("version") == "10.1")
    record("ECC cherry_pick", m.get("ecc_integration") == "cherry_pick")
    record("UA status disabled", "understand_anything" in raw and "status: disabled" in raw)
    record("ruflo reference_only", "reference_only" in raw)
    lt = m.get("loading_tiers", {})
    record(
        "L1 only P0×2常驻",
        lt.get("L1") == ["skill/using-superpowers", "skill/change-impact-analysis"],
    )
    l2 = lt.get("L2_gate", {})
    p0_l2 = {
        "skill/brainstorming",
        "skill/verification-before-completion",
        "skill/systematic-debugging",
    }
    flat_l2 = sum((l2.get(k, []) for k in l2), [])
    record("P0 L2 gate skills present", p0_l2 <= set(flat_l2))

    conflicts = m.get("module_resolver", {}).get("conflicts", [])
    needed = [
        ["deer_flow", "workstream_management"],
        ["shell_token", "output_token"],
        ["plugin/compound-engineering", "gstack_review"],
    ]
    record(
        "module_resolver conflicts",
        all(pair in conflicts for pair in needed),
        f"{len(conflicts)} pairs",
    )

    # settings.json plugins
    settings = json.load(open(os.path.join(BASE, "settings.json"), encoding="utf-8"))
    ep = settings.get("enabledPlugins", {})
    record("UA plugin off", ep.get("understand-anything@Lum1104") is False)
    record("superpowers on", ep.get("superpowers@claude-plugins-official") is True)
    record("claude-mem on", ep.get("claude-mem@thedotmack") is True)
    record(
        "compound-engineering absent/disabled",
        not any("compound" in k.lower() and v for k, v in ep.items()),
    )

    # Cursor sync
    for f in ("CLAUDE.md", "SPEC.md", "MANIFEST.yaml", "skills-INDEX.md", "agents-INDEX.md"):
        record(f"Cursor symlink {f}", os.path.lexists(os.path.join(CUR, f)))
    rules_dir = os.path.join(CUR, "rules")
    rule_files = os.listdir(rules_dir) if os.path.isdir(rules_dir) else []
    record("Cursor L0 rules = 4", len(rule_files) == 4, ", ".join(sorted(rule_files)))
    record("Cursor skills junction", os.path.isdir(os.path.join(CUR, "skills")))
    record("Cursor agents junction", os.path.isdir(os.path.join(CUR, "agents")))
    sm_path = os.path.join(BASE, "sync-mode.json")
    if not os.path.isfile(sm_path):
        sm_path = os.path.join(CUR, "sync-mode.json")
    if os.path.isfile(sm_path):
        record(
            "sync-mode index",
            json.load(open(sm_path, encoding="utf-8-sig")).get("mode") == "index",
        )
    else:
        record("sync-mode index", False, "missing")

    # Content routing in synced Cursor rules
    claude_mdc = open(os.path.join(rules_dir, "CLAUDE.mdc"), encoding="utf-8").read()
    record("Cursor CLAUDE v10.1", "v10.1" in claude_mdc)
    record("Explore chain synced", "codegraph → Grep → Read" in claude_mdc)
    record("UA disabled in Cursor CLAUDE", "UA disabled" in claude_mdc)

    claude_src = os.path.join(BASE, "CLAUDE.md")
    line_count = len(open(claude_src, encoding="utf-8").readlines())
    record("CLAUDE.md <=250 lines", line_count <= 250, str(line_count))

    # Docs
    repos = os.path.join(BASE, "docs", "research", "repos")
    n_cards = len([x for x in os.listdir(repos) if x.endswith(".md")]) if os.path.isdir(repos) else 0
    record("27 repo cards", n_cards == 27, str(n_cards))

    # Counts
    agent_names = {
        f.replace(".md", "")
        for f in os.listdir(os.path.join(BASE, "agents"))
        if f.endswith(".md") and f != "README.md"
    }
    record("25 agents", len(agent_names) == 25, str(len(agent_names)))
    n_skills = len(
        [d for d in os.listdir(os.path.join(BASE, "skills")) if os.path.isdir(os.path.join(BASE, "skills", d))]
    )
    record("skills count <=38", n_skills <= 38, str(n_skills))

    # Toolchain files
    record("pre-rtk hook", os.path.isfile(os.path.join(BASE, "hooks", "pre-rtk-rewrite.py")))
    record("pre-bash-guard", os.path.isfile(os.path.join(BASE, "hooks", "pre-bash-guard.py")))
    record("firecrawl-mcp.ps1", os.path.isfile(os.path.join(BASE, "scripts", "firecrawl-mcp.ps1")))
    record("codegraph index dir", os.path.isdir(os.path.join(BASE, ".codegraph")))
    record("openspec config", os.path.isfile(os.path.join(BASE, "openspec", "config.yaml")))

    openspec = shutil.which("openspec") or shutil.which("openspec.cmd")
    if openspec:
        r2 = subprocess.run(
            [openspec, "--version"], capture_output=True, text=True, encoding="utf-8"
        )
        record(
            "openspec CLI >=1.4",
            r2.returncode == 0 and r2.stdout.strip().startswith("1.4"),
            r2.stdout.strip(),
        )
    else:
        record("openspec CLI >=1.4", False, "openspec not in PATH")

    # Devin sync
    record("Devin L0 ROUTER", os.path.isfile(os.path.join(DEV, "00-CLAUDE-ROUTER.md")))

    # Simulate git stash block (Claude Code hook)
    hook = os.path.join(BASE, "hooks", "pre-bash-guard.py")
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git stash push -m agent-test"}})
    r3 = subprocess.run(
        [sys.executable, hook],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    record("git stash blocked (exit 2)", r3.returncode == 2, f"exit={r3.returncode}")

    # ~/.claude/hooks 不同步到编辑器；~/.cursor/hooks 为 Cursor Guard 独立部署
    claude_hooks = os.path.join(BASE, "hooks")
    cursor_hooks = os.path.join(CUR, "hooks")
    is_junction_to_claude = False
    if os.path.isdir(cursor_hooks):
        try:
            target = os.path.realpath(cursor_hooks)
            is_junction_to_claude = os.path.realpath(claude_hooks) == target
        except OSError:
            pass
    record(
        "Claude hooks not synced to Cursor",
        not is_junction_to_claude,
        "Cursor Guard hooks OK" if os.path.isdir(cursor_hooks) else "no cursor hooks dir",
    )

    print("=== v10.1 ACCEPTANCE SIMULATION ===\n")
    fails = 0
    for status, name, detail in results:
        suffix = f" — {detail}" if detail else ""
        print(f"[{status}] {name}{suffix}")
        if status == "FAIL":
            fails += 1
    print(f"\nTotal: {len(results) - fails}/{len(results)} PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
