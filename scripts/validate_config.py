#!/usr/bin/env python3
"""配置一致性校验 — V1-V20 共 20 项静态检查（结构/铁律/hook/MCP/INDEX/场景路由）。

命令：
    python scripts/validate_config.py        # 全量校验，有 ERROR 时退出码 1
    powershell -File scripts/check.ps1       # 上层健康检查，内部会调用本脚本

检查项：V1 触发词冲突 / V2 agent 职责重叠 / V3 CORE.md / V4 铁律一致 /
V5 MANIFEST 完整 / V6 MCP 安全 / V7 分层隔离 / V8 文件引用 / V9 deny 路径 /
V10-V12+V17 裸 except 与 R16 / V13-V14 Cursor Guard / V15 skill loading_tier /
V16 codegraph mandate / V17 autoCompactWindow / V18 codebase-memory 禁用 /
V19 三大 INDEX 与磁盘双向一致 / V20 scenario-router + harness-capabilities。

退出码：0 = 无 ERROR（WARNING 不影响）；1 = 存在 ERROR。
"""
import json
import os
import re
import shutil
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

def resolve_base() -> str:
    env = os.environ.get("CLAUDE_HOME")
    if env and os.path.isfile(os.path.join(env, "CLAUDE.md")):
        return os.path.normpath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(here)
    if os.path.isfile(os.path.join(repo, "CLAUDE.md")) and os.path.isdir(
        os.path.join(repo, "skills")
    ):
        return repo
    for key in ("USERPROFILE", "HOME"):
        home = os.environ.get(key) or ""
        cand = os.path.join(home, ".claude")
        if home and os.path.isfile(os.path.join(cand, "CLAUDE.md")):
            return cand
    return os.path.join(os.environ.get("HOME") or os.environ.get("USERPROFILE") or "", ".claude")


BASE = resolve_base()
ERRORS = []
WARNINGS = []
INFO = []

CORE_AGENTS = {
    "planner", "code-explorer", "code-reviewer", "build-error-resolver",
    "architect", "spec-reviewer", "agentic-orchestrator",
}
GSTACK_REVIEW_AGENTS = {
    "eng-reviewer", "ceo-reviewer", "designer", "dx-reviewer", "qa", "security-reviewer",
}
# v11 收敛：cso→security-reviewer 深度模式；release-engineer→skill/ship；design-engineer→skill/design-pipeline；
# product-manager 删除；performance-engineer/pair-agent/ios-specialist/land-and-deploy/design-shotgun 降级 catalog/agents/
GSTACK_SUPPLEMENT_AGENTS = {
    "sre", "doc-writer", "change-implementer", "codex-reviewer",
}
REQUIRED_AGENTS = CORE_AGENTS | GSTACK_REVIEW_AGENTS | GSTACK_SUPPLEMENT_AGENTS
GLOBAL_AGENTS_MAX = 17  # v11.4.11: 7 核心 + 6 审查 + 3 补全 + 1 跨模型

P0_SKILLS = {
    "using-superpowers", "brainstorming", "change-impact-analysis",
    "verification-before-completion", "systematic-debugging", "task-triage",
}
WORKFLOW_SKILLS = {
    "writing-plans", "executing-plans", "test-driven-development",
    "subagent-driven-development", "using-git-worktrees", "receiving-code-review",
    "requesting-code-review", "finishing-a-development-branch",
}  # v11: writing-skills 并入 skill-creator 前言
META_SKILLS = {
    "memory-compression", "spec-validation", "karpathy-guidelines", "caveman-compress",
}
# v11: office-hours/browser-qa/instinct-learning/onboarding-guide/claude-to-deerflow/taste-memory 降级 catalog/skills/；
# context-engineering 删除（rules/CONTEXT.md 为唯一正文）；frontend-refactor-proposer 并入 code-refactoring
EXTENSION_SKILLS = {
    "autoplan", "design-pipeline", "ship", "structured-artifacts",
}
MATTPOCOCK_SKILLS = {"triage", "improve-codebase-architecture"}
V9_SKILLS = {
    "workstream-management", "adr-management",
}
REQUIRED_SKILLS = (
    P0_SKILLS | WORKFLOW_SKILLS | META_SKILLS | EXTENSION_SKILLS
    | MATTPOCOCK_SKILLS | V9_SKILLS
)
GLOBAL_SKILLS_MAX = 36  # v11 定稿：superpowers 系 12 技能均为本地深度定制（相似度<10%），保留本地权威；writing-skills 并入 skill-creator

