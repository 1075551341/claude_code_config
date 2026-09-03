#!/usr/bin/env python3
"""场景路由加载器（v11.4.14）。

SSOT: config/scenario-router.yaml。
YAML = 分类后必加载集合 + 质量门；INDEX L3 信号仍可追加，禁止当成「只准加载这些」。
PyYAML 缺失时只返回静态指针（R16 不静默：stderr 留痕）。
"""
from __future__ import annotations

import os
import sys
from typing import Any

_HERE = os.path.dirname(os.path.abspath(__file__))
_HOOKS = os.path.dirname(_HERE)
_REPO = os.path.dirname(_HOOKS)


def _claude_home() -> str:
    env = os.environ.get("CLAUDE_HOME")
    if env and os.path.isfile(os.path.join(env, "config", "scenario-router.yaml")):
        return os.path.normpath(env)
    cand = os.path.join(_REPO, "config", "scenario-router.yaml")
    if os.path.isfile(cand):
        return _REPO
    return os.path.normpath(os.path.expanduser(os.environ.get("CLAUDE_HOME") or "~/.claude"))


def router_path() -> str:
    return os.path.join(_claude_home(), "config", "scenario-router.yaml")


def load_router() -> dict[str, Any] | None:
    path = router_path()
    if not os.path.isfile(path):
        print(f"scenario_router: missing {path}", file=sys.stderr)
        return None
    try:
        import yaml  # type: ignore
    except ImportError:
        print("scenario_router: PyYAML missing, skip parse", file=sys.stderr)
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        print(f"scenario_router: read failed: {exc}", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        print("scenario_router: YAML root is not a mapping", file=sys.stderr)
        return None
    return data


def _unique(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def merge_independent_review(defaults: Any, override: Any) -> dict[str, Any]:
    """independent_review 统一为 object。bool true=继承默认；false=关闭。"""
    base = dict(defaults) if isinstance(defaults, dict) else {}
    if override is True or override is None:
        return base
    if override is False:
        out = dict(base)
        out["enabled"] = False
        return out
    if not isinstance(override, dict):
        raise TypeError("independent_review must be an object or bool")
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            merged = dict(out[key])
            merged.update(val)
            out[key] = merged
        else:
            out[key] = val
    return out


def merge_scenario(router: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    defaults = router.get("load_defaults") or {}
    qdef = router.get("quality_defaults") or {}
    load = spec.get("load") or {}
    skills = _unique(list(defaults.get("skills") or []) + list(load.get("skills") or []))
    agents = list(load.get("agents") or [])
    rules = list(load.get("rules") or [])
    caps = _unique(list(defaults.get("capabilities") or []) + list(spec.get("capabilities") or []))
    quality = dict(qdef)
    sq = spec.get("quality") or {}
    if not isinstance(sq, dict):
        raise TypeError("scenario.quality must be a mapping")
    ir_def = qdef.get("independent_review") if isinstance(qdef, dict) else {}
    ldq = defaults.get("quality") or {}
    for key, val in sq.items():
        if key == "independent_review":
            quality[key] = merge_independent_review(ir_def, val)
        else:
            quality[key] = val
    if "independent_review" not in quality:
        quality["independent_review"] = merge_independent_review(ir_def, None)
    if ldq.get("hard_gates"):
        quality["hard_gates"] = _unique(
            list(ldq.get("hard_gates") or []) + list(quality.get("hard_gates") or [])
        )
    return {
        "load": {"skills": skills, "agents": agents, "rules": rules},
        "capabilities": caps,
        "quality": quality,
        "overlay": bool(spec.get("overlay")),
        "match": list(spec.get("match") or []),
    }


def scenario_by_triage(router: dict[str, Any], category: str, use_type: str) -> str | None:
    key = f"{(category or '').strip()}|{(use_type or '').strip()}"
    tmap = router.get("triage_map") or {}
    sid = tmap.get(key)
    return sid if isinstance(sid, str) else None


def resolve_scenario_id(router: dict[str, Any], tokens: list[str], *, overlay: bool = False) -> str | None:
    """AND + 最长 match 胜；同长 first-win。overlay=True 只竞选 overlay 场景。"""
    token_set = {t for t in tokens if t}
    scenarios = router.get("scenarios") or {}
    best_id = None
    best_len = -1
    for sid, spec in scenarios.items():
        if not isinstance(spec, dict):
            continue
        if bool(spec.get("overlay")) != overlay:
            continue
        match = [m for m in (spec.get("match") or []) if m]
        if not match:
            continue
        if not set(match).issubset(token_set):
            continue
        n = len(match)
        if n > best_len:
            best_len = n
            best_id = sid
    return best_id


def parallel_dispatch_ok(merged: dict[str, Any], models: list[str] | None = None) -> bool:
    """并行审查：defaults.parallel.enabled ∧ scenario.parallel_ok ∧ 全部 model=inherit。"""
    quality = merged.get("quality") or {}
    if quality.get("parallel_ok") is not True:
        return False
    ir = quality.get("independent_review") or {}
    parallel = ir.get("parallel") or {}
    if parallel.get("enabled") is not True:
        return False
    if parallel.get("forbid_multiplier_models") is not True:
        return False
    require = str(parallel.get("require_model") or "inherit").strip().lower()
    when = set(parallel.get("when_all") or [])
    if "model_inherit_only" not in when:
        return False
    if models is None:
        return True
    return all(str(m or "").strip().lower() == require for m in models)


def format_session_hint(router: dict[str, Any] | None = None) -> str:
    if router is None:
        router = load_router()
    if not router:
        return (
            "【场景路由】分类后 Read config/scenario-router.yaml（必加载集合+质量门；"
            "INDEX L3 信号可追加）。独立审前双图 ensure；并行审查须 model=inherit。"
        )
    n = len(router.get("scenarios") or {})
    tmap = router.get("triage_map") or {}
    map_line = "；".join(f"{k}→{v}" for k, v in tmap.items())
    return (
        f"【场景路由】task-triage 使用类型 → 下列场景（必加载+质量门，L3 INDEX 可追加；"
        f"{n} 场景）。{map_line}。"
        "分类后 Read config/scenario-router.yaml 该场景 load.*；工具经 harness-capabilities.yaml。"
        "独立审前 dual_graph_ensure；并行审查仅只读+维度不重叠+model=inherit。"
    )


def format_load_block(merged: dict[str, Any], scenario_id: str) -> str:
    load = merged.get("load") or {}
    skills = ", ".join(load.get("skills") or []) or "(none)"
    agents = ", ".join(load.get("agents") or []) or "(none)"
    caps = ", ".join(merged.get("capabilities") or []) or "(none)"
    quality = merged.get("quality") or {}
    review = ", ".join(quality.get("review") or []) or "(none)"
    return (
        f"【场景 {scenario_id}】skills: {skills}\n"
        f"agents: {agents}\n"
        f"capabilities: {caps}\n"
        f"review: {review}；parallel_ok={quality.get('parallel_ok') is True}"
    )
