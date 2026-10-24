#!/usr/bin/env python3
"""Workflow spine — 校验 config/workflow.yaml、渲染派生内容、强制 model/effort 无关。

命令：
    python scripts/workflow.py check     # 校验 + 漂移 + model-agnostic lint（有问题 exit 1）
    python scripts/workflow.py render    # 写回全部派生目标
    python scripts/workflow.py show      # 打印阶段 / 轨道 / 完成定义 / 审查
    python scripts/workflow.py lint      # 只跑 model-agnostic lint

根目录：--root > $CLAUDE_HOME > 本脚本所在仓库。派生目标清单见 docs/DEV_FLOW.md。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
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
GENERATED_NOTE = "派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改"
MAX_ROUNDS_CEILING = 3
VERDICTS = ["PASS", "NEEDS-CHANGES"]
PASS_BARS = ("requirements_met", "original_functionality_preserved")
TOP_KEYS = ("stages", "tracks", "completion", "quality", "review")

# ── model-agnostic lint ───────────────────────────────────────────
# 本包只描述角色/阶段/门控；模型与推理强度由调用方决定。下列模式命中即视为把配置绑到了具体模型或档位。
MODEL_PATTERNS = (
    r"\bclaude-(?:opus|sonnet|haiku|instant|\d)\w*",
    r"\b(?:opus|sonnet|haiku)\b",
    r"\bgpt\b",
    r"\bgpt-?\d[\w.]*",
    r"\bo[134](?:-(?:mini|preview|pro))?\b",
    r"\bkimi\b",
    r"\bmoonshot\b",
    r"\bk[23]-\d+k\b",
    r"\bdeepseek\b",
    r"\bminimax\b",
    r"\bgemini\b",
    r"\bgemini-?\d",
    r"\bllama\b",
    r"\bmistral\b",
    r"\bgrok-?\d",
    r"\bcomposer-\d",
    r"\bqwen-?\d",
    r"\bglm-\d",
    r"\bcodex\b",
)
EFFORT_PATTERNS = (
    r"\beffortLevel\b",
    r"\breasoning[_-]effort\b",
    r"\bthinking[_-]?budget\b",
    r"\bbudget_tokens\b",
    r"\bmax_thinking(?:_?tokens)?\b",
    r"\bthinkingLevel\b",
    r"\bxhigh\b",
    r"\bANTHROPIC_DEFAULT_\w+_MODEL\b",
    r"\bCLAUDE_CODE_SUBAGENT_MODEL\b",
)
FRONTMATTER_BANNED_KEYS = ("model", "effort")
_LINT_RE = re.compile("|".join(MODEL_PATTERNS + EFFORT_PATTERNS), re.I)
LINT_SUFFIXES = {".md", ".mdc", ".yaml", ".yml", ".json", ".py", ".ts", ".js", ".ps1", ".toml", ".txt"}
# 历史记录 / 外部调研 / 第三方插件元数据 / lint 自身与其测试 不受约束（docs/archive 已删）
LINT_EXCLUDES = (
    "CHANGELOG.md",
    "docs/research/",
    "docs/ADR/",
    "plugins/",
    "hooks/tests/",
    "scripts/workflow.py",
    "node_modules/",
    ".git/",
)
FRONTMATTER_DIRS = ("agents", "commands", "skills", "catalog/agents", "catalog/skills")


class SpineError(Exception):
    pass


def default_root() -> Path:
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


def load_spine(root: Path) -> dict:
    with open(root / SPINE, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SpineError(f"{SPINE}: top level must be a mapping")
    return data


def reviewers(spine: dict) -> list[str]:
    out: list[str] = []
    for names in spine["review"]["routing"].values():
        for n in names:
            if n not in out:
                out.append(n)
    return out


def disk_agents(root: Path) -> set[str]:
    return {p.stem for p in (root / "agents").glob("*.md") if p.name != "README.md"}


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
    errs = [f"missing top-level key {k!r}" for k in TOP_KEYS if k not in spine]
    for legacy in ("models", "roles", "constraints", "triage"):
        if legacy in spine:
            errs.append(f"top-level key {legacy!r} removed in schema 2 (model/effort are chosen by the caller)")
    if errs:
        return errs

    agents = disk_agents(root)
    stages, tracks = spine["stages"], spine["tracks"]
    for sid, st in stages.items():
        if not (root / "skills" / st.get("skill", "") / "SKILL.md").is_file():
            errs.append(f"stages.{sid}: skills/{st.get('skill')}/SKILL.md missing")
        if st.get("command") and not (root / "commands" / f"{st['command']}.md").is_file():
            errs.append(f"stages.{sid}: commands/{st['command']}.md missing")
        role = st.get("role")
        if role != "session" and role not in agents:
            errs.append(f"stages.{sid}: role {role!r} is neither 'session' nor agents/<name>.md")
        if not st.get("exit"):
            errs.append(f"stages.{sid}: exit gates required")
        for k in ("model", "effort", "tier"):
            if k in st:
                errs.append(f"stages.{sid}: {k!r} not allowed (chosen by the caller)")
    for tname, seq in tracks.items():
        for sid in seq:
            if sid not in stages:
                errs.append(f"tracks.{tname}: unknown stage {sid!r}")
            elif stages[sid].get("on_demand"):
                errs.append(f"tracks.{tname}: on_demand stage {sid!r} must not be in a track (R19)")
        if "verify" not in seq:
            errs.append(f"tracks.{tname}: must include verify (independent review gate)")

    comp = spine["completion"]
    if comp.get("independent_review_required") is not True:
        errs.append("completion.independent_review_required must be true (no review PASS ⇒ not complete)")
    if set(comp.get("required_on_tracks") or []) != set(tracks):
        errs.append(f"completion.required_on_tracks must cover every track {sorted(tracks)} (no exemptions)")
    if comp.get("on_rounds_exhausted") != "BLOCKED":
        errs.append("completion.on_rounds_exhausted must be BLOCKED (exhausted rounds ≠ done, ≠ skip review)")
    if comp.get("user_waiver_status") == "DONE":
        errs.append("completion.user_waiver_status must not be DONE")
    if not comp.get("done_when"):
        errs.append("completion.done_when required")

    q = spine["quality"]
    for key in ("definition_of_ready", "self_check", "verify_tiers"):
        if not q.get(key):
            errs.append(f"quality.{key} required")
    if not isinstance(q.get("attempt_escalation"), int) or q["attempt_escalation"] < 2:
        errs.append("quality.attempt_escalation must be int ≥ 2")

    review = spine["review"]
    routed = reviewers(spine)
    for n in routed:
        if n not in agents:
            errs.append(f"review.routing: agents/{n}.md missing")
    if "eng-reviewer" not in (review.get("routing") or {}).get("always", []):
        errs.append("review.routing.always must include eng-reviewer")
    roles = {st.get("role") for st in stages.values()}
    for a in sorted(agents - set(routed) - roles):
        errs.append(f"agents/{a}.md is neither a stage role nor a routed reviewer (orphan agent)")
    if set(routed) & roles:
        errs.append(f"reviewers must not also be stage roles: {sorted(set(routed) & roles)}")
    mr = review.get("max_rounds")
    if not isinstance(mr, int) or not 1 <= mr <= MAX_ROUNDS_CEILING:
        errs.append(f"review.max_rounds must be int in 1..{MAX_ROUNDS_CEILING}")
    for key in ("max_blocks", "min_files"):
        if not isinstance(review.get(key), int) or review[key] < 1:
            errs.append(f"review.{key} must be int ≥ 1")
    if isinstance(mr, int) and isinstance(review.get("max_blocks"), int) and review["max_blocks"] < mr:
        errs.append("review.max_blocks must be ≥ review.max_rounds")
    if review.get("refresh_graph_before_review") is not True:
        errs.append("review.refresh_graph_before_review must be true (hooks graph gate + V16 require it)")
    bars = review.get("pass_requires") or {}
    if tuple(bars) != PASS_BARS:
        errs.append(f"review.pass_requires must define exactly {PASS_BARS} (PASS = both bars met)")
    for key, bar in bars.items():
        if not isinstance(bar, dict) or not all(bar.get(k) for k in ("label", "check", "evidence")):
            errs.append(f"review.pass_requires.{key}: label / check / evidence required")
    if review.get("verdicts") != VERDICTS:
        errs.append(f"review.verdicts must be {VERDICTS} (hooks parse these)")
    names = tuple(d.get("name") for d in review.get("dimensions") or [])
    r20 = _r20_module(root)
    if r20 is not None:
        mech = ("满足",) + tuple(r20._REQUIRED)
        if names != mech:
            errs.append(f"review.dimensions {names} != hooks/_lib/r20_replay.py {mech}")
        labels = tuple(b.get("label") for b in bars.values() if isinstance(b, dict))
        if labels != tuple(getattr(r20, "PASS_BAR_LABELS", ())):
            errs.append(f"review.pass_requires labels {labels} != hooks/_lib/r20_replay.py PASS_BAR_LABELS")
        if set(routed) != set(r20.DEFAULT_REVIEWER_AGENTS):
            errs.append(
                f"review.routing {sorted(routed)} != "
                f"hooks/_lib/r20_replay.py DEFAULT_REVIEWER_AGENTS {sorted(r20.DEFAULT_REVIEWER_AGENTS)}"
            )
    return errs


def _lint_targets(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in LINT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel == ex or rel.startswith(ex) or f"/{ex}" in f"/{rel}" for ex in LINT_EXCLUDES):
            continue
        yield path, rel


def _frontmatter(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---", 4)
    return text[4:end].split("\n") if end > 0 else []


def lint(root: Path) -> list[str]:
    """命中模型 ID / 厂商档位 / effort 档 → 违规。返回 'path:line: match' 列表。"""
    out: list[str] = []
    for path, rel in _lint_targets(root):
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        for no, line in enumerate(text.splitlines(), 1):
            m = _LINT_RE.search(line)
            if m:
                out.append(f"{rel}:{no}: {m.group(0)!r}")
        if path.suffix == ".md" and rel.split("/")[0] in {d.split("/")[0] for d in FRONTMATTER_DIRS}:
            for line in _frontmatter(text):
                key = line.split(":", 1)[0].strip()
                if key in FRONTMATTER_BANNED_KEYS:
                    out.append(f"{rel}: frontmatter `{key}:` (agents inherit the caller's model and effort)")
    return out


# ── 渲染原语 ──────────────────────────────────────────────────────

_BLOCK_RE = "<!-- spine:{name} -->\n(.*?)<!-- /spine:{name} -->"


def replace_block(text: str, name: str, body: str, path: str) -> str:
    pattern = re.compile(_BLOCK_RE.format(name=re.escape(name)), re.S)
    if not pattern.search(text):
        raise SpineError(f"{path}: marker <!-- spine:{name} --> missing")
    block = f"<!-- spine:{name} -->\n{body.rstrip()}\n<!-- /spine:{name} -->"
    return pattern.sub(lambda _m: block, text, count=1)


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


# ── 派生内容 ──────────────────────────────────────────────────────


def _bars(spine: dict) -> list[str]:
    return [
        f"{i}. **{b['label']}**：{b['check']}。证据：{b['evidence']}。"
        for i, b in enumerate(spine["review"]["pass_requires"].values(), 1)
    ]


def body_completion(spine: dict) -> str:
    comp, rv = spine["completion"], spine["review"]
    return "\n".join([
        f"**完成定义**（{GENERATED_NOTE}）：没有独立审查 PASS ⇒ 任务未完成；适用全部轨道"
        f"（{', '.join(comp['required_on_tracks'])}），简单/只读/文档任务同样适用。",
        "",
        *[f"- {x}" for x in comp["done_when"]],
        "- **PASS = 两道门同时满足**（任一不满足即 NEEDS-CHANGES）：",
        *[f"  {x}" for x in _bars(spine)],
        f"- 一轮 = 改 → 验 → 刷图 → 并行全新审查（一次找齐）；目标第 1 轮 PASS，上限 **{rv['max_rounds']}** 轮。",
        f"- {rv['max_rounds']} 轮仍未 PASS ⇒ **{comp['on_rounds_exhausted']}**（未完成），"
        "不得声称完成，也不得改为「跳过审查」。",
        f"- 自检、实现者自签、验证命令全绿都不能替代独立审查；仅用户显式豁免时放行，状态记 `{comp['user_waiver_status']}`。",
    ])


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
        f"- 结论行只填其一：`{rv['verdicts'][0]}` | `{rv['verdicts'][1]}`；有任何必须修项即 `{rv['verdicts'][1]}`。"
        "你的 PASS 是任务完成的必要条件。",
        f"- 七维缺任一项本轮无效：{line}",
        "- **PASS 必须同时满足两道门**，逐道写结论 + 证据；任一道缺证据或不满足即 "
        f"`{rv['verdicts'][1]}`：",
        *[f"  {x}" for x in _bars(spine)],
        "- 输出须含以下两行，每道门单独一行（机械门逐行解析：PASS 时该行以「通过」开头、同一行写真实观察证据；"
        "「基本通过 / 部分通过 / 待定」或缺行都不算 PASS；尖括号模板、空证据、「证据：<…>」都不算；"
        "不通过时写「不通过」并给 NEEDS-CHANGES）：",
        *[f"  `- {b['label']}：通过（证据：贴本轮命令输出原文，禁止尖括号模板）`" for b in rv["pass_requires"].values()],
        "- 本契约的输出要求优先于上文个人模板：七维各一行 + 两道门两行 + 结论行，缺一本轮无效。",
        "- 审查者多为只读：「原功能保持」以主会话附带的测试 / validate / check 观察输出与相对起点的行为差异为证据，"
        "并核对它与 diff 一致；未附或对不上即 NEEDS-CHANGES。",
    ])


def body_ready_contract(spine: dict) -> str:
    q = spine["quality"]
    out = [f"## 一次通过契约（{GENERATED_NOTE}）", "", "**就绪定义**（缺一项不开工，回主会话补齐）："]
    out += [f"- {x}" for x in q["definition_of_ready"]]
    out += ["", "**交审前自检**（与审查者同一份清单；自检通过 ≠ 完成，完成须独立审查 PASS）："]
    out += [f"- {x}" for x in q["self_check"]]
    return "\n".join(out)


def body_stage_gate(spine: dict, sid: str) -> str:
    st = spine["stages"][sid]
    out = [
        f"## 门控（{GENERATED_NOTE}）",
        "",
        f"- 阶段：{st['label']} | skill：`skills/{st['skill']}/SKILL.md` | 角色：{st['role']}",
    ]
    if st.get("entry"):
        out.append("- 进入：" + "；".join(st["entry"]))
    out.append("- 退出（全部满足才进入下一阶段）：")
    out += [f"  - {x}" for x in st["exit"]]
    if st["skill"] == "verification-before-completion":
        out.append("- verify_tier：")
        out += [f"  - `{k}`：{v}" for k, v in spine["quality"]["verify_tiers"].items()]
        out += ["", body_completion(spine)]
    return "\n".join(out)


def body_flow(spine: dict) -> str:
    out = ["| 阶段 | 命令 | skill | 角色 | 退出门 |", "| --- | --- | --- | --- | --- |"]
    for st in spine["stages"].values():
        cmd = f"/{st['command']}" if st.get("command") else "—"
        out.append(f"| {st['label']} | {cmd} | {st['skill']} | {st['role']} | {_cell('；'.join(st['exit']))} |")
    out.append("")
    for tname, seq in spine["tracks"].items():
        out.append(f"- **{tname}**：" + " → ".join(spine["stages"][s]["label"] for s in seq))
    on_demand = [st["label"] for st in spine["stages"].values() if st.get("on_demand")]
    if on_demand:
        out.append(f"- **按需**：{'、'.join(on_demand)}（不在轨道内；任务完成且用户明确要求时进入，R19）")
    out.append(
        "- **模型 / effort**：不在本包配置；由调用方（会话、settings、编辑器、Task 传参）决定，agent 一律继承。"
    )
    out += ["", body_completion(spine)]
    return "\n".join(out)


def body_dimensions(spine: dict) -> str:
    dims = spine["review"]["dimensions"]
    out = [f"> {GENERATED_NOTE}。缺任一项视为本轮无效、不计 PASS。", ""]
    for i, d in enumerate(dims, 1):
        name = f"**{d['name']}**" if i == len(dims) else d["name"]
        out.append(f"{i}. {name}（{d['hint']}）")
    return "\n".join(out)


def body_review_routing(spine: dict) -> str:
    rv = spine["review"]
    width = max(len(k) for k in rv["routing"])
    lines = ["```"]
    for group, names in rv["routing"].items():
        prefix = "" if group == "always" else "+ "
        lines.append(f"{group.ljust(width)}  → {prefix}{', '.join(names)}")
    lines += ["```", "", f"> {GENERATED_NOTE}。审查者模型由调用方选择；cross_model 组要求与实现者不同的模型。"]
    return "\n".join(lines)


def body_derived() -> str:
    rows = [
        ("agents/*.md frontmatter", "无 `model` / `effort` 键（render 剥离，lint 拦截）"),
        ("审查者 agents `spine:review-contract`", "七维 + 结论 + 只读规则（review）"),
        ("change-implementer / planner `spine:ready-contract`", "就绪定义 + 交审自检（quality）"),
        ("commands/{discuss,plan,execute,verify,ship,compact}.md `spine:stage-gate`", "阶段门；verify 含完成定义"),
        ("CLAUDE.md / docs/DEV_FLOW.md `spine:flow`", "阶段表 + 轨道 + 完成定义"),
        ("rules/AGENTS.md `spine:review-routing`", "审查路由（review.routing）"),
        ("skills/verification-before-completion `spine:dimensions` / `spine:completion`", "七维 + 完成定义"),
        ("templates/cursor-guard/rules/CURSOR-EDITOR.mdc `spine:completion`", "Cursor 完成定义"),
        ("config/quality_gates.json verification_gate", "轮次 / 阻断 / 最少文件 / 审查者 / 刷图 / 完成状态"),
        ("templates/cursor-guard/guard-config.json verification.reviewer_agents", "Cursor 审查者名单"),
        ("templates/editor-graph-hooks/verify-gate.ts", "`review_max_rounds=<n>` 文案"),
    ]
    out = ["| 目标 | 内容（来源节） |", "| --- | --- |"]
    out += [f"| {a} | {b} |" for a, b in rows]
    return "\n".join(out)


def strip_frontmatter_keys(text: str, keys: tuple[str, ...], path: str) -> str:
    if not text.startswith("---\n"):
        raise SpineError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise SpineError(f"{path}: unterminated frontmatter")
    lines = [ln for ln in text[4:end].split("\n") if ln.split(":", 1)[0].strip() not in keys]
    return "---\n" + "\n".join(lines) + text[end:]


# ── 目标表 ────────────────────────────────────────────────────────


def build_targets(root: Path, spine: dict) -> dict[Path, str]:
    """返回 {path: 期望内容}；只包含有派生内容的文件。"""
    out: dict[Path, str] = {}

    def text_of(rel: Path) -> str:
        return out[rel] if rel in out else (root / rel).read_text(encoding="utf-8")

    for name in sorted(disk_agents(root)):
        rel = Path("agents") / f"{name}.md"
        out[rel] = strip_frontmatter_keys(text_of(rel), FRONTMATTER_BANNED_KEYS, str(rel))
    for name in reviewers(spine):
        rel = Path("agents") / f"{name}.md"
        out[rel] = replace_block(text_of(rel), "review-contract", body_review_contract(spine), str(rel))
    for name in ("change-implementer", "planner"):
        rel = Path("agents") / f"{name}.md"
        out[rel] = replace_block(text_of(rel), "ready-contract", body_ready_contract(spine), str(rel))
    for sid, st in spine["stages"].items():
        if st.get("command"):
            rel = Path("commands") / f"{st['command']}.md"
            out[rel] = replace_block(text_of(rel), "stage-gate", body_stage_gate(spine, sid), str(rel))

    verif = Path("skills") / "verification-before-completion" / "SKILL.md"
    blocks = [
        (Path("CLAUDE.md"), "flow", body_flow(spine)),
        (Path("docs") / "DEV_FLOW.md", "flow", body_flow(spine)),
        (Path("docs") / "DEV_FLOW.md", "derived", body_derived()),
        (Path("rules") / "AGENTS.md", "review-routing", body_review_routing(spine)),
        (verif, "dimensions", body_dimensions(spine)),
        (verif, "completion", body_completion(spine)),
        (Path("templates") / "cursor-guard" / "rules" / "CURSOR-EDITOR.mdc", "completion", body_completion(spine)),
    ]
    for rel, name, body in blocks:
        out[rel] = replace_block(text_of(rel), name, body, str(rel))

    rv, comp = spine["review"], spine["completion"]
    names = reviewers(spine)

    qg_rel = Path("config") / "quality_gates.json"
    qg = json.loads((root / qg_rel).read_text(encoding="utf-8"))
    vg = qg.setdefault("verification_gate", {})
    vg["max_blocks"] = rv["max_blocks"]
    vg["review_max_rounds"] = rv["max_rounds"]
    vg["require_reviewer_min_files"] = rv["min_files"]
    vg["require_refresh_before_review"] = bool(rv["refresh_graph_before_review"])
    vg["reviewer_agents"] = names
    vg["on_rounds_exhausted"] = comp["on_rounds_exhausted"]
    vg["user_waiver_status"] = comp["user_waiver_status"]
    qg.setdefault("graph_freshness", {})["require_refresh_before_review"] = bool(rv["refresh_graph_before_review"])
    out[qg_rel] = dump_json(qg)

    gc_rel = Path("templates") / "cursor-guard" / "guard-config.json"
    gc = json.loads((root / gc_rel).read_text(encoding="utf-8-sig"))
    gc.setdefault("verification", {})["reviewer_agents"] = names
    out[gc_rel] = dump_json(gc)

    vg_rel = Path("templates") / "editor-graph-hooks" / "verify-gate.ts"
    vg_text = text_of(vg_rel)
    if not re.search(r"review_max_rounds=\d+", vg_text):
        raise SpineError(f"{vg_rel}: review_max_rounds=<n> anchor missing")
    out[vg_rel] = re.sub(r"review_max_rounds=\d+", f"review_max_rounds={rv['max_rounds']}", vg_text)
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


def _prepare(root: Path) -> dict:
    spine = load_spine(root)
    errs = validate(spine, root)
    if errs:
        raise SpineError("\n".join(f"  x {e}" for e in errs))
    return spine


def _print_lint(hits: list[str]) -> None:
    print("model-agnostic lint: config must not name models, vendor tiers or effort levels")
    for h in hits:
        print(f"  ! {h}")


def cmd_check(root: Path) -> int:
    spine = _prepare(root)
    targets = build_targets(root, spine)
    drift = diff_targets(root, targets)
    hits = lint(root)
    if drift:
        print("workflow spine drift — run: python scripts/workflow.py render")
        for rel in drift:
            print(f"  ~ {rel.as_posix()}")
    if hits:
        _print_lint(hits)
    if drift or hits:
        return 1
    print(f"workflow spine OK ({len(targets)} derived targets in sync, model-agnostic lint clean)")
    return 0


def cmd_render(root: Path) -> int:
    spine = _prepare(root)
    targets = build_targets(root, spine)
    changed = diff_targets(root, targets)
    for rel in changed:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(targets[rel])
        print(f"  wrote {rel.as_posix()}")
    print(f"rendered: {len(changed)} changed / {len(targets)} targets")
    return 0


def cmd_show(root: Path) -> int:
    spine = _prepare(root)
    print(body_flow(spine))
    print()
    print(body_review_routing(spine))
    return 0


def cmd_lint(root: Path) -> int:
    hits = lint(root)
    if hits:
        _print_lint(hits)
        return 1
    print("model-agnostic lint clean")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "render", "show", "lint"):
        sub.add_parser(name)
    args = ap.parse_args(argv)
    root = args.root or default_root()
    handlers = {"check": cmd_check, "render": cmd_render, "show": cmd_show, "lint": cmd_lint}
    try:
        return handlers[args.cmd](root)
    except SpineError as exc:
        print(f"workflow spine invalid:\n{exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, yaml.YAMLError, KeyError) as exc:
        print(f"workflow spine error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
