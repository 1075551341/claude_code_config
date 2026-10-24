#!/usr/bin/env python3
"""
Claude Code 上下文窗口与压缩阈值 SSOT（模型无关：本包不登记任何厂商模型）。

模型最大窗口 known_context_tokens（未知返回 None）：
  1. env.CLAUDE_CODE_MAX_CONTEXT_TOKENS
  2. 模型名后缀 [1M] / [200K] / …
  3. config/model-context-windows.json model_tokens（出厂为空，用户本机自行登记）
  4. 无模型名时：claude-hud context-cache 实测 context_window_size

有效压缩窗口 ctx_window_tokens：
  1. env.CLAUDE_CODE_AUTO_COMPACT_WINDOW / settings.json autoCompactWindow（已知最大窗口时封顶）
  2. 已知最大窗口
  3. registry.default_tokens（保守默认 200K）

阈值：CLAUDE_COMPACT_WARN_PCT=70 / FORCE_PCT=90 / CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70（原生自动 /compact）

Cursor 侧独立：templates/cursor-guard/guard-config.json
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path

DEFAULT_WARN_PCT = 70.0
DEFAULT_FORCE_PCT = 90.0
DEFAULT_AUTOCOMPACT_PCT = 70.0

_SUFFIX_RE = re.compile(r"\[([0-9]+[KkMm]?)\]\s*$")
_CLAUDE_HOME = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))


def _settings_path() -> Path:
    return _CLAUDE_HOME / "settings.json"


def _registry_path() -> Path:
    return _CLAUDE_HOME / "config" / "model-context-windows.json"


@lru_cache(maxsize=1)
def _load_settings() -> dict:
    path = _settings_path()
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return {}


@lru_cache(maxsize=1)
def _load_registry() -> dict:
    path = _registry_path()
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return {
        "suffix_tokens": {"1M": 1_000_000, "200K": 200_000, "128K": 128_000},
        "model_tokens": {},
        "default_tokens": 200_000,
    }


def _parse_suffix_tokens(suffix: str, registry: dict) -> int | None:
    key = suffix.upper()
    table = registry.get("suffix_tokens") or {}
    if key in table:
        return int(table[key])
    m = re.fullmatch(r"(\d+)([KkMm]?)", suffix)
    if not m:
        return None
    num = int(m.group(1))
    unit = m.group(2).upper()
    if unit in ("M",):
        return num * 1_000_000
    if unit in ("K", ""):
        return num * 1_000
    return None


def _strip_model_suffix(model: str) -> tuple[str, int | None]:
    model = (model or "").strip()
    m = _SUFFIX_RE.search(model)
    if not m:
        return model, None
    base = model[: m.start()].rstrip()
    registry = _load_registry()
    return base, _parse_suffix_tokens(m.group(1), registry)


def active_model_name() -> str:
    settings = _load_settings()
    env_block = settings.get("env") or {}
    name = ""
    val = os.environ.get("ANTHROPIC_MODEL") or env_block.get("ANTHROPIC_MODEL") or settings.get("model")
    name = str(val).strip() if val else ""
    return name


def _hud_observed_window() -> int | None:
    cache_dir = _CLAUDE_HOME / "plugins" / "claude-hud" / "context-cache"
    if not cache_dir.is_dir():
        return None
    best: tuple[int, int] | None = None
    for path in cache_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            window = data.get("context_window_size")
            saved = int(data.get("saved_at") or 0)
            if isinstance(window, int) and window > 0:
                if best is None or saved >= best[0]:
                    best = (saved, window)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
    return best[1] if best else None


def known_context_tokens(model: str | None = None) -> int | None:
    """可确认的模型最大上下文；无法确认（未知模型、无后缀、未登记）返回 None。"""
    override = os.environ.get("CLAUDE_CODE_MAX_CONTEXT_TOKENS")
    if override:
        try:
            return max(1, int(override))
        except ValueError:
            pass
    name = model.strip() if model else active_model_name()
    if name:
        base, suffix_tokens = _strip_model_suffix(name)
        if suffix_tokens:
            return suffix_tokens
        models = _load_registry().get("model_tokens") or {}
        for key in (base, name):
            if key in models:
                return int(models[key])
        # 未登记模型：不猜，也不用 HUD 缓存（避免换模型后沿用旧窗口）
        return None
    return _hud_observed_window()


def _default_tokens() -> int:
    return int(_load_registry().get("default_tokens") or 200_000)


def _explicit_compact_window() -> int | None:
    val = os.environ.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if val:
        try:
            return max(1, int(val))
        except ValueError:
            pass
    settings = _load_settings()
    window = settings.get("autoCompactWindow")
    if isinstance(window, int) and window > 0:
        return window
    return None


def resolve_model_context_tokens(model: str | None = None) -> int:
    """模型最大上下文：已知值 > 用户显式窗口（未知模型时以调用方设置为准）> 保守默认。"""
    known = known_context_tokens(model)
    if known is not None:
        return known
    return _explicit_compact_window() or _default_tokens()


def ctx_window_tokens(model: str | None = None) -> int:
    """Hook / 估算用有效窗口：显式配置在已知最大窗口内封顶。"""
    known = known_context_tokens(model)
    explicit = _explicit_compact_window()
    if explicit is not None:
        return min(explicit, known) if known is not None else explicit
    return known if known is not None else _default_tokens()


def recommended_autocompact_window(model: str | None = None) -> int:
    """settings.json autoCompactWindow 推荐值（已知最大窗口；未知时保留调用方显式值）。"""
    return resolve_model_context_tokens(model)


def sync_settings_compact_window(*, write: bool = True) -> dict:
    """
    已知模型窗口时把 settings.json 的 autoCompactWindow 同步为该值；未知模型且已有显式值时不动。
    移除 env 中冗余的 CLAUDE_CODE_AUTO_COMPACT_WINDOW（由 resolver 动态推导）。
    """
    path = _settings_path()
    result = {
        "model": active_model_name(),
        "known_window": known_context_tokens(),
        "resolved_window": recommended_autocompact_window(),
        "previous_window": None,
        "updated": False,
        "removed_env_compact_window": False,
    }
    if not path.is_file():
        return result

    settings = json.loads(path.read_text(encoding="utf-8"))
    result["previous_window"] = settings.get("autoCompactWindow")
    target = result["resolved_window"]
    changed = False

    if settings.get("autoCompactWindow") != target:
        settings["autoCompactWindow"] = target
        changed = True

    env_block = settings.get("env") or {}
    if "CLAUDE_CODE_AUTO_COMPACT_WINDOW" in env_block:
        del env_block["CLAUDE_CODE_AUTO_COMPACT_WINDOW"]
        settings["env"] = env_block
        result["removed_env_compact_window"] = True
        changed = True

    if changed and write:
        path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _load_settings.cache_clear()

    result["updated"] = changed
    return result


def ctx_warn_pct() -> float:
    return float(os.environ.get("CLAUDE_COMPACT_WARN_PCT", str(DEFAULT_WARN_PCT)))


def ctx_force_pct() -> float:
    return float(os.environ.get("CLAUDE_COMPACT_FORCE_PCT", str(DEFAULT_FORCE_PCT)))


def autocompact_trigger_pct() -> float:
    settings = _load_settings()
    env_block = settings.get("env") or {}
    raw = os.environ.get("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE") or env_block.get(
        "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", str(DEFAULT_AUTOCOMPACT_PCT)
    )
    try:
        return float(raw)
    except (TypeError, ValueError):
        return DEFAULT_AUTOCOMPACT_PCT


def estimate_usage_pct(est_tokens: int, model: str | None = None) -> float:
    window = ctx_window_tokens(model)
    if window <= 0 or est_tokens <= 0:
        return 0.0
    return min(100.0, (est_tokens / window) * 100.0)


def context_level(est_pct: float) -> str:
    if est_pct >= ctx_force_pct():
        return "force"
    if est_pct >= ctx_warn_pct():
        return "warn"
    return "normal"
