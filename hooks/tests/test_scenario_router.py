# -*- coding: utf-8 -*-
"""scenario_router 加载语义与 independent_review 形状。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR / "_lib"))

import scenario_router as sr  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def main() -> int:
    print("=== scenario_router tests ===")
    router = sr.load_router()
    check("yaml loads", router is not None)
    if not router:
        print(f"passed={len(PASSED)} failed={len(FAILED)}")
        return 1 if FAILED else 0

    check("triage_map research is L3", router["triage_map"].get("非简单|调研类") == "research_l3")
    sid = sr.scenario_by_triage(router, "非简单", "配置类")
    check("triage config_structure", sid == "config_structure")
    spec = (router.get("scenarios") or {}).get(sid) or {}
    merged = sr.merge_scenario(router, spec)
    skills = merged["load"]["skills"]
    check("defaults include using-superpowers", "using-superpowers" in skills)
    check("defaults include task-triage", "task-triage" in skills)
    check("defaults include verification", "verification-before-completion" in skills)
    check("memory capability default", "memory" in merged["capabilities"])
    ir = merged["quality"]["independent_review"]
    check("IR is object", isinstance(ir, dict))
    check("IR before dual_graph", "dual_graph_ensure" in (ir.get("before") or []))
    check("config parallel_ok", merged["quality"].get("parallel_ok") is True)
    check("parallel inherit ok", sr.parallel_dispatch_ok(merged, ["inherit", "inherit"]))
    check("parallel rejects max", not sr.parallel_dispatch_ok(merged, ["inherit", "gpt-max"]))

    simple = sr.merge_scenario(router, router["scenarios"]["simple_docs"])
    check("simple_docs still dual-review default", simple["quality"].get("review_on_code_or_config_edit") is True)
    check("simple_docs has verification", "verification-before-completion" in simple["load"]["skills"])

    bug = sr.resolve_scenario_id(router, ["非简单", "Bug类"], overlay=False)
    check("bug_unclear unique", bug == "bug_unclear")
    dbg = sr.resolve_scenario_id(router, ["非简单", "Bug类", "调试"], overlay=True)
    check("debug is overlay", dbg == "debug")
    l1 = sr.resolve_scenario_id(router, ["调研", "L1"], overlay=False)
    check("research_l1 not primary", l1 is None)
    l3 = sr.resolve_scenario_id(router, ["非简单", "调研类"], overlay=False)
    check("research_l3 primary", l3 == "research_l3")

    vc = sr.merge_scenario(router, router["scenarios"]["verify_complete"])
    check("verify_complete IR object", isinstance(vc["quality"]["independent_review"], dict))
    check("verify_complete not parallel with implementer", vc["quality"].get("parallel_ok") is not True)

    unmatched = sr.resolve_scenario_id(router, ["未知类型"], overlay=False)
    check("unmatched interrupt", unmatched is None)

    hint = sr.format_session_hint(router)
    check("hint mentions yaml", "scenario-router.yaml" in hint)

    stop_path = HOOKS_DIR / "stop-verification-gate.py"
    src = stop_path.read_text(encoding="utf-8")
    start = src.index("DEFAULT_CFG")
    end = src.index("CODE_EXTENSIONS")
    block = src[start:end]
    check("stop DEFAULT_CFG dual graph key", "require_dual_graph_before_review" in block)
    check("stop DEFAULT_CFG parallel_review", "parallel_review" in block)

    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    os.environ.setdefault("CLAUDE_HOME", str(HOOKS_DIR.parent))
    sys.exit(main())
