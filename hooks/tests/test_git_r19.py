# -*- coding: utf-8 -*-
"""R19 分支禁令 + R15 包管理器混用警告。

直接运行：`python hooks/tests/test_git_r19.py`（退出码 0 = 全过）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR / "_lib"))

from git_r19 import match_git_branch_mutate, pm_mix_warning, detect_package_manager  # noqa: E402

GUARD_PATTERNS = (
    HOOKS_DIR.parent / "templates" / "cursor-guard" / "hooks" / "_lib" / "shell_patterns.py"
)

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        PASSED.append(name)
    else:
        FAILED.append(f"{name}: {detail}")


def test_branch_mutate() -> None:
    deny = [
        "git checkout -b feature/x",
        "git checkout -B feature/x",
        "git switch -c feature/x",
        "git switch main",
        "git checkout main",
        "git checkout -",
        "git branch feature/x",
        "git worktree add -b topic ../wt",
        "git -C /tmp/repo checkout -b foo",
        "git branch -d old",
        "git branch -m newname",
        "cd /tmp && git checkout -b feat",
        "true; git switch -c x",
        "true;git switch -c z",
        "GIT_DIR=/tmp git checkout -b x",
        "env GIT_DIR=/tmp git switch -c y",
        "git status && git checkout -b foo",
        'bash -c "git checkout -b feat"',
        "eval git checkout -b feat",
        'eval "git checkout -b feat"',
        "(git checkout -b feat)",
        "timeout 5 git checkout -b x",
        "nice git switch -c x",
        "git checkout $(echo main)",
        "git worktree add ../wt",
        "git checkout main --",
        'pwsh -Command "git checkout -b feat"',
        'pwsh.exe -c "git checkout -b feat"',
        'cmd /c "git checkout -b feat"',
        "true & git checkout -b feat",
        "git status & git checkout -b feat",
        "pwsh -Command { git checkout -b feat }",
        "pwsh -Command '& { git checkout -b feat }'",
        "{ git checkout -b feat; }",
        "env -i git checkout -b feat",
    ]
    allow = [
        "git status",
        "git diff",
        "git log -1",
        "git branch",
        "git branch -a",
        "git branch -vv",
        "git branch --list",
        "git checkout -- README.md",
        "git checkout HEAD -- src/a.py",
        "git checkout .",
        "git checkout HEAD file",
        "git restore src/a.py",
        "git add CORE.md",
        "python --version",
        "git commit -m msg",
        "git stash",
        "echo git checkout -b foo",
        "cd /tmp && git status",
        "git branch --format '%(refname:short)'",
        "git branch --format='%(refname:short)'",
        "git worktree add --detach ../wt",
        "git worktree list",
    ]
    for cmd in deny:
        check(f"deny:{cmd}", match_git_branch_mutate(cmd), "expected mutate=True")
    for cmd in allow:
        check(f"allow:{cmd}", not match_git_branch_mutate(cmd), "expected mutate=False")


def test_pm_mix() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n", encoding="utf-8")
        msg = pm_mix_warning("npm install lodash", str(root))
        check("pnpm+npm", msg is not None and "pnpm" in msg)
        check("pnpm+yarn", pm_mix_warning("yarn add lodash", str(root)) is not None)
        check("pnpm+pnpm", pm_mix_warning("pnpm add lodash", str(root)) is None)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        msg = pm_mix_warning("pip install requests", str(root))
        check("uv+pip", msg is not None and "uv" in msg)
        check("uv+python-m-pip", pm_mix_warning("python -m pip install requests", str(root)) is not None)
        check("uv+uv", pm_mix_warning("uv add requests", str(root)) is None)
        check("uv+uv-pip", pm_mix_warning("uv pip install requests", str(root)) is None)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "poetry.lock").write_text("# poetry\n", encoding="utf-8")
        msg = pm_mix_warning("pip install requests", str(root))
        check("poetry+pip", msg is not None and "poetry" in msg)
        check("poetry+python-m-pip", pm_mix_warning("python3 -m pip install x", str(root)) is not None)
        check("poetry+uv-pip", pm_mix_warning("uv pip install x", str(root)) is not None)


def test_detect_package_manager() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "package-lock.json").write_text("{}\n", encoding="utf-8")
        (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n", encoding="utf-8")
        check("dual-lock-pnpm", detect_package_manager(str(root)) == "pnpm")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        check("uv-lock", detect_package_manager(str(root)) == "uv")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        check("pyproject-uv", detect_package_manager(str(root)) == "uv")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "package.json").write_text('{"packageManager":"pnpm@9.0.0"}\n', encoding="utf-8")
        check("pkg-manager-field", detect_package_manager(str(root)) == "pnpm")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        child = root / "packages" / "app"
        child.mkdir(parents=True)
        (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n", encoding="utf-8")
        check("walk-up-pnpm", detect_package_manager(str(child)) == "pnpm")


def test_pre_bash_guard_fixtures() -> None:
    guard = HOOKS_DIR / "pre-bash-guard.py"
    cases = [
        ("git checkout -b feature/x", 2, True),
        ("git switch -c topic", 2, True),
        ("cd /tmp && git checkout -b feat", 2, True),
        ("GIT_DIR=/tmp git checkout -b x", 2, True),
        ("git checkout -", 2, True),
        ('bash -c "git checkout -b feat"', 2, True),
        ("eval git checkout -b feat", 2, True),
        ("(git checkout -b feat)", 2, True),
        ("timeout 5 git checkout -b x", 2, True),
        ("git worktree add ../wt", 2, True),
        ("git checkout main --", 2, True),
        ('pwsh -Command "git checkout -b feat"', 2, True),
        ('cmd /c "git checkout -b feat"', 2, True),
        ("true & git checkout -b feat", 2, True),
        ("pwsh -Command { git checkout -b feat }", 2, True),
        ("env -i git checkout -b feat", 2, True),
        ("{ git checkout -b feat; }", 2, True),
        ("git checkout -- README.md", 0, False),
        ("git worktree add --detach ../wt", 0, False),
        ("git checkout .", 0, False),
        ("git checkout HEAD file", 0, False),
        ("git status", 0, False),
    ]
    for cmd, expect_code, must_block in cases:
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        proc = subprocess.run(
            [sys.executable, str(guard)],
            input=payload,
            text=True,
            capture_output=True,
            cwd=str(HOOKS_DIR.parent),
        )
        blocked = proc.returncode == 2
        check(
            f"hook:{cmd}",
            proc.returncode == expect_code and blocked == must_block,
            f"code={proc.returncode} stderr={proc.stderr[:200]}",
        )


def test_cursor_shell_patterns_parity() -> None:
    if not GUARD_PATTERNS.is_file():
        FAILED.append("missing cursor-guard shell_patterns.py")
        return
    import importlib.util

    spec = importlib.util.spec_from_file_location("shell_patterns", GUARD_PATTERNS)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    samples = [
        "git checkout -b x",
        "git switch main",
        "git checkout -- file",
        "git checkout .",
        "git checkout -",
        "cd /tmp && git checkout -b feat",
        "GIT_DIR=/tmp git checkout -b x",
        'bash -c "git checkout -b feat"',
        "eval git checkout -b feat",
        "(git checkout -b feat)",
        "timeout 5 git checkout -b x",
        "nice git switch -c x",
        "git checkout $(echo main)",
        "git worktree add ../wt",
        "git worktree add --detach ../wt",
        'pwsh -Command "git checkout -b feat"',
        "true & git checkout -b feat",
        "pwsh -Command { git checkout -b feat }",
        "env -i git checkout -b feat",
        "git branch --format '%(refname:short)'",
        "git branch -a",
        "git status",
        "echo git checkout -b foo",
    ]
    for cmd in samples:
        a = match_git_branch_mutate(cmd)
        b = mod.match_git_branch_mutate(cmd)
        check(f"parity:{cmd}", a == b, f"claude={a} cursor={b}")


def main() -> int:
    test_branch_mutate()
    test_pm_mix()
    test_detect_package_manager()
    test_pre_bash_guard_fixtures()
    test_cursor_shell_patterns_parity()
    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    for item in FAILED:
        print("FAIL", item)
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
