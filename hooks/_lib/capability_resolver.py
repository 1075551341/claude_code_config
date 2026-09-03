#!/usr/bin/env python3
"""Harness 能力解析（v11.4.20）。

SSOT: config/harness-capabilities.yaml。
缺能力必须 fallback 或 interrupt，禁止假装已调用。
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
    if env and os.path.isfile(os.path.join(env, "config", "harness-capabilities.yaml")):
        return os.path.normpath(env)
    cand = os.path.join(_REPO, "config", "harness-capabilities.yaml")
    if os.path.isfile(cand):
        return _REPO
    return os.path.normpath(os.path.expanduser(os.environ.get("CLAUDE_HOME") or "~/.claude"))


def capabilities_path() -> str:
    return os.path.join(_claude_home(), "config", "harness-capabilities.yaml")


def load_capabilities() -> dict[str, Any] | None:
    path = capabilities_path()
    if not os.path.isfile(path):
        print(f"capability_resolver: missing {path}", file=sys.stderr)
        return None
    try:
        import yaml  # type: ignore
    except ImportError:
        print("capability_resolver: PyYAML missing, skip parse", file=sys.stderr)
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        print(f"capability_resolver: read failed: {exc}", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        print("capability_resolver: YAML root is not a mapping", file=sys.stderr)
        return None
    return data


def detect_harness() -> str:
    if os.environ.get("CURSOR_AGENT") or os.environ.get("CURSOR"):
        return "cursor"
    if os.environ.get("DSH_HOME") or os.environ.get("DEEPSEEK_HARNESS"):
        return "dsh"
    oc = os.environ.get("OPENCODE_CONFIG") or os.environ.get("OPENCODE_HOME")
    if oc:
        return "opencode"
    return "claude-code"


def _resolved_map(data: dict[str, Any], harness: str) -> dict[str, Any]:
    defaults = dict(data.get("defaults") or {})
    spec = (data.get("harnesses") or {}).get(harness) or {}
    if not isinstance(spec, dict):
        return defaults
    if spec.get("inherits") == "defaults" or "overrides" in spec:
        out = dict(defaults)
        for key, val in (spec.get("overrides") or {}).items():
            if isinstance(val, dict) and isinstance(out.get(key), dict):
                merged = dict(out[key])
                merged.update(val)
                out[key] = merged
            else:
                out[key] = val
        return out
    return defaults


def resolve_capability(
    capability: str,
    harness: str | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """返回 provider/name/fallback/interrupt/usable。

    usable=False 且无 fallback → 调用方应 interrupt，禁止假装已调用。
    """
    if data is None:
        data = load_capabilities() or {}
    hid = harness or detect_harness()
    caps = _resolved_map(data, hid)
    spec = caps.get(capability)
    if not isinstance(spec, dict):
        return {
            "capability": capability,
            "harness": hid,
            "provider": "none",
            "name": "",
            "fallback": None,
            "interrupt": True,
            "usable": False,
            "note": f"unknown capability {capability}",
        }
    provider = str(spec.get("provider") or "none")
    fallback = spec.get("fallback")
    interrupt = bool(spec.get("interrupt"))
    usable = provider not in ("none", "") or bool(fallback)
    if provider in ("none", "") and not fallback:
        interrupt = True
        usable = False
    return {
        "capability": capability,
        "harness": hid,
        "provider": provider,
        "name": spec.get("name") or "",
        "fallback": fallback,
        "interrupt": interrupt,
        "usable": usable,
        "note": spec.get("note") or "",
        "pin": spec.get("pin") or "",
    }


def format_interrupt(resolved: dict[str, Any]) -> str:
    cap = resolved.get("capability")
    hid = resolved.get("harness")
    fb = resolved.get("fallback")
    if fb:
        return (
            f"【harness {hid}】capability {cap} provider=none，改用 fallback `{fb}`。"
            "禁止假装已调用原 provider。"
        )
    return (
        f"【harness {hid}】capability {cap} 不可用且无 fallback。"
        "interrupt：禁止假装已调用。"
    )
