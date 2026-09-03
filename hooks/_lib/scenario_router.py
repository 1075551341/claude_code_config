#!/usr/bin/env python3
"""场景路由加载器（v11.4.20）。

SSOT: config/scenario-router.yaml。
YAML = 分类后必加载集合 + 质量门；INDEX L3 信号仍可追加，禁止当成「只准加载这些」。
PyYAML 缺失时只返回静态指针（R16 不静默：stderr 留痕）。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
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
        "分类后 Read config/scenario-router.yaml 该场景 load.*；分类契约含 triage_map 键时 UserPrompt 注入 load 块。"
        "工具经 harness-capabilities.yaml / capability_resolver。"
        "独立审前 dual_graph_ensure；并行审查仅只读+维度不重叠+model=inherit。"
    )


def format_load_block(merged: dict[str, Any], scenario_id: str) -> str:
    load = merged.get("load") or {}
    skills = ", ".join(load.get("skills") or []) or "(none)"
    agents = ", ".join(load.get("agents") or []) or "(none)"
    caps = ", ".join(merged.get("capabilities") or []) or "(none)"
    quality = merged.get("quality") or {}
    review = ", ".join(quality.get("review") or []) or "(none)"
    vt = quality.get("verify_tier") or ""
    return (
        f"【场景 {scenario_id}】skills: {skills}\n"
        f"agents: {agents}\n"
        f"capabilities: {caps}\n"
        f"review: {review}；verify_tier={vt}；parallel_ok={quality.get('parallel_ok') is True}"
        "。INDEX L3 信号仍可追加 Read；工具经 harness-capabilities.yaml / capability_resolver。"
    )


_TRIAGE_PAIR_RE = re.compile(
    r"(简单|非简单)\s*[|｜/]\s*(文档类|实现类|配置值类|Bug类|功能类|架构类|配置类|删除类|调研类)"
)
_SCENARIO_ID_RE = re.compile(r"SCENARIO_ID\s*[=:：]\s*([a-z][a-z0-9_]*)", re.I)
_CLASSIFY_HINT_RE = re.compile(r"使用类型|分类契约|task-triage")


def sidecar_path() -> str:
    return os.path.join(_claude_home(), ".state", "last_scenario.json")


def read_sidecar() -> dict[str, Any] | None:
    path = sidecar_path()
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"scenario_router: sidecar read failed: {exc}", file=sys.stderr)
        return None
    return data if isinstance(data, dict) else None


def write_sidecar(
    scenario_id: str,
    *,
    session_id: str = "",
    verify_tier: str = "",
    triage_key: str = "",
) -> None:
    path = sidecar_path()
    directory = os.path.dirname(path)
    try:
        os.makedirs(directory, exist_ok=True)
        payload = {
            "scenario_id": scenario_id,
            "session_id": session_id,
            "verify_tier": verify_tier,
            "triage_key": triage_key,
            "ts": time.time(),
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"scenario_router: sidecar write failed: {exc}", file=sys.stderr)


def _transcript_tail(path: str, max_bytes: int = 120000) -> str:
    if not path or not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - max_bytes))
            return fh.read()
    except OSError as exc:
        print(f"scenario_router: transcript read failed: {exc}", file=sys.stderr)
        return ""


def collect_route_text(
    prompt: str,
    *,
    transcript_path: str = "",
    extra: str = "",
) -> str:
    return "\n".join(p for p in (prompt or "", extra or "", _transcript_tail(transcript_path)) if p)


def parse_triage_key(text: str, router: dict[str, Any] | None = None) -> str | None:
    """返回 triage_map 键（如 非简单|配置类）。"""
    if not text:
        return None
    if router is None:
        router = load_router() or {}
    tmap = router.get("triage_map") or {}
    normalized = text.replace("｜", "|")
    for key in tmap:
        if key in normalized:
            return key if isinstance(key, str) else None
    match = _TRIAGE_PAIR_RE.search(normalized)
    if not match:
        return None
    key = f"{match.group(1)}|{match.group(2)}"
    return key if key in tmap else None


def parse_explicit_scenario_id(text: str, router: dict[str, Any] | None = None) -> str | None:
    if not text:
        return None
    if router is None:
        router = load_router() or {}
    scenarios = router.get("scenarios") or {}
    match = _SCENARIO_ID_RE.search(text)
    if not match:
        return None
    sid = match.group(1).strip()
    return sid if sid in scenarios else None


def unmatched_interrupt_needed(text: str, router: dict[str, Any] | None = None) -> bool:
    """分类意图出现但无法映射 triage_map → 提示 interrupt，不 deny。"""
    if not text or not _CLASSIFY_HINT_RE.search(text):
        return False
    if parse_explicit_scenario_id(text, router):
        return False
    return parse_triage_key(text, router) is None


def resolve_scenario_from_text(
    text: str, router: dict[str, Any] | None = None
) -> tuple[str | None, str]:
    """(scenario_id, triage_key)."""
    if router is None:
        router = load_router() or {}
    sid = parse_explicit_scenario_id(text, router)
    if sid:
        return sid, ""
    key = parse_triage_key(text, router)
    if not key:
        return None, ""
    tmap = router.get("triage_map") or {}
    mapped = tmap.get(key)
    return (mapped if isinstance(mapped, str) else None), key


def format_unmatched_interrupt() -> str:
    return (
        "【场景路由】未命中 triage_map（unmatched=interrupt）。"
        "禁止猜场景；补全分类契约键原文（如 非简单|配置类）后再改。"
    )


def inject_for_prompt(
    prompt: str,
    *,
    session_id: str = "",
    transcript_path: str = "",
) -> str | None:
    """UserPrompt 叠加注入：命中则 format_load_block；未命中分类意图则 interrupt 提示。"""
    router = load_router()
    if not router:
        return None
    text = collect_route_text(prompt, transcript_path=transcript_path)
    if unmatched_interrupt_needed(text, router):
        return format_unmatched_interrupt()
    sid, triage_key = resolve_scenario_from_text(text, router)
    if not sid:
        side = read_sidecar()
        if (
            side
            and side.get("scenario_id")
            and (not session_id or side.get("session_id") in ("", session_id))
        ):
            sid = str(side.get("scenario_id"))
            triage_key = str(side.get("triage_key") or triage_key)
        else:
            return None
    spec = (router.get("scenarios") or {}).get(sid) or {}
    if not isinstance(spec, dict):
        return None
    merged = merge_scenario(router, spec)
    vt = str((merged.get("quality") or {}).get("verify_tier") or "")
    write_sidecar(sid, session_id=session_id, verify_tier=vt, triage_key=triage_key)
    return format_load_block(merged, sid)


def missing_scenario_sidecar_warning(session_id: str = "") -> str | None:
    """代码/配置脏集时的提醒级检查：缺场景 sidecar 则警告，不加入 Stop reasons。"""
    side = read_sidecar()
    if not side or not side.get("scenario_id"):
        return (
            "场景路由：本会话有代码/配置变更但未写入分类 sidecar。"
            "请在回复中给出 triage_map 键（如 非简单|配置类）以便注入 load 集合。"
        )
    if session_id and side.get("session_id") not in ("", session_id):
        return (
            "场景路由：last_scenario.json 属于其他 session。"
            "请重新输出分类契约键，避免沿用过期场景 load。"
        )
    return None