# v11: DESIGN.md 并入 FRONTEND.md（设计系统节）；BESTPRACTICE.md 并入 GOVERNANCE.md（最佳实践详参章）
GLOBAL_RULES = {
    "CORE.md", "SECURITY.md", "GIT.md", "WORKFLOW.md",
    "AGENTS.md", "MCP.md", "CONTEXT.md", "OPENSPEC.md",
    "FRONTEND.md", "GOVERNANCE.md",
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
    for i in range(1, 21):
        if i == 0:
            continue
        tag = f"R{i}"
        if tag not in claude and tag not in core:
            ERRORS.append(f"V4: {tag} missing from CLAUDE.md or CORE.md")
    for tag in ("R17", "R18", "R20"):
        if tag not in claude or tag not in core:
            ERRORS.append(f"V4: {tag} must appear in both CLAUDE.md and CORE.md")
    if "Karpathy" not in core or "Karpathy" not in claude:
        ERRORS.append("V4: Karpathy principles missing from CORE.md or CLAUDE.md")
    verif_path = os.path.join(BASE, "skills", "verification-before-completion", "SKILL.md")
    extra = core
    if os.path.exists(verif_path):
        with open(verif_path, "r", encoding="utf-8") as fh:
            extra = core + "\n" + fh.read()
    for kw in ("漏改", "原功能", "文档/注释"):
        if kw not in extra:
            ERRORS.append(
                f"V4: R20 keyword {kw!r} missing from CORE.md or verification skill"
            )
        if kw not in claude:
            ERRORS.append(f"V4: R20 keyword {kw!r} missing from CLAUDE.md")


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
        "change_implementer",
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
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        pass  # noqa: R16 — validate_config self-check, skip unreadable config


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
    if line_count > 200:
        ERRORS.append(f"CLAUDE.md too long: {line_count} lines > 200 (SPEC ≤200)")

    commands_dir = os.path.join(BASE, "commands")
    if os.path.isdir(commands_dir):
        required_commands = {
            "discuss", "plan", "execute", "verify", "ship", "review",
            "compact", "clear", "status", "propose", "apply", "archive",
            "autoplan", "office-hours", "workstream", "adr", "deep-research", "sync",
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
    check_v13_cursor_guard()
    check_v14_cursor_guard_v11()
    check_v15_loading_tiers()
    check_v16_codegraph_mandate()
    check_v17_bare_except_extended()
    check_v17_auto_compact_window()
    check_v18_codebase_memory_optional()
    check_v19_index_disk_sync()
    check_v20_scenario_router()

    report(
        agents=len(agent_names),
        skills=len(skill_names),
        rules=len(rule_files),
        claude_lines=line_count,
    )
    return 1 if ERRORS else 0


def report(agents=0, skills=0, rules=0, claude_lines=0):
    print("=== .claude v11 VALIDATION (20 checks) ===")
    print(f"Agents: {agents} | Skills: {skills} | Rules: {rules}")
    print(f"CLAUDE.md: {claude_lines} lines (max 200)")
    print()
    for check_name in [
        "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
        "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18",
        "V19", "V20",
    ]:
        related = [e for e in ERRORS if e.startswith(check_name + ":")]
        related_w = [w for w in WARNINGS if w.startswith(check_name + ":")]
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
    hooks_dir = os.path.join(BASE, "hooks")
    count = 0
    for pyfile in glob_mod.glob(os.path.join(hooks_dir, "*.py")):
        if "_archive" in pyfile or "_optional" in pyfile or "_deprecated" in pyfile:
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
    # v11: post-codegraph-sync / stop-knowledge-graph-sync 已退役（codegraph v1.5 MCP 自动同步接管）
    # v11.1: 补漏登记 pre-userprompt-issue-tracker（settings.json 已注册）；
    #        pre-tmux-reminder / pre-loop-guard / pre-suggest-compact / stop-context-monitor
    #        为「保留未注册」（原生机制或 Cursor Guard 已覆盖），仅做存在性检查
    core_hooks = [
        "session-start-bootstrap.py", "pre-userprompt-verify-gate.py",
        "pre-userprompt-issue-tracker.py",
        "pre-bash-guard.py", "pre-rtk-rewrite.py",
        "pre-graph-freshness.py",
        "pre-read-before-edit.py", "pre-edit-impact-nudge.py",
        "pre-context-injector.py", "pre-manifest-validator.py",
        "pre-compact-state.py",
        "post-secret-detector.py", "post-edit-format.py",
        "post-edit-verify-tracker.py",
        "stop-verification-gate.py",
        "stop-session-summary.py", "stop-readme-updater.py",
    ]
    optional_hooks = [
        "pre-tmux-reminder.py", "pre-loop-guard.py",
        "pre-suggest-compact.py", "stop-context-monitor.py",
        "stop-graph-freshness.py",
    ]
    hooks_dir = os.path.join(BASE, "hooks")
    missing = []
    for h in core_hooks:
        if not os.path.exists(os.path.join(hooks_dir, h)):
            missing.append(h)
    missing_optional = [
        h for h in optional_hooks
        if not os.path.exists(os.path.join(hooks_dir, h))
    ]
    if missing:
        WARNINGS.append(f"V11: 缺少核心hooks: {', '.join(missing)}")
    else:
        print(f"  V11: {len(core_hooks)}核心hooks(已注册)存在 ✓")
    if missing_optional:
        WARNINGS.append(f"V11: 缺少保留未注册hooks: {', '.join(missing_optional)}")
    else:
        print(f"  V11: {len(optional_hooks)}保留未注册hooks存在 ✓")

def check_v12_r16_in_core():
    """V12: R16铁律在CORE.md和CLAUDE.md中存在"""
    core_path = os.path.join(BASE, "rules", "CORE.md")
    claude_path = os.path.join(BASE, "CLAUDE.md")
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


def check_v13_cursor_guard():
    """V13: Cursor Guard 模板与部署脚本存在"""
    template = os.path.join(BASE, "templates", "cursor-guard", "hooks.json")
    deploy_script = os.path.join(BASE, "scripts", "deploy-cursor-guard.ps1")
    required_hooks = (
        "sync_on_edit.py",
        "sync_on_prompt.py",
        "context_pre_tool.py",
        "context_post_tool.py",
        "context_stop.py",
        "session_bootstrap.py",
        "pre_compact_snapshot.py",
        "verification_stop.py",
        "first_edit_verify.py",
        "r20_capture.py",
        "graph_freshness.py",
    )
    if not os.path.isfile(template):
        ERRORS.append("V13: templates/cursor-guard/hooks.json missing")
        return
    if not os.path.isfile(deploy_script):
        ERRORS.append("V13: scripts/deploy-cursor-guard.ps1 missing")
        return
    hooks_tpl = os.path.join(BASE, "templates", "cursor-guard", "hooks")
    missing = [h for h in required_hooks if not os.path.isfile(os.path.join(hooks_tpl, h))]
    if missing:
        ERRORS.append(f"V13: missing cursor-guard hooks: {', '.join(missing)}")
    hook_io = os.path.join(hooks_tpl, "_lib", "hook_io.py")
    if not os.path.isfile(hook_io):
        ERRORS.append("V13: templates/cursor-guard/hooks/_lib/hook_io.py missing")
    proj_hooks = os.path.join(BASE, ".cursor", "hooks.json")
    if not os.path.isfile(proj_hooks):
        ERRORS.append(
            "V13: .cursor/hooks.json missing (Cursor treats absent project hooks as parse ERROR)"
        )
    else:
        try:
            with open(proj_hooks, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            if not isinstance(data, dict) or data.get("version") != 1:
                ERRORS.append("V13: .cursor/hooks.json must be JSON object with version=1")
        except (OSError, json.JSONDecodeError) as exc:
            ERRORS.append(f"V13: .cursor/hooks.json parse failed: {exc}")
    if not missing and os.path.isfile(hook_io) and os.path.isfile(proj_hooks):
        print(f"  V13: Cursor Guard 模板 {len(required_hooks)} hooks ✓")


# v11: 对齐 MANIFEST loading_tiers（SSOT）——brainstorming 属 L1（P0 路由集常驻）；
# subagent-driven-development 自 v10.15 默认关闭改 L3（显式触发），随 TDD 一并落 L3 默认档
SKILL_TIER_L1 = {"using-superpowers", "change-impact-analysis", "task-triage", "brainstorming"}
SKILL_TIER_L2 = {
    "writing-plans", "spec-validation", "executing-plans",
    "verification-before-completion", "systematic-debugging",
}
# L1 中唯一带 HARD-GATE 的技能：保留 disable-model-invocation，防 Cursor 触发词自动激活，
# 仅经 ROUTER/门控显式 Read（MANIFEST note: Cursor 用 disable + 显式 Read）
L1_DISABLE_EXEMPT = {"brainstorming"}


def _parse_skill_frontmatter(skill_path):
    """Return frontmatter dict from SKILL.md or None."""
    try:
        with open(skill_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError:
        return None
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    block = content[3:end]
    fm = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm


def check_v15_loading_tiers():
    """V15: L0-L3 skill frontmatter — loading_tier + disable-model-invocation 与 skills-INDEX 一致."""
    skills_dir = os.path.join(BASE, "skills")
    if not os.path.isdir(skills_dir):
        ERRORS.append("V15: skills/ directory missing")
        return
    checked = 0
    for name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        fm = _parse_skill_frontmatter(skill_path)
        if fm is None:
            continue
        checked += 1
        expected = (
            "L1" if name in SKILL_TIER_L1
            else ("L2" if name in SKILL_TIER_L2 else "L3")
        )
        actual = fm.get("loading_tier", "")
        if actual != expected:
            ERRORS.append(
                f"V15: skills/{name}/SKILL.md loading_tier={actual!r} expected {expected}"
            )
        has_disable = fm.get("disable-model-invocation") == "true"
        if expected == "L1" and has_disable and name not in L1_DISABLE_EXEMPT:
            ERRORS.append(f"V15: L1 skill {name} must not have disable-model-invocation")
        if expected in ("L2", "L3") and not has_disable:
            ERRORS.append(f"V15: {expected} skill {name} missing disable-model-invocation: true")

    manifest_path = os.path.join(BASE, "MANIFEST.yaml")
    if yaml and os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh)
        tiers = manifest.get("loading_tiers", {})
        for group, entries in tiers.items():
            if group == "note":
                continue
            if not isinstance(entries, list):
                for sub_entries in entries.values():
                    if not isinstance(sub_entries, list):
                        continue
                    for entry in sub_entries:
                        if not entry.startswith("skill/"):
                            continue
                        skill_name = entry.replace("skill/", "")
                        path = os.path.join(skills_dir, skill_name, "SKILL.md")
                        if not os.path.isfile(path):
                            ERRORS.append(f"V15: MANIFEST loading_tiers missing {path}")

    if checked and not any(e.startswith("V15:") for e in ERRORS):
        print(f"  V15: {checked} skills loading_tier + disable ✓")


def check_v14_cursor_guard_v11():
    """V14: Cursor Guard v1.1 扩展 hook 与文档"""
    v11_hooks = (
        "explore_router.py",
        "maintenance_hints.py",
        "shell_guard.py",
        "prompt_secret_scan.py",
    )
    hooks_tpl = os.path.join(BASE, "templates", "cursor-guard", "hooks")
    missing = [h for h in v11_hooks if not os.path.isfile(os.path.join(hooks_tpl, h))]
    if missing:
        ERRORS.append(f"V14: missing v1.1 hooks: {', '.join(missing)}")
        return
    doc = os.path.join(BASE, "docs", "CURSOR_EDITOR_SETUP.md")
    rule = os.path.join(BASE, "templates", "cursor-guard", "rules", "CURSOR-EDITOR.mdc")
    if not os.path.isfile(doc):
        ERRORS.append("V14: docs/CURSOR_EDITOR_SETUP.md missing")
    if not os.path.isfile(rule):
        ERRORS.append("V14: templates/cursor-guard/rules/CURSOR-EDITOR.mdc missing")
    hooks_json = os.path.join(BASE, "templates", "cursor-guard", "hooks.json")
    guard_cfg = os.path.join(BASE, "templates", "cursor-guard", "guard-config.json")
    try:
        with open(hooks_json, "r", encoding="utf-8-sig") as fh:
            gv = json.load(fh).get("guard_version")
        with open(guard_cfg, "r", encoding="utf-8-sig") as fh:
            expected = json.load(fh).get("version")
        if gv != expected:
            ERRORS.append(
                f"V14: templates/cursor-guard/hooks.json guard_version={gv!r} "
                f"expected {expected!r} (guard-config.json version)"
            )
    except (OSError, json.JSONDecodeError) as exc:
        ERRORS.append(f"V14: hooks.json/guard-config unreadable: {exc}")
        return
    man = os.path.join(BASE, "MANIFEST.yaml")
    try:
        with open(man, "r", encoding="utf-8") as fh:
            man_text = fh.read()
        note_m = re.search(
            r"cursor_guard:\s*\n(?:.*\n)*?\s*note:\s*\"([^\"]+)\"",
            man_text,
        )
        if expected and note_m and f"v{expected}" not in note_m.group(1):
            ERRORS.append(
                f"V14: MANIFEST cursor_guard.note missing Guard v{expected}"
            )
    except OSError as exc:
        ERRORS.append(f"V14: MANIFEST.yaml unreadable: {exc}")
    if not missing and os.path.isfile(doc) and os.path.isfile(rule):
        print(f"  V14: Cursor Guard v{gv} ({len(v11_hooks)} hooks + docs) ✓")


def check_v17_auto_compact_window():
    """V17: autoCompactWindow 须与当前模型解析窗口一致，且不得超过模型最大上下文."""
    settings_path = os.path.join(BASE, "settings.json")
    registry_path = os.path.join(BASE, "config", "model-context-windows.json")
    if not os.path.isfile(settings_path):
        return
    if not os.path.isfile(registry_path):
        WARNINGS.append("V17: config/model-context-windows.json missing")
    try:
        with open(settings_path, "r", encoding="utf-8") as fh:
            settings = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        ERRORS.append(f"V17: settings.json unreadable: {exc}")
        return

    hooks_lib = os.path.join(BASE, "hooks", "_lib")
    if hooks_lib not in sys.path:
        sys.path.insert(0, hooks_lib)
    try:
        from context_thresholds import (  # noqa: WPS433
            active_model_name,
            recommended_autocompact_window,
            resolve_model_context_tokens,
        )
    except ImportError as exc:
        ERRORS.append(f"V17: cannot import context_thresholds: {exc}")
        return

    env = settings.get("env") or {}
    model = active_model_name() or str(settings.get("model") or env.get("ANTHROPIC_MODEL") or "")
    window = settings.get("autoCompactWindow")
    env_window = env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    pct_override = env.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")
    warn_pct = env.get("CLAUDE_COMPACT_WARN_PCT")
    force_pct = env.get("CLAUDE_COMPACT_FORCE_PCT")

    expected = recommended_autocompact_window(model)
    model_max = resolve_model_context_tokens(model)

    if env_window is not None:
        WARNINGS.append(
            "V17: remove env.CLAUDE_CODE_AUTO_COMPACT_WINDOW — "
            "use autoCompactWindow + config/model-context-windows.json (动态解析)"
        )
        try:
            if int(env_window) > model_max:
                ERRORS.append(
                    f"V17: CLAUDE_CODE_AUTO_COMPACT_WINDOW={env_window} exceeds "
                    f"model max {model_max} for {model!r}"
                )
        except (TypeError, ValueError):
            pass

    if not isinstance(window, int) or window <= 0:
        ERRORS.append(f"V17: autoCompactWindow={window!r} invalid — run scripts/sync-compact-window.py")
    elif window > model_max:
        ERRORS.append(
            f"V17: autoCompactWindow={window} exceeds model max {model_max} for {model!r}"
        )
    elif window != expected:
        WARNINGS.append(
            f"V17: autoCompactWindow={window} != resolved {expected} for {model!r} "
            "— run scripts/sync-compact-window.py"
        )

    if str(pct_override) != "70":
        WARNINGS.append(
            f"V17: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE={pct_override!r} expected '70' "
            "(native auto-compact at 70%; hooks force at 90%)"
        )
    if str(warn_pct) != "70":
        WARNINGS.append(f"V17: CLAUDE_COMPACT_WARN_PCT={warn_pct!r} expected '70'")
    if str(force_pct) != "90":
        WARNINGS.append(f"V17: CLAUDE_COMPACT_FORCE_PCT={force_pct!r} expected '90'")

    if not any(e.startswith("V17:") for e in ERRORS):
        print(f"  V17: autoCompactWindow {window} / model {model!r} max {model_max} ✓")


def check_v16_codegraph_mandate():
    """V16: codegraph mandate — ~/.claude/.codegraph/ 索引目录就绪."""
    cg_dir = os.path.join(BASE, ".codegraph")
    if not os.path.isdir(cg_dir):
        ERRORS.append("V16: ~/.claude/.codegraph/ missing — run: codegraph init")
        return
    markers = (
        "index.sqlite",
        "graph.db",
        "codegraph.db",
        "daemon.pid",
        "config.json",
    )
    has_marker = any(os.path.isfile(os.path.join(cg_dir, m)) for m in markers)
    if not has_marker:
        # 目录存在但无索引文件
        entries = [
            f for f in os.listdir(cg_dir)
            if f not in (".gitignore", "daemon.log")
        ]
        if not entries:
            WARNINGS.append(
                "V16: .codegraph/ exists but no index — run: codegraph init in ~/.claude"
            )
        else:
            print(f"  V16: .codegraph/ present ({len(entries)} entries) ✓")
    else:
        print("  V16: codegraph index markers ✓")

    qg_path = os.path.join(BASE, "config", "quality_gates.json")
    try:
        with open(qg_path, "r", encoding="utf-8") as fh:
            gf = json.load(fh).get("graph_freshness") or {}
    except (OSError, json.JSONDecodeError) as exc:
        ERRORS.append(f"V16: quality_gates.json graph_freshness unreadable: {exc}")
        return
    required = (
        "session_ensure_timeout_sec",
        "pretool_ensure_timeout_sec",
        "stop_refresh_timeout_sec",
        "sync_ps1_timeout_sec",
    )
    missing = [k for k in required if k not in gf]
    if missing:
        ERRORS.append(f"V16: graph_freshness missing keys: {', '.join(missing)}")
        return
    if int(gf.get("session_ensure_timeout_sec") or 0) < 120:
        WARNINGS.append(
            "V16: graph_freshness.session_ensure_timeout_sec < 120 "
            "(首次建图可能被截断)"
        )
    snippet = os.path.join(BASE, "templates", "claude-settings", "hooks.snippet.json")
    try:
        with open(snippet, "r", encoding="utf-8") as fh:
            text = fh.read()
        if "pre-graph-freshness.py" not in text:
            ERRORS.append("V16: hooks.snippet.json missing pre-graph-freshness.py")
        if '"timeout": 120000' not in text and '"timeout":120000' not in text:
            WARNINGS.append("V16: hooks.snippet.json SessionStart timeout 不是 120000ms")
    except OSError as exc:
        WARNINGS.append(f"V16: hooks.snippet.json unreadable: {exc}")
    print("  V16: graph_freshness timeouts + snippet ✓")


def check_v17_bare_except_extended():
    """V17: R16 扩展 — 裸 except 扫描（hooks/ + scripts/，含 bare except: 和 except Exception:）"""
    import re as re_mod
    import glob as glob_mod

    # Infrastructure files exempt from V17 (launchers, guards)
    INFRA_EXEMPT = {
        "_editor_hook_launcher.py",
        "pre-loop-guard.py",      # L4 isolation layer, by design
    }
    scan_dirs = [
        os.path.join(BASE, "hooks"),
        os.path.join(BASE, "scripts"),
    ]
    violations = []

    for scan_dir in scan_dirs:
        if not os.path.isdir(scan_dir):
            continue
        for pyfile in glob_mod.glob(os.path.join(scan_dir, "*.py")):
            basename = os.path.basename(pyfile)
            if basename in INFRA_EXEMPT:
                continue
            if basename.startswith("_"):
                continue
            try:
                with open(pyfile, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    in_hooks = "hooks" in pyfile.lower()
                    # Only flag truly bare except: (no exception type) — always an error
                    if re_mod.match(r'^\s*except\s*:', line):
                        next_line = lines[i].strip() if i < len(lines) else ""
                        if 'noqa: R16' not in next_line and 'noqa: R16' not in stripped:
                            violations.append(f"{basename}:{i} bare 'except:'")
                    # except Exception: pass — flag in scripts/, exempt in hooks/ (fail-safe design)
                    elif re_mod.match(r'^\s*except\s+Exception\s*:', line) and not in_hooks:
                        next_line = lines[i].strip() if i < len(lines) else ""
                        if 'noqa: R16' not in next_line and 'noqa: R16' not in stripped:
                            body_lines = []
                            for j in range(i+1, min(i+3, len(lines))):
                                bl = lines[j].strip()
                                if bl and not bl.startswith('#'):
                                    body_lines.append(bl)
                                    break
                            body_text = " ".join(body_lines)
                            if body_text in ("pass", "") or stripped.endswith(": pass"):
                                violations.append(f"{basename}:{i} bare 'except Exception: pass'")
            except (OSError, UnicodeDecodeError) as e:
                WARNINGS.append(f"V17: 扫描{basename}失败: {e}")

    if violations:
        for v in violations:
            ERRORS.append(f"V17: {v}")
        print(f"  V17 R16 扩展: FAIL ({len(violations)} violations)")
    else:
        print("  V17 R16 扩展: PASS (0 bare except) ✓")


def check_v18_codebase_memory_optional():
    """V18: codebase-memory-mcp 已永久禁用（v10.10，全盘索引爆 CPU/内存）。
    要求：不在 .mcp.json mcpServers；optional-dev.json 中仅 disabled/归档（无运行条目）。"""
    import json

    opt_path = os.path.join(BASE, "mcp-configs", "optional-dev.json")
    mcp_path = os.path.join(BASE, ".mcp.json")
    opt_data = {}
    mcp_data = {}

    if os.path.isfile(opt_path):
        try:
            with open(opt_path, "r", encoding="utf-8") as fh:
                opt_data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            WARNINGS.append(f"V18: optional-dev.json unreadable: {exc}")
    else:
        WARNINGS.append("V18: mcp-configs/optional-dev.json missing")

    if os.path.isfile(mcp_path):
        try:
            with open(mcp_path, "r", encoding="utf-8") as fh:
                mcp_data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            pass

    opt_entry = (opt_data.get("mcpServers") or {}).get("codebase-memory")
    mcp_entry = (mcp_data.get("mcpServers") or {}).get("codebase-memory")
    disabled = opt_data.get("disabled") or {}
    archived = opt_data.get("_archive_codebase_memory")

    if mcp_entry:
        WARNINGS.append("V18: codebase-memory in .mcp.json - v10.10 永久禁用（全盘索引爆 CPU/内存），remove")
    if opt_entry:
        WARNINGS.append("V18: codebase-memory active in optional-dev mcpServers - v10.10 永久禁用，move to disabled/archive")
    if "codebase-memory" not in disabled and not archived:
        WARNINGS.append("V18: codebase-memory disabled/archive note missing in optional-dev.json")
    print("  V18: codebase-memory permanently disabled (CPU/RAM) OK")


def check_v19_index_disk_sync():
    """V19: 三大 INDEX 与磁盘双向一致（INDEX 不引用不存在项，磁盘项不漏登记）。

    原属 scripts/tests/_simtest.py，v10.17 该脚本删除后移植至此，
    避免 agents-INDEX 漏登记无人发现（V15 只覆盖 skills 的 loading_tier）。
    """
    def indexed(index_name, pattern, group):
        path = os.path.join(BASE, index_name)
        if not os.path.isfile(path):
            ERRORS.append(f"V19: {index_name} missing")
            return None
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        return {m.group(group) for m in re.finditer(pattern, text)}

    def compare(label, index_name, idx, disk):
        if idx is None:
            return
        ghost = idx - disk
        unlisted = disk - idx
        if ghost:
            ERRORS.append(f"V19: {index_name} 引用了不存在的{label}: {sorted(ghost)}")
        if unlisted:
            ERRORS.append(f"V19: {label} 未登记进 {index_name}: {sorted(unlisted)}")
        if not ghost and not unlisted:
            print(f"  V19: {index_name} == disk ({len(disk)} {label}) ✓")

    skills_dir = os.path.join(BASE, "skills")
    disk_skills = {
        d for d in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))
    } if os.path.isdir(skills_dir) else set()
    compare(
        "skill", "skills-INDEX.md",
        indexed("skills-INDEX.md", r"\[([^\]]+)\]\(skills/([^/]+)/SKILL\.md\)", 2),
        disk_skills,
    )

    agents_dir = os.path.join(BASE, "agents")
    disk_agents = {
        f[:-3] for f in os.listdir(agents_dir)
        if f.endswith(".md") and f != "README.md"
    } if os.path.isdir(agents_dir) else set()
    compare(
        "agent", "agents-INDEX.md",
        indexed("agents-INDEX.md", r"\[[^\]]+\]\(agents/([^)/]+)\.md\)", 1),
        disk_agents,
    )

    rules_dir = os.path.join(BASE, "rules")
    disk_rules = {
        f for f in os.listdir(rules_dir)
        if f.endswith(".md") and f != "README.md"
    } if os.path.isdir(rules_dir) else set()
    compare(
        "rule", "rules-INDEX.md",
        indexed("rules-INDEX.md", r"\[[^\]]+\]\(rules/([^)/]+\.md)\)", 1),
        disk_rules,
    )


def _load_yaml(rel: str):
    path = os.path.join(BASE, rel)
    if not os.path.isfile(path):
        ERRORS.append(f"V20: {rel} missing")
        return None
    if yaml is None:
        WARNINGS.append(f"V20: PyYAML missing, skip parse of {rel}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        ERRORS.append(f"V20: {rel} unreadable: {exc}")
        return None


def check_v20_scenario_router():
    """V20: scenario-router 语义闭环 + harness fallback + 钩子消费 quality_gates 新键。"""
    router = _load_yaml(os.path.join("config", "scenario-router.yaml"))
    caps = _load_yaml(os.path.join("config", "harness-capabilities.yaml"))
    if not router or not caps:
        return

    cap_ids = set(caps.get("capability_ids") or [])
    defaults = caps.get("defaults") or {}
    missing_default = cap_ids - set(defaults)
    if missing_default:
        ERRORS.append(f"V20: harness defaults 缺少 capability: {sorted(missing_default)}")

    for cid, spec in defaults.items():
        if not isinstance(spec, dict):
            continue
        has_fb = "fallback" in spec
        has_int = spec.get("interrupt") is True or spec.get("provider") == "interrupt"
        if not has_fb and not has_int:
            ERRORS.append(f"V20: capability {cid} 缺 fallback 或 interrupt")

    skills_dir = os.path.join(BASE, "skills")
    agents_dir = os.path.join(BASE, "agents")
    rules_dir = os.path.join(BASE, "rules")
    disk_skills = {
        d for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d))
    } if os.path.isdir(skills_dir) else set()
    disk_agents = {
        f[:-3] for f in os.listdir(agents_dir)
        if f.endswith(".md") and f != "README.md"
    } if os.path.isdir(agents_dir) else set()
    disk_rules = {
        f for f in os.listdir(rules_dir)
        if f.endswith(".md")
    } if os.path.isdir(rules_dir) else set()

    for name in (router.get("load_defaults") or {}).get("skills") or []:
        if name not in disk_skills:
            ERRORS.append(f"V20: load_defaults unknown skill {name}")

    tmap = router.get("triage_map") or {}
    scenarios = router.get("scenarios") or {}
    if not tmap:
        ERRORS.append("V20: triage_map missing")
    for key, sid in tmap.items():
        if sid not in scenarios:
            ERRORS.append(f"V20: triage_map {key} -> unknown scenario {sid}")
            continue
        spec = scenarios[sid]
        if spec.get("overlay"):
            ERRORS.append(f"V20: triage_map {key} 指向 overlay 场景 {sid}")
        expected = [p for p in str(key).split("|") if p]
        got = list(spec.get("match") or [])
        if sorted(expected) != sorted(got):
            ERRORS.append(f"V20: scenario {sid} match {got} != triage_map {expected}")

    mapped = set(tmap.values())
    for sid, spec in scenarios.items():
        if not isinstance(spec, dict):
            continue
        if not spec.get("overlay") and sid not in mapped:
            ERRORS.append(f"V20: 非 overlay 场景 {sid} 未出现在 triage_map")
        load = spec.get("load") or {}
        for name in load.get("skills") or []:
            if name not in disk_skills:
                ERRORS.append(f"V20: scenario {sid} unknown skill {name}")
        for name in load.get("agents") or []:
            if name not in disk_agents:
                ERRORS.append(f"V20: scenario {sid} unknown agent {name}")
        for name in load.get("rules") or []:
            if name not in disk_rules:
                ERRORS.append(f"V20: scenario {sid} unknown rule {name}")
        for cid in spec.get("capabilities") or []:
            if cid not in cap_ids:
                ERRORS.append(f"V20: scenario {sid} unknown capability {cid}")
        q = spec.get("quality")
        if q is not None and not isinstance(q, dict):
            ERRORS.append(f"V20: scenario {sid} quality 必须是 object")
            continue
        ir = (q or {}).get("independent_review")
        if ir is not None and not isinstance(ir, dict):
            ERRORS.append(f"V20: scenario {sid} independent_review 必须是 object")
        for an in (q or {}).get("review") or []:
            if an not in disk_agents:
                ERRORS.append(f"V20: scenario {sid} review unknown agent {an}")
        opt = (q or {}).get("review_catalog_optional") or {}
        if opt and not isinstance(opt, dict):
            ERRORS.append(f"V20: scenario {sid} review_catalog_optional 必须是 object")
        elif isinstance(opt, dict):
            for names in opt.values():
                for an in names if isinstance(names, list) else [names]:
                    if an not in disk_agents:
                        ERRORS.append(f"V20: scenario {sid} catalog review unknown agent {an}")

    ir = (router.get("quality_defaults") or {}).get("independent_review") or {}
    if not isinstance(ir, dict):
        ERRORS.append("V20: quality_defaults.independent_review 必须是 object")
    before = ir.get("before") or []
    if "dual_graph_ensure" not in before:
        ERRORS.append("V20: independent_review.before 必须含 dual_graph_ensure")
    parallel = ir.get("parallel") or {}
    if parallel.get("forbid_multiplier_models") is not True:
        ERRORS.append("V20: parallel.forbid_multiplier_models 必须为 true")
    if "model_inherit_only" not in (parallel.get("when_all") or []):
        ERRORS.append("V20: parallel.when_all 必须含 model_inherit_only")
    if str(parallel.get("require_model") or "").strip().lower() != "inherit":
        ERRORS.append("V20: parallel.require_model 必须为 inherit")

    harnesses = caps.get("harnesses") or {}
    required = {"claude-code", "cursor", "dsh", "opencode"}
    missing_h = required - set(harnesses)
    if missing_h:
        ERRORS.append(f"V20: harness-capabilities 缺少 harness: {sorted(missing_h)}")
    wb = harnesses.get("workbuddy") or {}
    ov = wb.get("overrides") or {}
    fake = set(ov) - cap_ids
    if fake:
        ERRORS.append(f"V20: workbuddy.overrides 含非 capability 键: {sorted(fake)}")
    dsh_extra = (harnesses.get("dsh") or {}).get("extra") or {}
    if dsh_extra.get("forbid") != "claude_md_overwrite_agents_md":
        ERRORS.append("V20: dsh.extra.forbid 必须为 claude_md_overwrite_agents_md")

    qg_path = os.path.join(BASE, "config", "quality_gates.json")
    try:
        with open(qg_path, "r", encoding="utf-8") as fh:
            qg = json.load(fh).get("verification_gate") or {}
    except (OSError, json.JSONDecodeError) as exc:
        ERRORS.append(f"V20: quality_gates.json unreadable: {exc}")
        qg = {}
    for key in ("require_dual_graph_before_review", "parallel_review"):
        if key not in qg:
            ERRORS.append(f"V20: quality_gates.verification_gate 缺少 {key}")
    stop_path = os.path.join(BASE, "hooks", "stop-verification-gate.py")
    try:
        stop_src = open(stop_path, encoding="utf-8").read()
    except OSError as exc:
        ERRORS.append(f"V20: stop-verification-gate.py unreadable: {exc}")
        stop_src = ""
    cfg_block = ""
    start = stop_src.find("DEFAULT_CFG")
    end = stop_src.find("CODE_EXTENSIONS")
    if start >= 0 and end > start:
        cfg_block = stop_src[start:end]
    for key in ("require_dual_graph_before_review", "parallel_review"):
        if key not in cfg_block:
            ERRORS.append(f"V20: stop-verification-gate DEFAULT_CFG 未消费 {key}")
    if "ensure_dual_graph_before_review" not in stop_src:
        ERRORS.append("V20: stop-verification-gate 缺少 ensure_dual_graph_before_review")

    reviewers = set()
    for spec in scenarios.values():
        if isinstance(spec, dict):
            reviewers.update((spec.get("quality") or {}).get("review") or [])
    reviewers.update(qg.get("reviewer_agents") or [])
    reviewers.discard("codex-reviewer")
    for name in sorted(reviewers):
        path = os.path.join(agents_dir, f"{name}.md")
        if not os.path.isfile(path):
            continue
        try:
            head = open(path, encoding="utf-8").read(800)
        except OSError:
            continue
        fm = ""
        if head.startswith("---"):
            parts = head.split("---", 2)
            fm = parts[1] if len(parts) > 2 else ""
        else:
            fm = head
        if "model: inherit" not in fm:
            ERRORS.append(f"V20: 审查者 {name} 缺 model: inherit")

    if not any(e.startswith("V20:") for e in ERRORS):
        print(f"  V20: scenario-router ({len(scenarios)}) + harness-capabilities OK ✓")


if __name__ == "__main__":
    sys.exit(main())
