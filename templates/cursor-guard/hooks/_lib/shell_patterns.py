#!/usr/bin/env python3
"""精简 Shell 危险模式（Cursor beforeShellExecution，独立于 Claude hooks）。"""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

# Git 命令选项前缀（防 -C/--git-dir/--work-tree/-c 变体绕过；支持空格/等号分隔，对齐 Claude pre-bash-guard）
_GIT_OPTS = r"(?:(?:-C|-c|--git-dir|--work-tree)(?:\s+|=)\S+(?:\s+|))*"

DENY_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+.*-[rRfF]{1,4}\s+/$", "禁止删除根目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/\*", "禁止删除根目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~\s*$", "禁止删除用户主目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~/?\*", "禁止删除用户主目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+[\"']?C:\\\\?\*", "禁止删除 C 盘所有文件"),
    (r"^format\s+[A-Za-z]:", "禁止格式化磁盘"),
    (r"^mkfs\b", "禁止格式化分区"),
    (r"\bgit\s+" + _GIT_OPTS + r"push\s+(?!.*--dry-run).*(?:--force|-f)\s+\S*origin\s+(main|master|release|prod)\b", "禁止强制推送到保护分支"),
    (r"\bgit\s+" + _GIT_OPTS + r"push\s+(?!.*--dry-run)\S*origin\s+(main|master)\b(?!\s*--force)", "禁止直接推送到 main/master，请走 PR"),
    (r"\bDROP\s+DATABASE\b", "禁止删除数据库"),
    (r"\bDROP\s+TABLE\b", "禁止删除数据表"),
    (r"redis-cli\s+.*\bFLUSHALL\b", "禁止 FLUSHALL"),
    (r"curl\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 curl 管道直接执行脚本"),
    (r"wget\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 wget 管道直接执行脚本"),
]

WARN_PATTERNS: list[tuple[str, str]] = [
    (r"sudo\s+rm\s+.*-[rRfF]", "sudo rm -rf 请确认目标路径"),
    (r"git\s+reset\s+--hard\b", "git reset --hard 会丢弃工作区修改"),
    (r"git\s+clean\s+.*-f", "git clean 会删除未跟踪文件"),
    (r"docker\s+(?:system|volume|image)\s+prune\b", "docker prune 请确认范围"),
]

_GIT_STASH_RE = re.compile(r"\bgit\s+" + _GIT_OPTS + r"stash\b", re.IGNORECASE)
_GIT_COMMIT_RE = re.compile(r"\bgit\s+" + _GIT_OPTS + r"commit\b", re.IGNORECASE)

# 与 hooks/_lib/git_r19.py 对等（部署副本不 import 该文件）
_GIT_GLOBAL_WITH_ARG = {
    "-C",
    "-c",
    "--git-dir",
    "--work-tree",
    "--namespace",
    "--super-prefix",
    "--config-env",
}
_BRANCH_MUTATE_FLAGS = {
    "-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy",
}
_BRANCH_LIST_FLAGS = {
    "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--list",
    "--show-current", "--contains", "--merged", "--no-merged", "--points-at",
}
_NPM_INSTALL_RE = re.compile(r"\bnpm\s+(?:i|install|add|ci)\b", re.IGNORECASE)
_PIP_INSTALL_RE = re.compile(
    r"(?:\bpip(?:3)?\s+install\b|\bpython(?:3(?:\.\d+)?)?\s+-m\s+pip\s+install\b|\bpy\s+-m\s+pip\s+install\b)",
    re.IGNORECASE,
)
_UV_PIP_RE = re.compile(r"\buv\s+pip\b", re.IGNORECASE)
_WRAPPERS = {"sudo", "command", "time", "nohup", "env"}
_SEPARATORS = {"&&", "||", ";", "|", "&"}


def match_git_stash(command: str) -> bool:
    return bool(_GIT_STASH_RE.search(command))


def match_git_commit(command: str) -> bool:
    return bool(_GIT_COMMIT_RE.search(command))


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
    out: list[list[str]] = []
    for seg in _split_compound(command):
        argv = _one_git_subargv(seg)
        if argv:
            out.append(argv)
    return out


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
    root = cwd if cwd and os.path.isdir(cwd) else os.getcwd()
    if _has_lockfile(root, ("pnpm-lock.yaml",)) and _NPM_INSTALL_RE.search(command):
        return "R15: pnpm 仓禁止混用 npm install（幻影依赖/双 lock）— 改用 pnpm"
    if _has_lockfile(root, ("uv.lock", "poetry.lock")) and _PIP_INSTALL_RE.search(
        command
    ) and not _UV_PIP_RE.search(command):
        return "R15: uv/poetry 仓禁止裸 pip install — 改用 uv add / poetry add"
    return None


NETWORK_ASK_PATTERN = re.compile(r"\b(curl|wget|nc)\s", re.IGNORECASE)


def match_deny(command: str) -> str | None:
    for pattern, reason in DENY_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
            return reason
    return None


def match_warn(command: str) -> str | None:
    for pattern, reason in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
            return reason
    return None


def is_network_command(command: str) -> bool:
    return bool(NETWORK_ASK_PATTERN.search(command))
