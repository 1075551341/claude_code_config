# -*- coding: utf-8 -*-
"""Guard sync_runner: resolve_pwsh is pwsh-only; missing → BLOCKED."""
from __future__ import annotations

import inspect
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates" / "cursor-guard" / "hooks" / "_lib"))

import sync_runner as sr  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def test_resolve_pwsh() -> None:
    src = inspect.getsource(sr.resolve_pwsh)
    check("resolve_pwsh calls which(pwsh)", 'which("pwsh")' in src)
    check("resolve_pwsh source has no powershell", "powershell" not in src)

    runner = inspect.getsource(sr)
    check("runner does not which powershell", 'which("powershell")' not in runner)
    check("runner does not quote powershell.exe", '"powershell.exe"' not in runner)
    check('runner does not quote "powershell"', '"powershell"' not in runner)

    with patch.object(sr.shutil, "which") as which:
        which.return_value = "/usr/bin/pwsh"
        got = sr.resolve_pwsh()
        check("resolve_pwsh returns which result", got == "/usr/bin/pwsh")
        check("which called once with pwsh", which.call_args == (("pwsh",),))

    with patch.object(sr.shutil, "which", return_value=None) as which:
        pwsh, err = sr.pwsh_or_blocked()
        check("missing pwsh returns None", pwsh is None)
        check("missing names 7.5+", "7.5" in err)
        check("missing forbids 5.1", "5.1" in err)
        check("missing names pwsh", err.startswith("pwsh"))
        check("missing does not suggest powershell.exe", "powershell.exe" not in err)
        which.assert_called_with("pwsh")
        check("missing which was pwsh", which.call_args == (("pwsh",),))


def main() -> int:
    print("test_guard_sync_runner")
    test_resolve_pwsh()
    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        print("FAILED:", ", ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
