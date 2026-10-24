# -*- coding: utf-8 -*-
"""config/workflow.yaml 主干：校验、完成门、两道 PASS 门、派生漂移、model-agnostic lint。"""
from __future__ import annotations

import copy
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location("workflow", ROOT / "scripts" / "workflow.py")
assert _spec and _spec.loader
wf = importlib.util.module_from_spec(_spec)
sys.modules["workflow"] = wf
_spec.loader.exec_module(wf)

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def rejected(mutate, needle: str) -> bool:
    bad = copy.deepcopy(spine)
    mutate(bad)
    return any(needle in e for e in wf.validate(bad, ROOT))


spine = wf.load_spine(ROOT)
errs = wf.validate(spine, ROOT)
check("live spine validates", not errs, "; ".join(errs))
live_targets = wf.build_targets(ROOT, spine)
check("live derived targets in sync", not wf.diff_targets(ROOT, live_targets))
check("live tree passes model-agnostic lint", not wf.lint(ROOT), "; ".join(wf.lint(ROOT)[:5]))

# ── model / effort 不得回流 ──
for legacy in ("models", "roles", "triage", "constraints"):
    check(f"legacy top-level {legacy!r} rejected", rejected(lambda s, k=legacy: s.update({k: {}}), legacy))
check("stage-level model rejected", rejected(lambda s: s["stages"]["execute"].update(model="x"), "'model'"))
check("stage-level effort rejected", rejected(lambda s: s["stages"]["verify"].update(effort="x"), "'effort'"))
for name in sorted(wf.disk_agents(ROOT)):
    fm = wf._frontmatter(live_targets[Path("agents") / f"{name}.md"])
    check(f"{name}: no model/effort in frontmatter",
          not any(ln.split(":", 1)[0].strip() in ("model", "effort") for ln in fm))

fm = "---\nname: x\nmodel: m\ndescription: |\n  a\n  b\neffort: e\ntools: Read\n---\nbody\n"
out = wf.strip_frontmatter_keys(fm, ("model", "effort"), "x.md")
check("render strips model/effort, keeps block scalar",
      out == "---\nname: x\ndescription: |\n  a\n  b\ntools: Read\n---\nbody\n")

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "agents").mkdir()
    (root / "agents" / "x.md").write_text("---\nname: x\nmodel: inherit\n---\n", encoding="utf-8")
    (root / "rules.md").write_text("pick a vendor-tier alias: opus\n", encoding="utf-8")
    (root / "config.json").write_text('{"effortLevel": "high"}\n', encoding="utf-8")
    (root / "think.json").write_text('{"thinking_budget": 8000}\n', encoding="utf-8")
    (root / "CHANGELOG.md").write_text("history may mention sonnet\n", encoding="utf-8")
    hits = wf.lint(root)
    check("lint flags agent frontmatter model key", any("agents/x.md" in h and "frontmatter" in h for h in hits))
    check("lint flags vendor tier alias in prose", any(h.startswith("rules.md:1") for h in hits))
    check("lint flags effort key in config", any(h.startswith("config.json:1") and "effortLevel" in h for h in hits))
    check("lint flags thinking_budget in config", any(h.startswith("think.json:1") and "thinking_budget" in h for h in hits))
    check("lint ignores CHANGELOG history", not any("CHANGELOG" in h for h in hits))
    for i, phrase in enumerate((
        "推荐使用 MiniMax", "GPT Image 生成", "use Gemini for this", "run Llama locally",
        "Mistral is best", "Moonshot backend", "try o1 here", "claude-3-5 works",
    )):
        (root / f"p{i}.md").write_text(phrase + "\n", encoding="utf-8")
    hits = wf.lint(root)
    for i, phrase in enumerate(("minimax", "gpt", "gemini", "llama", "mistral", "moonshot", "o1", "claude-3")):
        check(f"lint flags {phrase}", any(h.startswith(f"p{i}.md:1") for h in hits))

# ── 完成门：独立审查强制 ──
check("review not required rejected",
      rejected(lambda s: s["completion"].update(independent_review_required=False), "independent_review_required"))
