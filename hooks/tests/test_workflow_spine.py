# -*- coding: utf-8 -*-
"""config/workflow.yaml 主干：全部 profile 可解析、漂移可检出、约束可拦截。"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
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


spine = wf.load_spine(ROOT)
errs = wf.validate(spine, ROOT)
check("live spine validates", not errs, "; ".join(errs))

active = wf.Resolved(spine)
live_targets = wf.build_targets(ROOT, active)
check("live derived targets in sync", not wf.diff_targets(ROOT, live_targets))

for pname in spine["models"]["profiles"]:
    r = wf.Resolved(spine, pname)
    targets = wf.build_targets(ROOT, r)
    eng = targets[Path("agents/eng-reviewer.md")]
    want = r.agent_model("eng-reviewer")
    check(f"{pname}: eng-reviewer frontmatter model={want}", f"\nmodel: {want}\n" in eng)
    has_effort = "\neffort:" in eng.split("---", 2)[1]
    check(f"{pname}: effort only when supported", has_effort == bool(r.profile.get("supports_effort")))

single = wf.Resolved(spine, "single")
check("single profile routes every role to inherit", all(single.agent_model(n) == "inherit" for n in spine["roles"]))

check("eng-reviewer always routed", "eng-reviewer" in active.reviewers())

bad = copy.deepcopy(spine)
bad["roles"]["eng-reviewer"]["tier"] = "light"
check("reviewer tier below implementer rejected", any("eng-reviewer" in e and "tier" in e for e in wf.validate(bad, ROOT)))

bad = copy.deepcopy(spine)
bad["review"]["dimensions"] = bad["review"]["dimensions"][:-1]
check("dimension drift vs r20_replay rejected", any("r20_replay" in e for e in wf.validate(bad, ROOT)))

bad = copy.deepcopy(spine)
bad["tracks"]["simple"] = ["triage", "nope"]
check("unknown stage in track rejected", any("nope" in e for e in wf.validate(bad, ROOT)))

rel = Path("agents/eng-reviewer.md")
tampered = dict(live_targets)
tampered[rel] = live_targets[rel].replace("<!-- /spine:review-contract -->", "x\n<!-- /spine:review-contract -->")
check("edited generated block reported as drift", rel in wf.diff_targets(ROOT, tampered))

bad = copy.deepcopy(spine)
bad["tracks"]["non_simple"] = bad["tracks"]["non_simple"] + ["ship"]
check("on_demand stage inside a track rejected", any("on_demand" in e for e in wf.validate(bad, ROOT)))

bad = copy.deepcopy(spine)
bad["review"]["refresh_graph_before_review"] = False
check("refresh_graph_before_review=false rejected", any("refresh_graph_before_review" in e for e in wf.validate(bad, ROOT)))

bad = copy.deepcopy(spine)
bad["review"]["routing"]["extra"] = ["sre"]
check("reviewer list drift vs hooks defaults rejected", any("DEFAULT_REVIEWER_AGENTS" in e for e in wf.validate(bad, ROOT)))

frag = wf.settings_fragment(active)
check("settings fragment never sets CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL" not in frag.get("env", {}))

anth = wf.Resolved(spine, "anthropic")
user = {"env": {"CLAUDE_CODE_SUBAGENT_MODEL": "x", "KEEP": "1"}, "theme": "dark"}
on_anth, _ = wf.merge_settings(user, anth)
check("anthropic merge sets model + redirects + effort",
      on_anth.get("model") == "opus" and "ANTHROPIC_DEFAULT_OPUS_MODEL" in on_anth["env"] and "effortLevel" in on_anth)
check("merge keeps unrelated keys", on_anth["env"].get("KEEP") == "1" and on_anth.get("theme") == "dark")
on_single, _ = wf.merge_settings(on_anth, single)
check("switch to single drops alias model / redirects / effort",
      "model" not in on_single and "effortLevel" not in on_single
      and not any(k.startswith("ANTHROPIC_DEFAULT_") for k in on_single.get("env", {})))
on_kimi, _ = wf.merge_settings(on_anth, wf.Resolved(spine, "kimi"))
check("switch to kimi drops effort, repoints redirects",
      "effortLevel" not in on_kimi and on_kimi["env"]["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "k3-256k")
gateway = {"env": {"ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-5-air"}}
kept, notes = wf.merge_settings(gateway, single)
check("single keeps gateway-owned redirect", kept["env"].get("ANTHROPIC_DEFAULT_HAIKU_MODEL") == "glm-5-air"
      and any("kept env.ANTHROPIC_DEFAULT_HAIKU_MODEL" in n for n in notes))
null_env, _ = wf.merge_settings({"env": None}, single)
check("env: null tolerated (dropped, no crash)", "env" not in null_env)
check("empty env object preserved", wf.merge_settings({"env": {}}, single)[0] == {"env": {}})
check("alias session model keeps [1m] suffix", wf.merge_settings({"model": "opus[1m]"}, anth)[0]["model"] == "opus[1m]")
with tempfile.TemporaryDirectory() as tmp:
    sp = Path(tmp) / "settings.json"
    sp.write_text('{"env": null, "model": "opus"}', encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        rc = wf.main(["--root", str(ROOT), "apply-settings", "--settings", str(sp)])
    check("apply-settings dry-run tolerates env: null", rc == 0)
_, notes = wf.merge_settings({"env": {"ANTHROPIC_MODEL": "k3"}}, anth)
check("env.ANTHROPIC_MODEL override is reported", any("ANTHROPIC_MODEL" in n for n in notes))

fm = "---\nname: x\ndescription: |\n  line one\n  line two\ntools: Read\n---\nbody\n"
out = wf.set_frontmatter(fm, {"model": "opus", "effort": "high"}, "x.md")
check("frontmatter insert skips block-scalar description",
      "  line two\nmodel: opus\neffort: high\ntools: Read" in out)
check("frontmatter render idempotent", wf.set_frontmatter(out, {"model": "opus", "effort": "high"}, "x.md") == out)

sys.path.insert(0, str(ROOT / "hooks" / "_lib"))
import context_thresholds as ct  # noqa: E402

for key in wf.ALIAS_ENV.values():
    os.environ.pop(key, None)
check("alias resolves via ANTHROPIC_DEFAULT_*_MODEL",
      ct._resolve_alias("opus", {"ANTHROPIC_DEFAULT_OPUS_MODEL": "k3-256k"}) == "k3-256k")
check("alias keeps [1m] suffix",
      ct._resolve_alias("sonnet[1m]", {"ANTHROPIC_DEFAULT_SONNET_MODEL": "m"}) == "m[1m]")
check("alias without redirect untouched", ct._resolve_alias("haiku", {}) == "haiku")
check("non-alias model untouched", ct._resolve_alias("claude-opus-5-5", {}) == "claude-opus-5-5")

print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
sys.exit(1 if FAILED else 0)
