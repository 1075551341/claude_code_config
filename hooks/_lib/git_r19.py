#!/usr/bin/env python3
"""R19 git 分支禁令 + R15 包管理器混用警告（Claude pre-bash-guard 与测试共用）。

Cursor Guard 的 shell_patterns.py 保持对等实现（部署副本不依赖本文件）。
"""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

_GIT_GLOBAL_WITH_ARG = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--super-prefix",
    "--config-env",
}

_NPM_INSTALL_RE = re.compile(r"\bnpm\s+(?:i|install|add|ci)\b", re.IGNORECASE)
_PIP_INSTALL_RE = re.compile(r"\bpip(?:3)?\s+install\b", re.IGNORECASE)
_UV_PIP_RE = re.compile(r"\buv\s+pip\b", re.IGNORECASE)

_BRANCH_MUTATE_FLAGS = {
    "-d",
    "-D",
    "--delete",
    "-m",
    "-M",
    "--move",
    "-c",
    "-C",
    "--copy",
}
_BRANCH_LIST_FLAGS = {
    "-a",
    "--all",
    "-r",
    "--remotes",
    "-v",
    "-vv",
    "--verbose",
    "--list",
    "--show-current",
    "--contains",
    "--merged",
    "--no-merged",
    "--points-at",
}


def git_subargv(command: str) -> list[str] | None:
    """Return git subcommand + args, skipping global git options. None if not a git invocation."""
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    i = 0
    while i < len(tokens) and tokens[i] in ("sudo", "command", "time", "nohup", "env"):
        i += 1
        while i < len(tokens) and "=" in tokens[i] and not tokens[i].startswith("-"):
            i += 1
    if i >= len(tokens):
        return None
    if tokens[i] != "git" and not str(tokens[i]).endswith("/git"):
        return None
    i += 1
    while i < len(tokens):
        t = tokens[i]
        if t in _GIT_GLOBAL_WITH_ARG:
            i += 2
            continue
        if t.startswith("--git-dir=") or t.startswith("--work-tree=") or t.startswith("--namespace="):
            i += 1
            continue
        if t.startswith("-") and t not in ("-h", "--help"):
            # --no-pager, -p (paginate), etc. before subcommand
            i += 1
            continue
        break
    return tokens[i:] if i < len(tokens) else None


def match_git_branch_mutate(command: str) -> bool:
    """True if the command creates, switches, renames, or deletes a branch (not path restore / list)."""
    argv = git_subargv(command)
    if not argv:
        return False
    sub, args = argv[0], argv[1:]
    if any(a in ("-h", "--help") for a in args) and not any(
        a in ("-b", "-B", "-c", "-C") for a in args
    ):
        return False

    if sub == "checkout":
        if any(
            a in ("-b", "-B", "--orphan") or a == "--branch" or a.startswith("--branch=")
            for a in args
        ):
            return True
        if "--" in args:
            return False
        if any(a in ("--ours", "--theirs", "--conflict") or a.startswith("--conflict=") for a in args):
            return False
        positional = [a for a in args if not a.startswith("-")]
        return bool(positional)

    if sub == "switch":
        return True

    if sub == "branch":
        if any(
            a in _BRANCH_MUTATE_FLAGS
            or a.startswith("--delete")
            or a.startswith("--move")
            or a.startswith("--copy")
            for a in args
        ):
            return True
        if any(a in _BRANCH_LIST_FLAGS for a in args):
            return False
        positional = [a for a in args if not a.startswith("-")]
        return bool(positional)

    if sub == "worktree" and args and args[0] == "add":
        return any(a in ("-b", "-B") for a in args[1:])

    return False


def _has_lockfile(cwd: str, names: tuple[str, ...]) -> bool:
    p = Path(cwd)
    for _ in range(6):
        for name in names:
            if (p / name).is_file():
                return True
        if (p / ".git").exists() or (p / ".git").is_file():
            break
        if p.parent == p:
            break
        p = p.parent
    return False


def pm_mix_warning(command: str, cwd: str | None) -> str | None:
    """Warn (do not deny) when mixing package managers against lockfiles (R15)."""
    root = cwd if cwd and os.path.isdir(cwd) else os.getcwd()
    if _has_lockfile(root, ("pnpm-lock.yaml",)) and _NPM_INSTALL_RE.search(command):
        return "R15: pnpm 仓禁止混用 npm install（幻影依赖/双 lock）— 改用 pnpm"
    if _has_lockfile(root, ("uv.lock", "poetry.lock")) and _PIP_INSTALL_RE.search(
        command
    ) and not _UV_PIP_RE.search(command):
        return "R15: uv/poetry 仓禁止裸 pip install — 改用 uv add / poetry add"
    return None
