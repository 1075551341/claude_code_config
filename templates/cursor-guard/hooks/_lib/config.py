#!/usr/bin/env python3
"""Cursor Guard 配置加载（~/.cursor/guard-config.json + 环境变量）。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CURSOR_DIR = Path(os.environ.get("CURSOR_HOME", Path.home() / ".cursor"))
GUARD_CONFIG = CURSOR_DIR / "guard-config.json"
STATE_DIR = CURSOR_DIR / ".state"
DEFAULT_CLAUDE_HOME = Path.home() / ".claude"

DEFAULT_COMPRESS_KEYWORDS = [
    "压缩上下文",
    "压缩 上下文",
    "compact context",
    "compact 上下文",
]

DEFAULT_EXTRACT_KEYWORDS = [
    "提取上下文",
    "提取 上下文",
    "extract context",
    "extract 上下文",
]

DEFAULT_PROMPT_KEYWORDS = [
    "/sync",
    "同步配置",
    "sync config",
    "刷新规则",
    "更新索引",
    "更新文档",
    "同步文档",
]


def _expand(path_str: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path_str)))


def _read_raw_config() -> dict:
    if not GUARD_CONFIG.exists():
        return {}
    try:
        return json.loads(GUARD_CONFIG.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cursor-guard: guard-config read failed: {e}", file=sys.stderr, flush=True)
        return {}


def load_guard_config() -> dict:
    cfg = _read_raw_config()
    legacy_ctx = cfg.get("context", {})
    comp = cfg.get("compression", {})
    sync = cfg.get("sync", {})
    explore = cfg.get("explore", {})
    shell = cfg.get("shell", {})
    secrets = cfg.get("secrets", {})

    claude_home = _expand(
        os.environ.get("CLAUDE_HOME", sync.get("claude_home", str(DEFAULT_CLAUDE_HOME)))
    )

    window_tokens = int(
        os.environ.get(
            "CURSOR_GUARD_WINDOW_TOKENS",
            comp.get("window_tokens", legacy_ctx.get("window_tokens", 200000)),
        )
    )
    warn_pct = float(
        os.environ.get(
            "CURSOR_GUARD_WARN_PCT",
            comp.get("warn_pct", legacy_ctx.get("warn_pct", 70)),
        )
    )
    force_pct = float(
        os.environ.get(
            "CURSOR_GUARD_FORCE_PCT",
            comp.get("force_pct", legacy_ctx.get("force_pct", 90)),
        )
    )

    compression = {
        "window_tokens": window_tokens,
        "warn_pct": warn_pct,
        "force_pct": force_pct,
        "reset_on_warn": comp.get("reset_on_warn", legacy_ctx.get("reset_on_warn", False)),
        "stop_nudge_at_warn": comp.get("stop_nudge_at_warn", True),
        "auto_followup_at_force": comp.get("auto_followup_at_force", True),
        "compress_prompt_keywords": comp.get(
            "compress_prompt_keywords", DEFAULT_COMPRESS_KEYWORDS
        ),
        "extract_prompt_keywords": comp.get(
            "extract_prompt_keywords", DEFAULT_EXTRACT_KEYWORDS
        ),
    }

    return {
        "version": cfg.get("version", "0"),
        "profile": os.environ.get("CURSOR_GUARD_PROFILE", cfg.get("profile", "standard")),
        "compression": compression,
        "context": compression,
        "explore": {
            "codegraph_first": explore.get("codegraph_first", True)
            and os.environ.get("CURSOR_GUARD_CODEGRAPH_FIRST", "1") != "0",
            "nudge_on_grep_read": explore.get("nudge_on_grep_read", True),
        },
        "sync": {
            "auto_on_edit": os.environ.get("CURSOR_GUARD_AUTO_SYNC", "1") != "0"
            and sync.get("auto_on_edit", True),
            "debounce_seconds": int(
                os.environ.get(
                    "CURSOR_GUARD_SYNC_DEBOUNCE",
                    sync.get("debounce_seconds", 60),
                )
            ),
            "claude_home": claude_home,
            "prompt_keywords": sync.get("prompt_keywords", DEFAULT_PROMPT_KEYWORDS),
        },
        "shell": {
            "enabled": os.environ.get("CURSOR_GUARD_SHELL", "1") != "0"
            and shell.get("enabled", True),
            "ask_network": shell.get("ask_network", True),
            "profile": shell.get("profile", "standard"),
        },
        "secrets": {
            "scan_prompts": os.environ.get("CURSOR_GUARD_SCAN_SECRETS", "1") != "0"
            and secrets.get("scan_prompts", True),
            "block_on_match": secrets.get("block_on_match", False),
        },
    }


def state_path(name: str) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / name
