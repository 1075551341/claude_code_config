# -*- coding: utf-8 -*-
"""R15 语言/OS 检测 + R19 分支 deny 模式。"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS / "_lib"))

from shell_patterns import match_deny  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "session_start_bootstrap",
    HOOKS / "session-start-bootstrap.py",
)
assert _spec and _spec.loader
ssb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ssb)


def test_r19_branch_deny() -> None:
    assert match_deny("git checkout -b feature-x")
    assert match_deny("git switch -c feature-x")
    assert match_deny("git branch feature-x")
    assert match_deny("git -C /tmp checkout main")
    assert match_deny("git switch main")
    assert match_deny("git stash")
    assert match_deny("git commit -m x")
    assert match_deny("git worktree add --branch new ../dir main")
    assert match_deny("cmd.exe /c dir")
    assert match_deny("powershell.exe -Command Get-Date")
    assert match_deny("git branch -c old new")
    assert match_deny("powershell -Command Get-Date")


def test_r19_branch_allow() -> None:
    assert match_deny("git status") is None
    assert match_deny("git branch") is None
    assert match_deny("git branch -vv") is None
    assert match_deny("git branch --list") is None
    assert match_deny("git checkout -- README.md") is None
    assert match_deny("git checkout HEAD -- README.md") is None
    assert match_deny("git log") is None
    assert match_deny("git worktree add ../x main") is None
    assert match_deny("pwsh -NoProfile -File scripts/sync.ps1") is None
    assert match_deny("powershell.exe -File python-mcp.ps1") is None


def test_r15_lang_java() -> None:
    root = Path(tempfile.mkdtemp())
    (root / "pom.xml").write_text("<project/>", encoding="utf-8")
    assert ssb.detect_project_language(str(root)) == "java"


def test_r15_lang_javascript(tmp_path: Path | None = None) -> None:
    root = Path(tempfile.mkdtemp()) if tmp_path is None else tmp_path
    (root / "package.json").write_text("{}", encoding="utf-8")
    assert ssb.detect_project_language(str(root)) == "javascript"
    pm = ssb.detect_package_manager(str(root))
    assert pm in ("pnpm", "npm")
    line = ssb.format_r15_lang(str(root))
    assert line and "javascript" in line and "pnpm" in line
    if shutil.which("pnpm"):
        assert "已兜底" not in line


def test_r15_lang_python() -> None:
    root = Path(tempfile.mkdtemp())
    (root / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
    assert ssb.detect_project_language(str(root)) == "python"
    line = ssb.format_r15_lang(str(root))
    assert line and "python" in line and ("uv" in line or "pip" in line)


def test_r15_os_line() -> None:
    line = ssb.detect_r15_os()
    assert line.startswith("R15 OS:")
    if sys.platform == "win32":
        assert "pwsh" in line
        assert "powershell.exe" not in line.lower() or "禁止" in line


def main() -> None:
    test_r19_branch_deny()
    test_r19_branch_allow()
    test_r15_lang_javascript()
    test_r15_lang_python()
    test_r15_lang_java()
    test_r15_os_line()
    print("test_r15_r19: ok")


if __name__ == "__main__":
    main()
