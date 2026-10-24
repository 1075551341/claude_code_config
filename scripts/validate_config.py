#!/usr/bin/env python3
"""配置一致性校验 — V1-V21 共 21 项静态检查（结构/铁律/hook/MCP/INDEX/工具链/工作流主干）。

命令：
    python scripts/validate_config.py        # 全量校验，有 ERROR 时退出码 1
    pwsh -File scripts/check.ps1             # 上层健康检查，内部会调用本脚本

检查项：V1 触发词冲突 / V2 agent 职责重叠 / V3 CORE.md / V4 铁律一致 /
V5 MANIFEST 完整 / V6 MCP 安全 / V7 分层隔离 / V8 文件引用 / V9 deny 路径 /
V10-V12+V17 裸 except 与 R16 / V13-V14 Cursor Guard / V15 skill loading_tier /
V16 codegraph mandate / V17 autoCompactWindow / V18 codebase-memory 禁用 /
V19 三大 INDEX 与磁盘双向一致 / V20 工具链地板（pwsh 7.5 / pnpm；无 5.1 回退）/
V21 工作流主干 config/workflow.yaml 校验 + 派生内容无漂移 + 无模型/推理强度绑定（scripts/workflow.py check）。

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

BASE = os.environ.get("CLAUDE_HOME") or os.path.join(
    os.environ.get("USERPROFILE") or os.environ.get("HOME", ""),
    ".claude",
)
ERRORS = []
WARNINGS = []
INFO = []

# V20: MCP/JSON spawn of Windows PowerShell 5.1 (any spacing/case / .exe)
V20_POWERSHELL_COMMAND_RE = re.compile(
    r"""["']command["']\s*:\s*["']powershell(?:\.exe)?["']""",
    re.IGNORECASE,
)
V20_SYNC_SPAWN_PS_RE = re.compile(
    r"""(?:which\(|args\s*=\s*\[[^\]]*)["']powershell(?:\.exe)?["']""",
    re.IGNORECASE | re.DOTALL,
)
# Control-flow fallbacks in live scripts (mentioning npm/powershell in comments is OK)
V20_SCRIPT_PNPM_NPM_FALLBACK_RE = re.compile(
    r"(?is)(?:-not|!)\s*\(?\s*Get-Command\s+['\"]?pnpm\b"
    r"[\s\S]{0,400}?\bnpm\s+(?:install|i\b|run\b|exec\b|-g\b)",
)
V20_SCRIPT_PWSH_PS_FALLBACK_RE = re.compile(
    r"(?is)(?:-not|!)\s*\(?\s*Get-Command\s+['\"]?pwsh\b"
    r"[\s\S]{0,400}?powershell(?:\.exe)?",
)

# v13: 9 agents = 2 stage roles + 7 independent reviewers (config/workflow.yaml SSOT)
STAGE_AGENTS = {"planner", "change-implementer"}
REVIEW_AGENTS = {
    "eng-reviewer", "ceo-reviewer", "designer", "dx-reviewer", "qa",
    "security-reviewer", "cross-model-reviewer",
}
REQUIRED_AGENTS = STAGE_AGENTS | REVIEW_AGENTS
GLOBAL_AGENTS_MAX = 9

P0_SKILLS = {
    "using-superpowers", "brainstorming", "change-impact-analysis",
    "verification-before-completion", "systematic-debugging", "task-triage",
}
# superpowers 同名：本地定制或薄壳，删除会让上游插件版生效
WORKFLOW_SKILLS = {
    "writing-plans", "executing-plans", "test-driven-development",
    "subagent-driven-development", "using-git-worktrees", "receiving-code-review",
    "requesting-code-review", "finishing-a-development-branch",
}
SUPPORT_SKILLS = {
    "memory-compression", "spec-validation", "caveman-compress",
    "design-pipeline", "ship", "workstream-management", "adr-management",
}
REQUIRED_SKILLS = P0_SKILLS | WORKFLOW_SKILLS | SUPPORT_SKILLS
GLOBAL_SKILLS_MAX = 26

GLOBAL_RULES = {"CORE.md", "AGENTS.md", "GIT.md", "MCP.md", "OPENSPEC.md", "SECURITY.md"}
GLOBAL_RULES_MAX = 6
IRON_LAWS = ("R1", "R3", "R4", "R5", "R8", "R9", "R11", "R12", "R13", "R14",
             "R15", "R16", "R17", "R18", "R19", "R20")
