#!/usr/bin/env python3
"""Optional project formatter. Not registered globally; never downloads tools."""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_lib"))
from tool_paths import extract_edit_paths, is_edit_tool


def run(command: list[str], cwd: Path) -> bool:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"formatter failed: {type(exc).__name__}", file=sys.stderr)
        return False
    if result.returncode:
        print(f"formatter failed: exit={result.returncode}; run the project's formatter directly for diagnostics", file=sys.stderr)
        return False
    return True


def find_project(path: Path) -> Path | None:
    for directory in (path.parent, *path.parent.parents):
        if any((directory / name).exists() for name in ("package.json", "pyproject.toml", "go.mod", "Cargo.toml", ".git")):
            return directory
    return None


def formatter(path: Path, project: Path) -> list[str] | None:
    """Require a project formatter config even when a global binary exists."""
    ext = path.suffix.lower()
    if ext in {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".json", ".md", ".html", ".yaml", ".yml"}:
        configured = any(project.glob(".prettierrc*")) or any(project.glob("prettier.config.*"))
        package = project / "package.json"
        if package.exists():
            configured = configured or "prettier" in json.loads(package.read_text(encoding="utf-8"))
        if not configured:
            return None
        candidates = (project / "node_modules/.bin/prettier.cmd", project / "node_modules/.bin/prettier")
        executable = next((str(p) for p in candidates if p.is_file()), None) or shutil.which("prettier")
        return [executable, "--write", "--end-of-line", "auto", str(path)] if executable else None
    if ext == ".py":
        tools = {}
        config = project / "pyproject.toml"
        if config.exists():
            tools = tomllib.loads(config.read_text(encoding="utf-8")).get("tool", {})
        for tool in ("ruff", "black"):
            configured = tool in tools or (tool == "ruff" and any((project / name).exists() for name in ("ruff.toml", ".ruff.toml")))
            if not configured:
                continue
            local = project / ".venv" / ("Scripts" if os.name == "nt" else "bin") / (tool + (".exe" if os.name == "nt" else ""))
            executable = str(local) if local.is_file() else shutil.which(tool)
            if executable:
                return [executable, "format", str(path)] if tool == "ruff" else [executable, str(path)]
    if ext == ".rs" and any((project / name).is_file() for name in ("rustfmt.toml", ".rustfmt.toml")):
        executable = shutil.which("rustfmt")
        return [executable, str(path)] if executable else None
    opt_in = project / ".claude/format.json"
    if ext == ".go" and opt_in.exists() and json.loads(opt_in.read_text(encoding="utf-8")).get("gofmt") is True:
        executable = shutil.which("gofmt")
        return [executable, "-w", str(path)] if executable else None
    return None


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if not is_edit_tool(str(data.get("tool_name", "")), data.get("tool_input", {})):
            return 0
        failed = False
        for value in extract_edit_paths(data.get("tool_input", {}), str(data.get("cwd", ""))):
            path = Path(value)
            if not path.is_file():
                continue
            project = find_project(path)
            command = formatter(path, project) if project else None
            if command and not run(command, project):
                failed = True
        return 1 if failed else 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"formatter configuration failed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
