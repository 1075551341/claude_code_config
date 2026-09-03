#!/usr/bin/env python3
"""R19 git 分支禁令 + R15 包管理器混用警告（Claude pre-bash-guard 与测试共用）。

Cursor Guard 的 shell_patterns.py 保持对等实现（部署副本不依赖本文件）。
改本文件后必须同步 templates/cursor-guard/hooks/_lib/shell_patterns.py。
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
_PIP_INSTALL_RE = re.compile(
    r"(?:\bpip(?:3)?\s+install\b|\bpython(?:3(?:\.\d+)?)?\s+-m\s+pip\s+install\b|\bpy\s+-m\s+pip\s+install\b)",
    re.IGNORECASE,
)
_UV_PIP_RE = re.compile(r"\buv\s+pip\b", re.IGNORECASE)

_WRAPPERS = {"sudo", "command", "time", "nohup", "env"}
_SEPARATORS = {"&&", "||", ";", "|", "&"}

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


def _is_env_assign(tok: str) -> bool:
    return "=" in tok and not tok.startswith("-") and not tok.startswith("=")


def _is_git_bin(tok: str) -> bool:
    base = tok.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return tok == "git" or base in ("git", "git.exe")


def _skip_git_globals(tokens: list[str], i: int) -> int:
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t in _SEPARATORS:
            break
        if t in _GIT_GLOBAL_WITH_ARG:
            i += 2
            continue
        if t.startswith("--git-dir=") or t.startswith("--work-tree=") or t.startswith("--namespace="):
            i += 1
            continue
        if t.startswith("-") and t not in ("-h", "--help"):
            i += 1
            continue
        break
    return i


def _split_compound(command: str) -> list[str]:
    """Split on && / || / ; / | / newlines outside quotes (shlex keeps 'true;' as one token)."""
    s = command.replace("\r\n", "\n")
    out: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if quote:
            buf.append(c)
            if c == "\\" and quote == '"' and i + 1 < n:
                buf.append(s[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in ("'", '"'):
            quote = c
            buf.append(c)
            i += 1
            continue
        if c == "\n" or c == ";":
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            i += 1
            continue
        if s.startswith("&&", i) or s.startswith("||", i):
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            i += 2
            continue
        if c == "|":
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    part = "".join(buf).strip()
    if part:
        out.append(part)
    return out


def _one_git_subargv(segment: str) -> list[str] | None:
    try:
        tokens = shlex.split(segment, posix=True)
    except ValueError:
        tokens = segment.split()
    i = 0
    n = len(tokens)
    while i < n and _is_env_assign(tokens[i]):
        i += 1
    while i < n and tokens[i] in _WRAPPERS:
        i += 1
        while i < n and _is_env_assign(tokens[i]):
            i += 1
    if i >= n or not _is_git_bin(tokens[i]):
        return None
    i += 1
    i = _skip_git_globals(tokens, i)
    return tokens[i:] if i < n else None


def iter_git_subargvs(command: str) -> list[list[str]]:
    """Every git subcommand argv in a compound command (&& / ; / | / env prefix)."""
    out: list[list[str]] = []
    for seg in _split_compound(command):
        argv = _one_git_subargv(seg)
        if argv:
            out.append(argv)
    return out


def git_subargv(command: str) -> list[str] | None:
    """First git subcommand + args in the command line. None if no git invocation."""
    found = iter_git_subargvs(command)
    return found[0] if found else None


def _checkout_is_mutate(args: list[str]) -> bool:
    if any(
        a in ("-b", "-B", "--orphan") or a == "--branch" or a.startswith("--branch=")
        for a in args
    ):
        return True
    if "--" in args:
        return False
    if any(a in ("--ours", "--theirs", "--conflict") or a.startswith("--conflict=") for a in args):
        return False
    positional: list[str] = []
    for a in args:
        if a == "-":
            positional.append(a)
        elif a.startswith("-"):
            continue
        else:
            positional.append(a)
    if not positional:
        return False
    if positional[0] == "-":
        return True
    if any(
        p in (".", "..") or p.startswith("./") or p.startswith("../") for p in positional
    ):
        return False
    if len(positional) >= 2:
        return False
    return True


def _argv_is_branch_mutate(argv: list[str]) -> bool:
    if not argv:
        return False
    sub, args = argv[0], argv[1:]
    if any(a in ("-h", "--help") for a in args) and not any(
        a in ("-b", "-B", "-c", "-C") for a in args
    ):
        return False

    if sub == "checkout":
        return _checkout_is_mutate(args)

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


def match_git_branch_mutate(command: str) -> bool:
    """True if any git invocation creates, switches, renames, or deletes a branch."""
    return any(_argv_is_branch_mutate(argv) for argv in iter_git_subargvs(command))


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
