#!/usr/bin/env python3
"""Cursor 侧 re-export Claude SSOT secret_patterns（import_claude_lib）。"""
from __future__ import annotations

import os
from pathlib import Path

from hook_io import import_claude_lib

_mod = import_claude_lib(
    os.environ.get("CLAUDE_HOME") or str(Path.home() / ".claude"),
    "secret_patterns",
)
SECRET_PATTERNS = [(p, d) for p, d, *_rest in _mod.SECRET_PATTERNS]
find_secrets = _mod.find_secrets
is_safe_context = _mod.is_safe_context
SAFE_CONTEXTS = _mod.SAFE_CONTEXTS
SAFE_FILE_PATTERNS = _mod.SAFE_FILE_PATTERNS
