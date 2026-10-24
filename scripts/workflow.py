#!/usr/bin/env python3
"""Workflow spine — 校验 config/workflow.yaml 并渲染全部派生内容。

命令：
    python scripts/workflow.py check                 # 校验 + 漂移检测（有漂移/错误 exit 1）
    python scripts/workflow.py render                # 写回全部派生目标
    python scripts/workflow.py show [--profile P]    # 打印模型档 / 角色路由 / 阶段与轨道
    python scripts/workflow.py apply-settings [--write] [--settings PATH]
                                                     # 把 profile 的模型键合并进 Claude settings.json

根目录：--root > $CLAUDE_HOME > 本脚本所在仓库。派生目标清单见 docs/DEV_FLOW.md。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("workflow.py: PyYAML required (uv pip install pyyaml)\n")
    sys.exit(2)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"workflow.py: stdout reconfigure failed: {exc}\n")

SPINE = Path("config") / "workflow.yaml"
EFFORTS = ("low", "medium", "high", "xhigh")
AGENT_MODELS = ("alias", "inherit")
GENERATED_NOTE = "派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改"
SNIPPET = Path("templates") / "claude-settings" / "model.snippet.json"
ALIAS_ENV = {
    "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
}


class SpineError(Exception):
    pass


# ── 加载与解析 ────────────────────────────────────────────────────


def default_root() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


def load_spine(root: Path) -> dict:
    path = root / SPINE
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SpineError(f"{SPINE}: top level must be a mapping")
    return data


class Resolved:
    """profile + roles 解析结果：每个角色最终用什么模型/effort。"""

    def __init__(self, spine: dict, profile_name: str | None = None):
        models = spine["models"]
        self.spine = spine
        self.profile_name = profile_name or models["active_profile"]
        self.profile = models["profiles"][self.profile_name]
        self.tier_order = list(models["tier_order"])
        self.alias = models["claude_code_alias"]
        self.roles = spine["roles"]

    def tier_entry(self, tier: str) -> dict:
        return self.profile["tiers"][tier]

    def agent_model(self, role: str) -> str:
        if self.profile.get("agent_model") == "inherit":
            return "inherit"
        return self.alias[self.roles[role]["tier"]]

    def effort(self, role: str) -> str | None:
        if not self.profile.get("supports_effort"):
            return None
        return self.roles[role].get("effort")

    def concrete(self, role: str) -> str:
        return str(self.tier_entry(self.roles[role]["tier"]).get("claude_code", "inherit"))

    def cursor_slug(self, role: str) -> str:
        return str(self.tier_entry(self.roles[role]["tier"]).get("cursor", "inherit"))

    def reviewers(self) -> list[str]:
        out: list[str] = []
        for names in self.spine["review"]["routing"].values():
            for n in names:
                if n not in out:
                    out.append(n)
        return out


# ── 校验 ──────────────────────────────────────────────────────────


def _r20_module(root: Path):
    lib = root / "hooks" / "_lib"
    if not (lib / "r20_replay.py").is_file():
        return None
    sys.path.insert(0, str(lib))
    try:
        import r20_replay  # noqa: WPS433
    finally:
        sys.path.pop(0)
    return r20_replay


def validate(spine: dict, root: Path) -> list[str]:
    errs: list[str] = []
    for key in ("models", "roles", "stages", "tracks", "quality", "review", "triage", "constraints"):
        if key not in spine:
            errs.append(f"missing top-level key {key!r}")
    if errs:
        return errs

    models = spine["models"]
    tiers = list(models.get("tier_order") or [])
    profiles = models.get("profiles") or {}
    if models.get("active_profile") not in profiles:
        errs.append(f"models.active_profile {models.get('active_profile')!r} not in profiles")
    if set(models.get("claude_code_alias") or {}) != set(tiers):
        errs.append("models.claude_code_alias keys must equal tier_order")
    for alias in (models.get("claude_code_alias") or {}).values():
        if alias not in ALIAS_ENV:
            errs.append(f"claude_code_alias {alias!r} not one of {sorted(ALIAS_ENV)}")
    for pname, prof in profiles.items():
        if prof.get("agent_model") not in AGENT_MODELS:
            errs.append(f"profile {pname}: agent_model must be one of {AGENT_MODELS}")
        ptiers = prof.get("tiers") or {}
        if set(ptiers) != set(tiers):
            errs.append(f"profile {pname}: tiers {sorted(ptiers)} != tier_order {sorted(tiers)}")
        for tname, entry in ptiers.items():
            if not entry.get("claude_code") or not entry.get("cursor"):
                errs.append(f"profile {pname}.{tname}: claude_code and cursor required")
            ctx = entry.get("context_tokens")
            if ctx is not None and (not isinstance(ctx, int) or ctx <= 0):
                errs.append(f"profile {pname}.{tname}: context_tokens must be positive int")
        if prof.get("agent_model") == "alias":
            for tname, entry in ptiers.items():
                if entry.get("claude_code") == "inherit":
                    errs.append(f"profile {pname}.{tname}: alias profile needs a concrete claude_code model")

    agents_dir = root / "agents"
    disk_agents = {p.stem for p in agents_dir.glob("*.md") if p.name != "README.md"}
    roles = spine["roles"]
    if "session" not in roles:
        errs.append("roles.session required")
    for rname, role in roles.items():
        if role.get("tier") not in tiers:
            errs.append(f"roles.{rname}: tier {role.get('tier')!r} not in tier_order")
        if role.get("effort") is not None and role.get("effort") not in EFFORTS:
            errs.append(f"roles.{rname}: effort {role.get('effort')!r} not in {EFFORTS}")
        if rname != "session" and rname not in disk_agents:
            errs.append(f"roles.{rname}: agents/{rname}.md missing")
    for agent in sorted(disk_agents - set(roles)):
        errs.append(f"agents/{agent}.md has no roles entry (every agent must be routed)")

    review = spine["review"]
    routed = []
    for group, names in (review.get("routing") or {}).items():
        for n in names:
            routed.append(n)
            if n not in roles:
                errs.append(f"review.routing.{group}: {n!r} has no role")
    if "eng-reviewer" not in (review.get("routing") or {}).get("always", []):
        errs.append("review.routing.always must include eng-reviewer")
    impl = spine["constraints"].get("reviewer_min_tier_of")
    if impl in roles and tiers:
        floor = tiers.index(roles[impl]["tier"]) if roles[impl]["tier"] in tiers else 0
        for n in routed:
            if n in roles and roles[n].get("tier") in tiers and tiers.index(roles[n]["tier"]) < floor:
                errs.append(f"reviewer {n} tier {roles[n]['tier']} < {impl} tier {roles[impl]['tier']}")
    for key in ("max_rounds", "max_blocks", "min_files"):
        if not isinstance(review.get(key), int) or review[key] < 1:
            errs.append(f"review.{key} must be int ≥ 1")
    if review.get("refresh_graph_before_review") is not True:
        errs.append("review.refresh_graph_before_review must be true (hooks graph gate + V16 require it)")
    if review.get("verdicts") != ["PASS", "NEEDS-CHANGES"]:
        errs.append("review.verdicts must be [PASS, NEEDS-CHANGES] (hooks parse these)")
    names = tuple(d.get("name") for d in review.get("dimensions") or [])
    r20 = _r20_module(root)
    if r20 is not None:
        mech = ("满足",) + tuple(r20._REQUIRED)
        if names != mech:
            errs.append(f"review.dimensions {names} != hooks/_lib/r20_replay.py {mech}")
        configured = set(routed) | set(review.get("legacy_reviewer_names") or [])
        if configured != set(r20.DEFAULT_REVIEWER_AGENTS):
            errs.append(
                f"review.routing + legacy_reviewer_names {sorted(configured)} != "
                f"hooks/_lib/r20_replay.py DEFAULT_REVIEWER_AGENTS {sorted(r20.DEFAULT_REVIEWER_AGENTS)}"
            )

    stages = spine["stages"]
    for sid, st in stages.items():
        if not (root / "skills" / st.get("skill", "") / "SKILL.md").is_file():
            errs.append(f"stages.{sid}: skills/{st.get('skill')}/SKILL.md missing")
        if st.get("command") and not (root / "commands" / f"{st['command']}.md").is_file():
            errs.append(f"stages.{sid}: commands/{st['command']}.md missing")
        if st.get("role") not in roles:
            errs.append(f"stages.{sid}: role {st.get('role')!r} not in roles")
        if not st.get("exit"):
            errs.append(f"stages.{sid}: exit gates required")
    for tname, seq in spine["tracks"].items():
        for sid in seq:
            if sid not in stages:
                errs.append(f"tracks.{tname}: unknown stage {sid!r}")
            elif stages[sid].get("on_demand"):
                errs.append(f"tracks.{tname}: on_demand stage {sid!r} must not be in a track (R19)")
    triage = spine["triage"]
    for k, t in {**triage.get("required_tier", {}), **triage.get("task_priority_tiers", {})}.items():
        if t not in tiers:
            errs.append(f"triage.{k}: tier {t!r} not in tier_order")
    return errs


# ── 渲染原语 ──────────────────────────────────────────────────────

_BLOCK_RE = "<!-- spine:{name} -->\n(.*?)<!-- /spine:{name} -->"


def replace_block(text: str, name: str, body: str, path: str) -> str:
    pattern = re.compile(_BLOCK_RE.format(name=re.escape(name)), re.S)
    if not pattern.search(text):
        raise SpineError(f"{path}: marker <!-- spine:{name} --> missing")
    block = f"<!-- spine:{name} -->\n{body.rstrip()}\n<!-- /spine:{name} -->"
    return pattern.sub(lambda _m: block, text, count=1)


def set_frontmatter(text: str, updates: dict[str, str | None], path: str) -> str:
    if not text.startswith("---\n"):
        raise SpineError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise SpineError(f"{path}: unterminated frontmatter")
    lines = text[4:end].split("\n")
    anchor = next((i for i, ln in enumerate(lines) if ln.startswith("description:")), len(lines) - 1)
    while anchor + 1 < len(lines) and lines[anchor + 1][:1] in (" ", "\t"):
        anchor += 1
    for key, value in updates.items():
        idx = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
        if value is None:
            if idx is not None:
                del lines[idx]
                if idx <= anchor:
                    anchor -= 1
            continue
        line = f"{key}: {value}"
        if idx is not None:
            lines[idx] = line
            anchor = idx
        else:
            anchor += 1
            lines.insert(anchor, line)
    return "---\n" + "\n".join(lines) + text[end:]


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


# ── 派生内容 ──────────────────────────────────────────────────────


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _role_cell(r: Resolved, role: str) -> str:
    tier = r.roles[role]["tier"]
    eff = r.effort(role)
    return f"{role}（{tier}{' / ' + eff if eff else ''}）"


def body_review_contract(spine: dict) -> str:
    rv = spine["review"]
    dims = rv["dimensions"]
    line = " / ".join(d["name"] for d in dims[:-1]) + f" / **{dims[-1]['name']}**（{dims[-1]['hint']}）"
    return "\n".join([
        f"## 审查契约（{GENERATED_NOTE}）",
        "",
        "- 只找问题：禁止 Write / Edit / Shell 改文件，禁止贴可粘贴补丁；修复 → `change-implementer`。",
        "- 对照 **原始要求 + 当前 diff + 本轮新鲜图谱**（主会话已在 last_edit 之后刷新），扫完影响面一次列全再下结论；"
        "每轮全新开审，禁止 resume，上轮清单不得限定范围。",
        f"- 结论行只填其一：`{rv['verdicts'][0]}` | `{rv['verdicts'][1]}`；有任何必须修项即 `{rv['verdicts'][1]}`。",
        f"- 七维缺任一项本轮无效：{line}",
    ])


def body_ready_contract(spine: dict) -> str:
    q = spine["quality"]
    out = [f"## 一次通过契约（{GENERATED_NOTE}）", "", "**就绪定义**（缺一项不开工，回主会话补齐）："]
    out += [f"- {x}" for x in q["definition_of_ready"]]
    out += ["", "**交审前自检**（与审查者同一份清单）："]
    out += [f"- {x}" for x in q["self_check"]]
    return "\n".join(out)


def body_stage_gate(r: Resolved, sid: str) -> str:
    st = r.spine["stages"][sid]
    out = [
        f"## 门控（{GENERATED_NOTE}）",
        "",
        f"- 阶段：{st['label']} | skill：`skills/{st['skill']}/SKILL.md` | 角色：{_role_cell(r, st['role'])}",
    ]
    if st.get("entry"):
        out.append("- 进入：" + "；".join(st["entry"]))
    out.append("- 退出（全部满足才进入下一阶段）：")
    out += [f"  - {x}" for x in st["exit"]]
    if st["skill"] == "verification-before-completion":
        out.append("- verify_tier：")
        out += [f"  - `{k}`：{v}" for k, v in r.spine["quality"]["verify_tiers"].items()]
    return "\n".join(out)


def body_flow(r: Resolved) -> str:
    sp = r.spine
    out = ["| 阶段 | 命令 | skill | 角色（档/effort） | 退出门 |", "| --- | --- | --- | --- | --- |"]
    for sid, st in sp["stages"].items():
        cmd = f"/{st['command']}" if st.get("command") else "—"
        gates = _cell("；".join(st["exit"]))
        out.append(f"| {st['label']} | {cmd} | {st['skill']} | {_role_cell(r, st['role'])} | {gates} |")
    out.append("")
    for tname, seq in sp["tracks"].items():
        out.append(f"- **{tname}**：" + " → ".join(sp["stages"][s]["label"] for s in seq))
    on_demand = [st["label"] for st in sp["stages"].values() if st.get("on_demand")]
    if on_demand:
        out.append(f"- **按需**：{'、'.join(on_demand)}（不在轨道内；用户明确要求时进入，R19）")
    rv = sp["review"]
    out.append(
        f"- **审查**：一轮 = 改 → 验 → 刷图 → 并行全新审查；上限 {rv['max_rounds']} 轮"
        f"（Stop 阻断 {rv['max_blocks']} 次）；必派 {', '.join(rv['routing']['always'])}。"
    )
    return "\n".join(out)


def body_models(r: Resolved) -> str:
    out = [
        f"当前 profile：**{r.profile_name}** — {r.profile.get('description', '')}",
        "",
        "| 档位 | Claude Code 别名 → 模型 | Cursor slug | 上下文 |",
        "| --- | --- | --- | --- |",
    ]
    for t in reversed(r.tier_order):
        e = r.tier_entry(t)
        ctx = e.get("context_tokens")
        alias = "inherit" if r.profile.get("agent_model") == "inherit" else r.alias[t]
        out.append(f"| {t} | `{alias}` → `{e['claude_code']}` | `{e['cursor']}` | {ctx or '—'} |")
    return "\n".join(out)


def body_roles(r: Resolved) -> str:
    out = ["| 角色 | 档位 | effort | Claude Code `model` | Cursor Task `model` |", "| --- | --- | --- | --- | --- |"]
    for role in r.roles:
        out.append(
            f"| {role} | {r.roles[role]['tier']} | {r.effort(role) or '—'} | "
            f"`{r.agent_model(role)}`（{r.concrete(role)}） | `{r.cursor_slug(role)}` |"
        )
    out += ["", "> effort 只作用于 Claude Code；Cursor slug 按档位固定（effort / fast 已编码在 slug 中）。"]
    return "\n".join(out)


def body_tier_map(r: Resolved) -> str:
    tri = r.spine["triage"]
    req = tri["required_tier"]
    out = [
        f"> {GENERATED_NOTE}。当前 profile：`{r.profile_name}`。",
        "",
        "| 档 | 当前 profile 模型（Claude Code / Cursor） |",
        "| --- | --- |",
    ]
    for t in reversed(r.tier_order):
        e = r.tier_entry(t)
        out.append(f"| `{t}` | `{e['claude_code']}` / `{e['cursor']}` |")
    out += [
        "",
        f"- 所需档：①–⑤ 全低 → `{req['all_low']}`；含中 → `{req['any_mid']}`；含高或黑名单 → `{req['any_high_or_blacklist']}`",
        f"- attempt ≥ {tri['attempt_escalation']} → 执行升档非简单 + verify_tier=全量",
    ]
    return "\n".join(out)


def body_priority_tiers(r: Resolved) -> str:
    out = [f"> {GENERATED_NOTE}。", "", "| 任务级别 | 档 | 当前模型 |", "| --- | --- | --- |"]
    for prio, t in r.spine["triage"]["task_priority_tiers"].items():
        out.append(f"| {prio} | `{t}` | `{r.tier_entry(t)['claude_code']}` |")
    out.append("")
    out.append("派发时：Claude Code `Task` 传档位别名（或 `inherit`）；Cursor 传上表 Cursor slug（见 CURSOR-EDITOR 派生表）。")
    return "\n".join(out)


def body_dimensions(spine: dict) -> str:
    out = [f"> {GENERATED_NOTE}。缺任一项视为本轮无效、不计 PASS。", ""]
    for i, d in enumerate(spine["review"]["dimensions"], 1):
        name = f"**{d['name']}**" if i == len(spine["review"]["dimensions"]) else d["name"]
        out.append(f"{i}. {name}（{d['hint']}）")
    return "\n".join(out)


def body_review_routing(r: Resolved) -> str:
    rv = r.spine["review"]
    width = max(len(k) for k in rv["routing"])
    lines = ["```"]
    for group, names in rv["routing"].items():
        prefix = "" if group == "always" else "+ "
        lines.append(f"{group.ljust(width)}  → {prefix}{', '.join(names)}")
    lines.append("```")
    lines.append("")
    lines.append(
        f"> {GENERATED_NOTE}。档位：审查者 ≥ `{r.spine['constraints']['reviewer_min_tier_of']}`；"
        f"旧名 {', '.join('`' + n + '`' for n in rv['legacy_reviewer_names'])} 仍被 hooks 识别为审查委派。"
    )
    return "\n".join(lines)


def body_derived() -> str:
    rows = [
        ("agents/*.md frontmatter", "`model` / `effort`（roles × active profile）"),
        ("审查者 agents `spine:review-contract`", "七维 + 结论 + 只读规则（review）"),
        ("change-implementer / planner `spine:ready-contract`", "就绪定义 + 交审自检（quality）"),
        ("commands/{discuss,plan,execute,verify,ship,compact}.md `spine:stage-gate`", "阶段进入/退出门（stages）"),
        ("CLAUDE.md / docs/DEV_FLOW.md `spine:flow`", "阶段表 + 轨道 + 审查轮次"),
        ("rules/AGENTS.md `spine:review-routing`", "审查路由（review.routing）"),
        ("skills/task-triage `spine:tier-map`", "⑥模型匹配档位（triage + profile）"),
        ("skills/subagent-driven-development `spine:priority-tiers`", "子任务优先级 → 档位"),
        ("skills/verification-before-completion `spine:dimensions`", "七维清单"),
        ("templates/cursor-guard/rules/CURSOR-EDITOR.mdc `spine:cursor-models`", "Cursor Task model slug 表"),
        ("config/quality_gates.json verification_gate", "轮次 / 阻断 / 最少文件 / 审查者名单 / 刷图"),
        ("templates/cursor-guard/guard-config.json verification.reviewer_agents", "Cursor 审查者名单"),
        ("config/model-context-windows.json model_tokens", "全部 profile 模型上下文"),
        ("templates/claude-settings/model.snippet.json", "settings.json 模型键（apply-settings 合并）"),
        ("templates/editor-graph-hooks/verify-gate.ts", "`review_max_rounds=<n>` 文案（review.max_rounds）"),
    ]
    out = ["| 目标 | 内容（来源节） |", "| --- | --- |"]
    out += [f"| {a} | {b} |" for a, b in rows]
    return "\n".join(out)


def settings_fragment(r: Resolved) -> dict:
    frag: dict = {}
    if r.profile.get("agent_model") == "alias":
        frag["model"] = r.agent_model("session")
        frag["env"] = {ALIAS_ENV[r.alias[t]]: r.tier_entry(t)["claude_code"] for t in reversed(r.tier_order)}
    eff = r.effort("session")
    if eff:
        frag["effortLevel"] = eff
    return frag


# ── 目标表 ────────────────────────────────────────────────────────

def build_targets(root: Path, r: Resolved) -> dict[Path, str]:
    """返回 {path: 期望内容}；只包含有派生内容的文件。"""
    sp = r.spine
    out: dict[Path, str] = {}

    def text_of(rel: Path) -> str:
        p = root / rel
        return out[rel] if rel in out else p.read_text(encoding="utf-8")

    for role in sp["roles"]:
        if role == "session":
            continue
        rel = Path("agents") / f"{role}.md"
        out[rel] = set_frontmatter(
            text_of(rel), {"model": r.agent_model(role), "effort": r.effort(role)}, str(rel)
        )
    for name in r.reviewers():
        rel = Path("agents") / f"{name}.md"
        out[rel] = replace_block(text_of(rel), "review-contract", body_review_contract(sp), str(rel))
    for name in ("change-implementer", "planner"):
        rel = Path("agents") / f"{name}.md"
        out[rel] = replace_block(text_of(rel), "ready-contract", body_ready_contract(sp), str(rel))
    for sid, st in sp["stages"].items():
        if st.get("command"):
            rel = Path("commands") / f"{st['command']}.md"
            out[rel] = replace_block(text_of(rel), "stage-gate", body_stage_gate(r, sid), str(rel))

    blocks = [
        (Path("CLAUDE.md"), "flow", body_flow(r)),
        (Path("CLAUDE.md"), "models", body_models(r)),
        (Path("docs") / "DEV_FLOW.md", "flow", body_flow(r)),
        (Path("docs") / "DEV_FLOW.md", "models", body_models(r)),
        (Path("docs") / "DEV_FLOW.md", "roles", body_roles(r)),
        (Path("docs") / "DEV_FLOW.md", "derived", body_derived()),
        (Path("rules") / "AGENTS.md", "review-routing", body_review_routing(r)),
        (Path("skills") / "task-triage" / "SKILL.md", "tier-map", body_tier_map(r)),
        (Path("skills") / "subagent-driven-development" / "SKILL.md", "priority-tiers", body_priority_tiers(r)),
        (Path("skills") / "verification-before-completion" / "SKILL.md", "dimensions", body_dimensions(sp)),
        (Path("templates") / "cursor-guard" / "rules" / "CURSOR-EDITOR.mdc", "cursor-models", body_roles(r)),
    ]
    for rel, name, body in blocks:
        out[rel] = replace_block(text_of(rel), name, body, str(rel))

    rv = sp["review"]
    reviewer_names = r.reviewers() + [n for n in rv["legacy_reviewer_names"] if n not in r.reviewers()]

    qg_rel = Path("config") / "quality_gates.json"
    qg = json.loads((root / qg_rel).read_text(encoding="utf-8"))
    vg = qg.setdefault("verification_gate", {})
    vg["max_blocks"] = rv["max_blocks"]
    vg["review_max_rounds"] = rv["max_rounds"]
    vg["require_reviewer_min_files"] = rv["min_files"]
    vg["require_refresh_before_review"] = bool(rv["refresh_graph_before_review"])
    vg["reviewer_agents"] = reviewer_names
    qg.setdefault("graph_freshness", {})["require_refresh_before_review"] = bool(rv["refresh_graph_before_review"])
    out[qg_rel] = dump_json(qg)

    gc_rel = Path("templates") / "cursor-guard" / "guard-config.json"
    gc = json.loads((root / gc_rel).read_text(encoding="utf-8-sig"))
    gc.setdefault("verification", {})["reviewer_agents"] = reviewer_names
    out[gc_rel] = dump_json(gc)

    mc_rel = Path("config") / "model-context-windows.json"
    mc = json.loads((root / mc_rel).read_text(encoding="utf-8"))
    table = mc.setdefault("model_tokens", {})
    for prof in sp["models"]["profiles"].values():
        for entry in prof["tiers"].values():
            model, ctx = entry.get("claude_code"), entry.get("context_tokens")
            if model and model != "inherit" and ctx:
                table[model] = ctx
    out[mc_rel] = dump_json(mc)

    vg_rel = Path("templates") / "editor-graph-hooks" / "verify-gate.ts"
    vg_text = text_of(vg_rel)
    if not re.search(r"review_max_rounds=\d+", vg_text):
        raise SpineError(f"{vg_rel}: review_max_rounds=<n> anchor missing")
    out[vg_rel] = re.sub(r"review_max_rounds=\d+", f"review_max_rounds={rv['max_rounds']}", vg_text)

    snippet = {
        "_comment": f"{GENERATED_NOTE}。合并：python scripts/workflow.py apply-settings --write",
        "_profile": r.profile_name,
        **settings_fragment(r),
    }
    out[SNIPPET] = dump_json(snippet)
    return out


def diff_targets(root: Path, targets: dict[Path, str]) -> list[Path]:
    drift = []
    for rel, want in targets.items():
        p = root / rel
        have = p.read_text(encoding="utf-8-sig") if p.is_file() else None
        if have != want:
            drift.append(rel)
    return drift


# ── 命令 ──────────────────────────────────────────────────────────


def _prepare(root: Path, profile: str | None = None) -> tuple[dict, Resolved]:
    spine = load_spine(root)
    errs = validate(spine, root)
    if profile and profile not in spine["models"]["profiles"]:
        errs.append(f"--profile {profile!r} not in models.profiles")
    if errs:
        raise SpineError("\n".join(f"  x {e}" for e in errs))
    return spine, Resolved(spine, profile)


def cmd_check(root: Path) -> int:
    _, r = _prepare(root)
    targets = build_targets(root, r)
    drift = diff_targets(root, targets)
    if drift:
        print("workflow spine drift — run: python scripts/workflow.py render")
        for rel in drift:
            print(f"  ~ {rel.as_posix()}")
        return 1
    print(f"workflow spine OK (profile={r.profile_name}, {len(targets)} derived targets in sync)")
    return 0


def cmd_render(root: Path) -> int:
    _, r = _prepare(root)
    targets = build_targets(root, r)
    changed = diff_targets(root, targets)
    for rel in changed:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(targets[rel])
        print(f"  wrote {rel.as_posix()}")
    print(f"rendered profile={r.profile_name}: {len(changed)} changed / {len(targets)} targets")
    return 0


def cmd_show(root: Path, profile: str | None) -> int:
    _, r = _prepare(root, profile)
    print(body_models(r))
    print()
    print(body_roles(r))
    print()
    print(body_flow(r))
    if r.profile.get("agent_model") == "inherit":
        print("\nnote: profile uses inherit — every agent follows the session model; pick it with /model or settings.model")
    return 0


def merge_settings(current: dict, r: Resolved) -> tuple[dict, list[str]]:
    """把 profile 片段合并进 settings；清掉上一 profile 留下的、本 profile 不再管理的键。"""
    merged = json.loads(json.dumps(current))
    frag = settings_fragment(r)
    notes: list[str] = []
    had_env = isinstance(current.get("env"), dict)
    env = merged["env"] = merged.get("env") if isinstance(merged.get("env"), dict) else {}
    ours = {
        str(e.get("claude_code"))
        for prof in r.spine["models"]["profiles"].values()
        for e in prof["tiers"].values()
    }
    for key in ALIAS_ENV.values():
        if key in frag.get("env", {}) or key not in env:
            continue
        if env[key] in ours:
            notes.append(f"removed env.{key}={env[key]!r} (written by a previous profile)")
            env.pop(key)
        else:
            notes.append(f"kept env.{key}={env[key]!r} (not from any profile; gateway/background model)")
    env.update(frag.get("env", {}))
    if "CLAUDE_CODE_SUBAGENT_MODEL" in env:
        env.pop("CLAUDE_CODE_SUBAGENT_MODEL")
        notes.append("removed env.CLAUDE_CODE_SUBAGENT_MODEL (it overrides every agent's routed model)")
    if "model" in frag:
        cur = str(merged.get("model") or "")
        suffix = cur[cur.index("["):] if "[" in cur and cur.split("[")[0].lower() == frag["model"] else ""
        merged["model"] = frag["model"] + suffix
        if env.get("ANTHROPIC_MODEL"):
            notes.append(
                f"env.ANTHROPIC_MODEL={env['ANTHROPIC_MODEL']!r} (e.g. from cc-switch) overrides settings.model; "
                "remove it if the session model should follow this profile"
            )
    elif str(merged.get("model", "")).split("[")[0].lower() in ALIAS_ENV:
        merged.pop("model")
        notes.append("removed alias settings.model (this profile has no ANTHROPIC_DEFAULT_*_MODEL redirects)")
    if "effortLevel" in frag:
        merged["effortLevel"] = frag["effortLevel"]
    elif "effortLevel" in merged:
        merged.pop("effortLevel")
        notes.append("removed effortLevel (profile.supports_effort=false)")
    if r.profile.get("agent_model") == "inherit":
        notes.append("profile uses inherit: choose the session model yourself (/model or settings.model)")
    if not env and not had_env:
        merged.pop("env")
    return merged, notes


def cmd_apply_settings(root: Path, settings: Path | None, write: bool) -> int:
    _, r = _prepare(root)
    path = settings or Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "settings.json"
    current = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}
    merged, notes = merge_settings(current, r)
    if merged == current:
        print(f"{path}: already matches profile {r.profile_name}")
        for n in notes:
            print(f"  note: {n}")
        return 0
    print(f"{path}: profile {r.profile_name} →")
    for key in ("model", "effortLevel"):
        if current.get(key) != merged.get(key):
            print(f"  {key}: {current.get(key)!r} → {merged.get(key)!r}")
    cur_env = current.get("env") if isinstance(current.get("env"), dict) else {}
    new_env = merged.get("env") if isinstance(merged.get("env"), dict) else {}
    for key in sorted(set(cur_env) | set(new_env)):
        a, b = cur_env.get(key), new_env.get(key)
        if a != b:
            print(f"  env.{key}: {a!r} → {b!r}")
    for n in notes:
        print(f"  note: {n}")
    backup = path.with_name(f"{path.name}.bak_{time.strftime('%Y%m%d-%H%M%S')}")
    if not write:
        print(f"dry-run; re-run with --write to apply (backup → {backup.name})")
        return 0
    if path.is_file():
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dump_json(merged))
    print("written")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("render")
    s = sub.add_parser("show")
    s.add_argument("--profile")
    a = sub.add_parser("apply-settings")
    a.add_argument("--settings", type=Path)
    a.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    root = args.root or default_root()
    try:
        if args.cmd == "check":
            return cmd_check(root)
        if args.cmd == "render":
            return cmd_render(root)
        if args.cmd == "show":
            return cmd_show(root, args.profile)
        return cmd_apply_settings(root, args.settings, args.write)
    except SpineError as exc:
        print(f"workflow spine invalid:\n{exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, yaml.YAMLError, KeyError) as exc:
        print(f"workflow spine error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