LIVE_POLICY_PATHS = (
    "CLAUDE.md",
    "rules/CORE.md",
    "rules/AGENTS.md",
    "skills/verification-before-completion/SKILL.md",
    "skills/executing-plans/SKILL.md",
    "skills/task-triage/SKILL.md",
    "skills/requesting-code-review/SKILL.md",
    "skills/change-impact-analysis/SKILL.md",
    "templates/cursor-guard/rules/CURSOR-EDITOR.mdc",
    "docs/DEV_FLOW.md",
    "commands/verify.md",
    "commands/review.md",
    "agents/eng-reviewer.md",
    "hooks/_lib/gate_messages.md",
)
# 旧政策残留：只读/简单免审、5 轮、轮次耗尽仍算完成
LIVE_POLICY_BANS = ("只读免审", "最多 5 轮", "放行并标 DONE_WITH_CONCERNS", "模型匹配低")


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
    for tag in IRON_LAWS:
        if not re.search(rf"(?<![A-Za-z0-9]){tag}(?![0-9])", claude + "\n" + core):
            ERRORS.append(f"V4: {tag} missing from CLAUDE.md or CORE.md")
    for tag in ("R17", "R18", "R20"):
        if tag not in claude or tag not in core:
            ERRORS.append(f"V4: {tag} must appear in both CLAUDE.md and CORE.md")
    verif_path = os.path.join(BASE, "skills", "verification-before-completion", "SKILL.md")
    extra = core
    if os.path.exists(verif_path):
        with open(verif_path, "r", encoding="utf-8") as fh:
            extra = core + "\n" + fh.read()
    for kw in ("漏改", "原功能", "文档/注释", "问题是否解决"):
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
        "change_implementer", "workflow_spine",
    }
    missing = required - set(concerns.keys())
    if missing:
        WARNINGS.append(f"V5: Missing MANIFEST concerns: {sorted(missing)}")
    agents_max = manifest.get("global_agents_max", GLOBAL_AGENTS_MAX)
    skills_max = manifest.get("global_skills_max", GLOBAL_SKILLS_MAX)
    rules_max = manifest.get("global_rules_max", GLOBAL_RULES_MAX)
    if agents_max != GLOBAL_AGENTS_MAX or skills_max != GLOBAL_SKILLS_MAX:
        WARNINGS.append(
            f"V5: MANIFEST limits ({agents_max}/{skills_max}) "
            f"!= validator ({GLOBAL_AGENTS_MAX}/{GLOBAL_SKILLS_MAX})"
        )
    if rules_max != GLOBAL_RULES_MAX:
        WARNINGS.append(
            f"V5: MANIFEST global_rules_max ({rules_max}) != validator ({GLOBAL_RULES_MAX})"
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
        expected = {
            "codegraph",
            "code-review-graph",
            "serena",
            "everything",
            "grep",
        }
        if seen != expected:
            ERRORS.append(
                f"V6: .mcp.json resident {sorted(seen)} != {sorted(expected)}"
            )
        if "CODEGRAPH_MCP_TOOLS" in content:
            ERRORS.append("V6: CODEGRAPH_MCP_TOOLS must not be set (impact not exposed)")
        if "everything-mcp==1.0.6" not in content or "mcp<2" not in content:
            ERRORS.append("V6: everything must pin everything-mcp==1.0.6 and mcp<2")
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
    if len(rule_files) > GLOBAL_RULES_MAX:
        ERRORS.append(f"Too many global rules: {len(rule_files)} > {GLOBAL_RULES_MAX}")

    claude_path = os.path.join(BASE, "CLAUDE.md")
    line_count = 0
    if os.path.exists(claude_path):
        with open(claude_path, "r", encoding="utf-8") as fh:
            claude_md = fh.read()
        line_count = claude_md.count("\n") + 1
    if line_count > 200:
        ERRORS.append(f"CLAUDE.md too long: {line_count} lines > 200")

    commands_dir = os.path.join(BASE, "commands")
    if os.path.isdir(commands_dir):
        required_commands = {
            "discuss", "plan", "execute", "verify", "ship", "review",
            "compact", "propose", "apply", "archive",
            "workstream", "adr", "deep-research", "sync",
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
    check_live_policy_bans()
    check_v17_bare_except_extended()
    check_v17_auto_compact_window()
    check_v18_codebase_memory_optional()
    check_v19_index_disk_sync()
    check_v20_toolchain()
    check_v21_workflow_spine()

    report(
        agents=len(agent_names),
        skills=len(skill_names),
        rules=len(rule_files),
        claude_lines=line_count,
    )
    return 1 if ERRORS else 0


def report(agents=0, skills=0, rules=0, claude_lines=0):
    print("=== .claude v13 VALIDATION (21 checks) ===")
    print(f"Agents: {agents} | Skills: {skills} | Rules: {rules}")
    print(f"CLAUDE.md: {claude_lines} lines (max 200)")
    print()
    for check_name in [
        "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
        "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18",
        "V19", "V20", "V21",
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
        "r20-capture.py",
        "stop-verification-gate.py",
        "stop-session-summary.py", "stop-readme-updater.py",
    ]
    # v12: pre-tmux-reminder / pre-loop-guard / pre-suggest-compact / stop-context-monitor 已删除
    optional_hooks = [
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
    try:
        with open(hooks_json, "r", encoding="utf-8-sig") as fh:
            hj = json.load(fh)
        explore_matcher = ""
        for item in (hj.get("hooks") or {}).get("preToolUse") or []:
            if "explore_router.py" in str(item.get("command") or ""):
                explore_matcher = str(item.get("matcher") or "")
                break
        if "CallDynamicTool" not in explore_matcher or "everything" not in explore_matcher:
            ERRORS.append(
                "V14: explore_router matcher must include CallDynamicTool and everything"
            )
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        ERRORS.append(f"V14: explore_router matcher unreadable: {exc}")
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

    def _section_after(text: str, heading: str | None) -> str:
        if not heading:
            return text
        idx = text.find(heading)
        if idx < 0:
            return ""
        rest = text[idx:]
        nxt = rest.find("\n## ", 1)
        return rest if nxt < 0 else rest[:nxt]

    if expected:
        live_stamps = (
            ("hooks/README.md", "## Cursor 编辑器", r"Cursor Guard v(\d+\.\d+\.\d+)"),
            ("README.md", "## 版本", r"当前：[^\n]*Guard (\d+\.\d+\.\d+)"),
            ("docs/CURSOR_EDITOR_SETUP.md", None, r"\*\*v(\d+\.\d+\.\d+)\*\*"),
            ("SPEC.md", None, r"Cursor Guard 运行时 23（v(\d+\.\d+\.\d+)）"),
            ("docs/SYNC_GUIDE.md", "## 版本史", r"Guard \**(\d+\.\d+\.\d+)"),
        )
        for rel, heading, pat in live_stamps:
            path = os.path.join(BASE, rel)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    body = fh.read()
            except OSError as exc:
                ERRORS.append(f"V14: cannot read {rel}: {exc}")
                continue
            chunk = _section_after(body, heading)
            if heading and not chunk:
                ERRORS.append(f"V14: {rel} missing heading {heading!r}")
                continue
            found = re.search(pat, chunk)
            if not found:
                ERRORS.append(f"V14: {rel} missing live Guard version stamp")
            elif found.group(1) != expected:
                ERRORS.append(
                    f"V14: {rel} live Guard {found.group(1)!r} expected {expected!r}"
                )
        hist = (
            ("hooks/README.md", r"\*\*v5\.19 变更[^\n]*1\.2\.16"),
            ("docs/SYNC_GUIDE.md", r"v20\.21[^\n]*Guard 1\.2\.16"),
            ("docs/CURSOR_EDITOR_SETUP.md", r"\*\*v1\.2\.16\*\*"),
        )
        for rel, pat in hist:
            path = os.path.join(BASE, rel)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    body = fh.read()
            except OSError as exc:
                ERRORS.append(f"V14: cannot read {rel} (history): {exc}")
                continue
            if not re.search(pat, body):
                ERRORS.append(
                    f"V14: {rel} missing historical Guard 1.2.16 stamp ({pat})"
                )
    if not missing and os.path.isfile(doc) and os.path.isfile(rule):
        print(f"  V14: Cursor Guard v{gv} ({len(v11_hooks)} hooks + docs) ✓")


def check_v17_auto_compact_window():
    """V17: autoCompactWindow 有效；模型窗口可确认时不得超过且应一致（未知模型以调用方设置为准）."""
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
            known_context_tokens,
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

    model_max = known_context_tokens(model)

    if env_window is not None:
        WARNINGS.append(
            "V17: remove env.CLAUDE_CODE_AUTO_COMPACT_WINDOW — "
            "use autoCompactWindow + config/model-context-windows.json (动态解析)"
        )
        try:
            if model_max is not None and int(env_window) > model_max:
                ERRORS.append(
                    f"V17: CLAUDE_CODE_AUTO_COMPACT_WINDOW={env_window} exceeds "
                    f"model max {model_max} for {model!r}"
                )
        except (TypeError, ValueError):
            pass

    if not isinstance(window, int) or window <= 0:
        ERRORS.append(f"V17: autoCompactWindow={window!r} invalid — run scripts/sync-compact-window.py")
    elif model_max is not None and window > model_max:
        ERRORS.append(
            f"V17: autoCompactWindow={window} exceeds model max {model_max} for {model!r}"
        )
    elif model_max is not None and window != model_max:
        WARNINGS.append(
            f"V17: autoCompactWindow={window} != known max {model_max} for {model!r} "
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
        print(f"  V17: autoCompactWindow {window} / model {model!r} max {model_max or 'caller-defined'} ✓")


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
        "require_refresh_before_review",
    )
    missing = [k for k in required if k not in gf]
    if missing:
        ERRORS.append(f"V16: graph_freshness missing keys: {', '.join(missing)}")
        return
    if not bool(gf.get("require_refresh_before_review")):
        ERRORS.append("V16: graph_freshness.require_refresh_before_review must be true")
    spine_path = os.path.join(BASE, "config", "workflow.yaml")
    try:
        with open(qg_path, "r", encoding="utf-8") as fh:
            vg = json.load(fh).get("verification_gate") or {}
        if not yaml:
            WARNINGS.append("V16: PyYAML missing — skipped quality_gates vs config/workflow.yaml review comparison")
            return
        review = {}
        if os.path.isfile(spine_path):
            with open(spine_path, "r", encoding="utf-8") as fh:
                review = (yaml.safe_load(fh) or {}).get("review") or {}
        for gate_key, spine_key in (("review_max_rounds", "max_rounds"), ("max_blocks", "max_blocks")):
            want = review.get(spine_key)
            if want is None:
                ERRORS.append(f"V16: config/workflow.yaml review.{spine_key} missing")
            elif int(vg.get(gate_key) or 0) != int(want):
                ERRORS.append(
                    f"V16: verification_gate.{gate_key}={vg.get(gate_key)!r} != workflow.yaml "
                    f"review.{spine_key}={want!r} — run scripts/workflow.py render"
                )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        ERRORS.append(f"V16: verification_gate unreadable: {exc}")
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
        if "mcp__everything__" not in text:
            ERRORS.append("V16: hooks.snippet.json missing mcp__everything__ matcher")
        if '"timeout": 120000' not in text and '"timeout":120000' not in text:
            WARNINGS.append("V16: hooks.snippet.json SessionStart timeout 不是 120000ms")
    except OSError as exc:
        WARNINGS.append(f"V16: hooks.snippet.json unreadable: {exc}")
    print("  V16: graph_freshness timeouts + snippet ✓")


def check_live_policy_bans():
    """现行政策文件禁止旧政策残留（免审旁路 / 5 轮 / 耗尽仍完成 / 模型匹配；史留 CHANGELOG）。"""
    for rel in LIVE_POLICY_PATHS:
        path = os.path.join(BASE, rel)
        if not os.path.isfile(path):
            ERRORS.append(f"V16: live policy missing {rel}")
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            ERRORS.append(f"V16: cannot read {rel}: {exc}")
            continue
        for ban in LIVE_POLICY_BANS:
            if ban in text:
                ERRORS.append(f"V16: {rel} hardcodes {ban!r}")


def check_v17_bare_except_extended():
    """V17: R16 扩展 — 裸 except 扫描（hooks/ + scripts/，含 bare except: 和 except Exception:）"""
    import re as re_mod
    import glob as glob_mod

    # Infrastructure files exempt from V17 (launchers, guards)
    INFRA_EXEMPT = {
        "_editor_hook_launcher.py",
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


def check_v20_toolchain():
    """V20: 工具链 SSOT — pwsh 7.5 / pnpm；live 脚本无 5.1 Requires；which_pwsh 不回退 powershell。"""
    path = os.path.join(BASE, "config", "toolchain.yaml")
    if not os.path.isfile(path):
        ERRORS.append("V20: config/toolchain.yaml missing")
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        ERRORS.append(f"V20: cannot read toolchain.yaml: {exc}")
        return
    data = {}
    if yaml:
        try:
            loaded = yaml.safe_load(raw)
            if isinstance(loaded, dict):
                data = loaded
        except yaml.YAMLError as exc:
            ERRORS.append(f"V20: toolchain.yaml unreadable: {exc}")
            return
    windows = data.get("windows") if isinstance(data.get("windows"), dict) else {}
    node = data.get("node") if isinstance(data.get("node"), dict) else {}
    ps_min = str(windows.get("powershell_min") or "")
    pkg = str(node.get("package_manager") or "")
    if not ps_min:
        m = re.search(r'powershell_min:\s*"([^"]+)"', raw)
        ps_min = m.group(1) if m else ""
    if not pkg:
        m = re.search(r"package_manager:\s*(\S+)", raw)
        pkg = (m.group(1) if m else "").strip()
    if ps_min != "7.5":
        ERRORS.append(f"V20: windows.powershell_min={ps_min!r} expected '7.5'")
    if pkg != "pnpm":
        ERRORS.append(f"V20: node.package_manager={pkg!r} expected 'pnpm'")
    python_cfg = data.get("python") if isinstance(data.get("python"), dict) else {}
    missing_tool = str(data.get("missing_tool") or "")
    pnpm_major = str(node.get("pnpm_major") or "")
    py_installer = str(python_cfg.get("installer") or "")
    if not missing_tool:
        m = re.search(r"missing_tool:\s*(\S+)", raw)
        missing_tool = (m.group(1) if m else "").strip()
    if not pnpm_major:
        m = re.search(r'pnpm_major:\s*"([^"]+)"', raw)
        pnpm_major = m.group(1) if m else ""
    if not py_installer:
        m = re.search(r"installer:\s*(\S+)", raw)
        py_installer = (m.group(1) if m else "").strip()
    if missing_tool != "BLOCKED":
        ERRORS.append(f"V20: missing_tool={missing_tool!r} expected 'BLOCKED'")
    if pnpm_major != "11":
        ERRORS.append(f"V20: node.pnpm_major={pnpm_major!r} expected '11'")
    if py_installer != "uv":
        ERRORS.append(f"V20: python.installer={py_installer!r} expected 'uv'")

    for rel in (".mcp.json", "docs/CURSOR_MCP_PROFILE.md"):
        live_path = os.path.join(BASE, rel)
        try:
            with open(live_path, "r", encoding="utf-8") as fh:
                live = fh.read()
        except OSError as exc:
            ERRORS.append(f"V20: cannot read {rel}: {exc}")
            continue
        if V20_POWERSHELL_COMMAND_RE.search(live):
            ERRORS.append(f"V20: {rel} still has command powershell; must spawn pwsh")

    sync_runner = os.path.join(
        BASE, "templates", "cursor-guard", "hooks", "_lib", "sync_runner.py"
    )
    try:
        with open(sync_runner, "r", encoding="utf-8") as fh:
            runner = fh.read()
    except OSError as exc:
        ERRORS.append(f"V20: cannot read sync_runner.py: {exc}")
    else:
        if V20_SYNC_SPAWN_PS_RE.search(runner):
            ERRORS.append("V20: Guard sync_runner must not spawn powershell")
        if "def resolve_pwsh" not in runner:
            ERRORS.append("V20: Guard sync_runner must define resolve_pwsh")
        if "shutil.which(\"pwsh\")" not in runner and "shutil.which('pwsh')" not in runner:
            ERRORS.append("V20: Guard sync_runner must resolve pwsh")

    shell_patterns = os.path.join(
        BASE, "templates", "cursor-guard", "hooks", "_lib", "shell_patterns.py"
    )
    try:
        with open(shell_patterns, "r", encoding="utf-8") as fh:
            patterns = fh.read()
    except OSError as exc:
        ERRORS.append(f"V20: cannot read shell_patterns.py: {exc}")
    else:
        if r"powershell(?:\.exe)?" not in patterns:
            ERRORS.append(
                "V20: Guard shell_patterns WARN must include powershell (align pre-bash-guard)"
            )

    scripts_dir = os.path.join(BASE, "scripts")
    if os.path.isdir(scripts_dir):
        for name in sorted(os.listdir(scripts_dir)):
            if not name.endswith(".ps1"):
                continue
            script_path = os.path.join(scripts_dir, name)
            try:
                with open(script_path, "r", encoding="utf-8-sig") as fh:
                    text = fh.read()
            except OSError as exc:
                ERRORS.append(f"V20: cannot read scripts/{name}: {exc}")
                continue
            if "#Requires -Version 5.1" in text:
                ERRORS.append(f"V20: scripts/{name} still has #Requires -Version 5.1")
            if "#Requires -Version 7.5" not in text:
                ERRORS.append(f"V20: scripts/{name} missing #Requires -Version 7.5")
            if V20_SCRIPT_PNPM_NPM_FALLBACK_RE.search(text):
                ERRORS.append(
                    f"V20: scripts/{name} falls back to npm when pnpm is missing"
                )
            if V20_SCRIPT_PWSH_PS_FALLBACK_RE.search(text):
                ERRORS.append(
                    f"V20: scripts/{name} falls back to powershell when pwsh is missing"
                )

    gf = os.path.join(BASE, "hooks", "_lib", "graph_freshness.py")
    try:
        with open(gf, "r", encoding="utf-8") as fh:
            src = fh.read()
    except OSError as exc:
        ERRORS.append(f"V20: cannot read graph_freshness.py: {exc}")
        return
    m = re.search(r"def which_pwsh\([^)]*\)[^\n]*\n((?:[ \t].*\n)+)", src)
    body = m.group(1) if m else ""
    if not body:
        ERRORS.append("V20: which_pwsh definition not found")
    else:
        if 'which_tool("powershell")' in body or "which_tool('powershell')" in body:
            ERRORS.append("V20: which_pwsh must not fall back to powershell")
        if 'which_tool("pwsh")' not in body and "which_tool('pwsh')" not in body:
            ERRORS.append('V20: which_pwsh must call which_tool("pwsh")')

    claude_path = os.path.join(BASE, "CLAUDE.md")
    try:
        with open(claude_path, "r", encoding="utf-8") as fh:
            claude = fh.read()
    except OSError as exc:
        ERRORS.append(f"V20: cannot read CLAUDE.md: {exc}")
        return
    r15 = re.search(r"R15[^|\n]+", claude)
    if not r15:
        ERRORS.append("V20: CLAUDE.md R15 entry missing")
    else:
        row = r15.group(0)
        if "兜底" in row:
            ERRORS.append("V20: CLAUDE.md R15 must not contain 兜底")
        if "pnpm" not in row:
            ERRORS.append("V20: CLAUDE.md R15 must mention pnpm")
    print("  V20: toolchain floors + pwsh-only which_pwsh ✓")


def check_v21_workflow_spine():
    """V21: config/workflow.yaml 是唯一调度面 — 校验 schema，并要求全部派生内容与之一致。"""
    if not yaml:
        WARNINGS.append("V21: PyYAML not installed, skipping workflow spine check")
        return
    script = os.path.join(BASE, "scripts", "workflow.py")
    if not os.path.isfile(os.path.join(BASE, "config", "workflow.yaml")):
        ERRORS.append("V21: config/workflow.yaml missing")
        return
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("workflow_spine", script)
    if spec is None or spec.loader is None:
        ERRORS.append("V21: scripts/workflow.py missing")
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        root = Path(BASE)
        spine = mod.load_spine(root)
        errs = mod.validate(spine, root)
        for e in errs:
            ERRORS.append(f"V21: {e}")
        if errs:
            return
        drift = mod.diff_targets(root, mod.build_targets(root, spine))
        hits = mod.lint(root)
    except (OSError, ImportError, SyntaxError, ValueError, KeyError, TypeError,
            getattr(mod, "SpineError", ValueError), yaml.YAMLError) as exc:
        ERRORS.append(f"V21: workflow spine unreadable: {type(exc).__name__}: {exc}")
        return
    for rel in drift:
        ERRORS.append(f"V21: derived content drift in {rel.as_posix()} — run scripts/workflow.py render")
    for hit in hits:
        ERRORS.append(f"V21: model/effort binding: {hit}")
    if not drift and not hits:
        print("  V21: workflow spine valid, derived targets in sync, no model/effort binding ✓")

if __name__ == "__main__":
    sys.exit(main())
