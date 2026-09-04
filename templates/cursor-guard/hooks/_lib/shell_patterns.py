#!/usr/bin/env python3
"""Cursor 侧 re-export Claude SSOT shell_patterns（import_claude_lib）。"""
from __future__ import annotations

import os
from pathlib import Path

from hook_io import import_claude_lib

_mod = import_claude_lib(
    os.environ.get("CLAUDE_HOME") or str(Path.home() / ".claude"),
    "shell_patterns",
)
GIT_OPTS = _mod.GIT_OPTS
DANGER_PATTERNS = _mod.DANGER_PATTERNS
DENY_PATTERNS = _mod.DENY_PATTERNS
WARN_PATTERNS = _mod.WARN_PATTERNS
NETWORK_ASK_PATTERN = _mod.NETWORK_ASK_PATTERN
match_deny = _mod.match_deny
match_warn = _mod.match_warn
match_git_stash = _mod.match_git_stash
match_git_commit = _mod.match_git_commit
is_network_command = _mod.is_network_command
