# -*- coding: utf-8 -*-
"""v11.4 IMPACT 自动登记测试（post-edit-verify-tracker.append_impact_record）。

直接运行：`python hooks/tests/test_impact_autolog.py`（退出码 0 = 全过）。
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location(
    "post_edit_verify_tracker",
    HOOKS_DIR / "post-edit-verify-tracker.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PASSED = []
FAILED = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def read_log(cwd: str) -> list:
    path = os.path.join(cwd, ".claude", "state", "impact-manifest.log")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh]


def test_autolog_writes_relative_paths() -> None:
    with tempfile.TemporaryDirectory() as td:
        f1 = str(Path(td) / "src" / "a.py")
        ok = mod.append_impact_record("s1", td, [f1])
        check("autolog returns True", ok is True)
        lines = read_log(td)
        check("autolog one line", len(lines) == 1, str(lines))
        parts = lines[0].split("|")
        check("autolog format IMPACT|session|paths|ts", len(parts) >= 4 and parts[0] == "IMPACT" and parts[1] == "s1", lines[0])
        check("autolog relative posix path", parts[2] == "src/a.py", parts[2])


def test_autolog_appends_multiple_lines() -> None:
    with tempfile.TemporaryDirectory() as td:
        mod.append_impact_record("s1", td, [str(Path(td) / "a.py")])
        mod.append_impact_record("s1", td, [str(Path(td) / "b.py")])
        lines = read_log(td)
        check("autolog appends second line", len(lines) == 2, str(lines))
        declared = set()
        for line in lines:
            parts = line.split("|")
            if len(parts) >= 3 and parts[0] == "IMPACT":
                declared.update(p for p in parts[2].split(",") if p)
        check("declared union covers both", declared == {"a.py", "b.py"}, str(declared))


def test_autolog_empty_paths_noop() -> None:
    with tempfile.TemporaryDirectory() as td:
        ok = mod.append_impact_record("s1", td, [])
        check("empty paths noop False", ok is False)
        check("no file written for empty", read_log(td) == [])


def test_tracked_edit_auto_logs_via_subprocess() -> None:
    """端到端：Edit 工具事件 → 状态追踪 + IMPACT 行同时落盘。

    前置与生产一致：payload 带 platform=claude-code；proj 须为 git 仓库
    （git_baseline 记录依赖 git status 成功）。
    """
    import subprocess

    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        env = os.environ.copy()
        env["CLAUDE_HOME"] = home
        # 生产同构：隔离 home 须带 quality_gates.json（否则 impact 门默认关）
        cfg_src = HOOKS_DIR.parent / "config" / "quality_gates.json"
        cfg_dst = Path(home) / "config"
        cfg_dst.mkdir()
        if cfg_src.exists():
            (cfg_dst / "quality_gates.json").write_text(cfg_src.read_text(encoding="utf-8"), encoding="utf-8")
        for args in (
            ["git", "init", "-q"],
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-qm", "init"],
        ):
            subprocess.run(args, cwd=proj, capture_output=True)
        target = str(Path(proj) / "x.py")
        payload = json.dumps(
            {
                "session_id": "autolog-e2e",
                "tool_name": "Edit",
                "tool_input": {"file_path": target},
                "cwd": proj,
                "platform": "claude-code",
            }
        )
        proc = subprocess.run(
            [sys.executable, str(HOOKS_DIR / "post-edit-verify-tracker.py")],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("e2e exit 0", proc.returncode == 0, proc.stderr[-300:])
        lines = [ln for ln in read_log(proj) if ln.startswith("IMPACT|autolog-e2e|")]
        check("e2e impact logged", len(lines) == 1, proc.stderr[-300:] or str(lines))
        if lines:
            check("e2e path recorded", "x.py" in lines[0].split("|")[2], lines[0])


def main() -> int:
    print("=== IMPACT autolog tests ===")
    test_autolog_writes_relative_paths()
    test_autolog_appends_multiple_lines()
    test_autolog_empty_paths_noop()
    test_tracked_edit_auto_logs_via_subprocess()
    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
