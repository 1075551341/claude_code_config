# -*- coding: utf-8 -*-
"""V20 regex fixtures: compact JSON / powershell.exe must be caught even when live files are pwsh."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("CLAUDE_HOME", str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "validate_config", ROOT / "scripts" / "validate_config.py"
)
assert _spec and _spec.loader
vc = importlib.util.module_from_spec(_spec)
sys.modules["validate_config"] = vc
_spec.loader.exec_module(vc)

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def test_powershell_command_regex() -> None:
    hit = vc.V20_POWERSHELL_COMMAND_RE.search
    check("space powershell", bool(hit('"command": "powershell"')))
    check("compact powershell", bool(hit('"command":"powershell"')))
    check("powershell.exe", bool(hit('"command": "powershell.exe"')))
    check("compact powershell.exe", bool(hit('"command":"powershell.exe"')))
    check("PowerShell.exe case", bool(hit('"command": "PowerShell.exe"')))
    check("single quotes", bool(hit("'command': 'powershell'")))
    check("pwsh not hit", hit('"command": "pwsh"') is None)
    check("npx not hit", hit('"command": "npx"') is None)
    check("winget prose not hit", hit("winget install --id Microsoft.PowerShell") is None)
    check("command pwsh nearby", hit('{"command": "pwsh", "args": ["-File"]}') is None)


def test_script_fallback_regex_positive() -> None:
    pnpm_bad = (
        'if (-not (Get-Command pnpm -EA SilentlyContinue)) {\n'
        "    npm install\n"
        "}\n"
    )
    pwsh_bad = (
        'if (-not (Get-Command pwsh)) {\n'
        "    powershell -File x.ps1\n"
        "}\n"
    )
    check(
        "pnpm→npm fallback is detected",
        bool(vc.V20_SCRIPT_PNPM_NPM_FALLBACK_RE.search(pnpm_bad)),
    )
    check(
        "pwsh→powershell fallback is detected",
        bool(vc.V20_SCRIPT_PWSH_PS_FALLBACK_RE.search(pwsh_bad)),
    )
    inventory = '@{ C = "npm"; N = "npm"; Req = $false }'
    check(
        "npm inventory is not fallback",
        vc.V20_SCRIPT_PNPM_NPM_FALLBACK_RE.search(inventory) is None,
    )
    comment = "若客户端仍 fork powershell.exe，改 mcp.json"
    check(
        "powershell.exe comment is not fallback",
        vc.V20_SCRIPT_PWSH_PS_FALLBACK_RE.search(comment) is None,
    )


def main() -> int:
    print("test_v20_toolchain")
    test_powershell_command_regex()
    test_script_fallback_regex_positive()
    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        print("FAILED:", ", ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