check("track exemption rejected",
      rejected(lambda s: s["completion"].update(required_on_tracks=["non_simple"]), "required_on_tracks"))
check("exhausted rounds must be BLOCKED",
      rejected(lambda s: s["completion"].update(on_rounds_exhausted="DONE_WITH_CONCERNS"), "on_rounds_exhausted"))
check("user waiver cannot be DONE", rejected(lambda s: s["completion"].update(user_waiver_status="DONE"), "DONE"))
check("track without verify rejected", rejected(lambda s: s["tracks"].update(simple=["triage", "execute"]), "verify"))
check("max_rounds > 3 rejected", rejected(lambda s: s["review"].update(max_rounds=4), "max_rounds"))
check("max_rounds default is 3", spine["review"]["max_rounds"] == 3)
check("max_blocks < max_rounds rejected", rejected(lambda s: s["review"].update(max_blocks=2), "max_blocks"))

# ── 两道 PASS 门 ──
check("pass_requires missing bar rejected",
      rejected(lambda s: s["review"]["pass_requires"].pop("original_functionality_preserved"), "pass_requires"))
check("pass_requires bar without evidence rejected",
      rejected(lambda s: s["review"]["pass_requires"]["requirements_met"].pop("evidence"), "evidence"))
check("pass_requires label drift vs hooks rejected",
      rejected(lambda s: s["review"]["pass_requires"]["requirements_met"].update(label="x"), "PASS_BAR_LABELS"))
contract = live_targets[Path("agents/eng-reviewer.md")]
check("reviewer contract renders both bars",
      all(b["label"] in contract for b in spine["review"]["pass_requires"].values()))
check("completion block renders both bars",
      all(b["label"] in live_targets[Path("CLAUDE.md")] for b in spine["review"]["pass_requires"].values()))

# ── 结构 ──
check("dimension drift vs r20_replay rejected",
      rejected(lambda s: s["review"].update(dimensions=s["review"]["dimensions"][:-1]), "r20_replay"))
check("unknown stage in track rejected", rejected(lambda s: s["tracks"].update(simple=["triage", "nope", "verify"]), "nope"))
check("on_demand stage inside a track rejected",
      rejected(lambda s: s["tracks"]["non_simple"].append("ship"), "on_demand"))
check("refresh_graph_before_review=false rejected",
      rejected(lambda s: s["review"].update(refresh_graph_before_review=False), "refresh_graph_before_review"))
check("reviewer list drift vs hooks defaults rejected",
      rejected(lambda s: s["review"]["routing"].update(extra=["planner"]), "DEFAULT_REVIEWER_AGENTS"))
check("eng-reviewer always routed", "eng-reviewer" in spine["review"]["routing"]["always"])
rel = Path("agents/eng-reviewer.md")
tampered = dict(live_targets)
tampered[rel] = live_targets[rel].replace("<!-- /spine:review-contract -->", "x\n<!-- /spine:review-contract -->")
check("edited generated block reported as drift", rel in wf.diff_targets(ROOT, tampered))

# ── 上下文窗口：不登记模型，未知模型以调用方设置为准 ──
sys.path.insert(0, str(ROOT / "hooks" / "_lib"))
import context_thresholds as ct  # noqa: E402

for key in ("CLAUDE_CODE_MAX_CONTEXT_TOKENS", "CLAUDE_CODE_AUTO_COMPACT_WINDOW"):
    os.environ.pop(key, None)
check("suffix gives known window", ct.known_context_tokens("any-model[1M]") == 1_000_000)
check("unregistered model is unknown", ct.known_context_tokens("any-model") is None)
os.environ["CLAUDE_CODE_AUTO_COMPACT_WINDOW"] = "900000"
check("unknown model trusts explicit window", ct.ctx_window_tokens("any-model") == 900_000)
check("known window caps explicit", ct.ctx_window_tokens("any-model[200K]") == 200_000)
os.environ.pop("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
check("unknown model without explicit → default", ct.ctx_window_tokens("any-model") == 200_000)

print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
