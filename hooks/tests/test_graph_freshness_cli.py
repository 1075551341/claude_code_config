#!/usr/bin/env python3
"""Tests for portable graph-freshness CLI (templates/editor-graph-hooks)."""
from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(ROOT / "templates" / "editor-graph-hooks"))
import graph_freshness_cli as cli  # noqa: E402

FAILED = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILED
    status = "OK" if cond else "FAIL"
    extra = f" {detail}" if detail and not cond else ""
    print(f"  [{status}] {name}{extra}")
    if not cond:
        FAILED += 1


def test_status_nongit() -> None:
    orig = sys.stdout
    sys.stdout = io.StringIO()
    try:
        with tempfile.TemporaryDirectory() as td:
            code = cli.main(["status", "--cwd", td])
        check("nongit status exit 0", code == 0)
    finally:
        sys.stdout = orig


def test_ensure_and_refresh_json() -> None:
    def fake_run(argv, cwd, timeout_sec):
        joined = " ".join(str(a) for a in argv)
        root = Path(cwd)
        if "init" in joined or "sync" in joined:
            (root / ".codegraph").mkdir(exist_ok=True)
            (root / ".codegraph" / "config.json").write_text("{}", encoding="utf-8")
        if "build" in joined or "update" in joined:
            (root / ".code-review-graph").mkdir(exist_ok=True)
            (root / ".code-review-graph" / "graph.db").write_bytes(b"")
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    orig_run = cli.run_cmd
    orig_which = cli.which_tool
    orig_out = sys.stdout
    buf = io.StringIO()
    cli.run_cmd = fake_run  # type: ignore[method-assign]
    cli.which_tool = lambda name: f"/bin/{name}"  # type: ignore[method-assign]
    sys.stdout = buf
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            code = cli.main(["ensure", "--cwd", str(root), "--timeout", "40"])
            payload = json.loads(buf.getvalue().strip().splitlines()[-1])
            check("ensure json ok", code == 0 and payload.get("ok") is True, json.dumps(payload))
            check("eligible git", payload.get("eligible") is True)
            buf.truncate(0)
            buf.seek(0)
            code2 = cli.main(["refresh", "--cwd", str(root), "--timeout", "20"])
            payload2 = json.loads(buf.getvalue().strip().splitlines()[-1])
            check("refresh json ok", code2 == 0 and payload2.get("ok") is True)
            check("refresh mode", payload2.get("mode") == "refresh")
            check("ui field present", "ui" in payload and "成功" in str(payload.get("ui")))
    finally:
        cli.run_cmd = orig_run  # type: ignore[method-assign]
        cli.which_tool = orig_which  # type: ignore[method-assign]
        sys.stdout = orig_out


def test_missing_cli_blocks() -> None:
    orig_which = cli.which_tool
    orig_out = sys.stdout
    buf = io.StringIO()
    cli.which_tool = lambda name: None  # type: ignore[method-assign]
    sys.stdout = buf
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            code = cli.main(["ensure", "--cwd", str(root), "--timeout", "10"])
            payload = json.loads(buf.getvalue().strip().splitlines()[-1])
            check("missing CLI blocked", code == 2 and payload.get("blocked") is True)
    finally:
        cli.which_tool = orig_which  # type: ignore[method-assign]
        sys.stdout = orig_out


def test_disabled_config() -> None:
    orig_out = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td, "cfg.json")
            cfg.write_text('{"enabled": false}', encoding="utf-8")
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            code = cli.main(["ensure", "--cwd", str(root), "--config", str(cfg)])
            payload = json.loads(buf.getvalue().strip().splitlines()[-1])
            check("disabled skips", code == 0 and payload.get("skipped") is True)
    finally:
        sys.stdout = orig_out


def test_plugin_once_markers() -> None:
    src = ROOT / "templates" / "editor-graph-hooks" / "graph-freshness.ts"
    text = src.read_text(encoding="utf-8")
    check("plugin cooldown const", "REFRESH_COOLDOWN_MS" in text)
    check("plugin rule latch", "ruleInjected" in text)
    check("plugin ensure latch", "ensured.has" in text)
    check("no session.updated ensure", "session.updated" not in text)
    check("plugin toast ui", "showToast" in text)
    vg = ROOT / "templates" / "editor-graph-hooks" / "verify-gate.ts"
    vg_text = vg.read_text(encoding="utf-8")
    check("verify-gate 影响范围", "影响范围" in vg_text)
    check("verify-gate r20_check mention", "r20_check.py" in vg_text)


def test_r20_check_portable() -> None:
    import r20_check as r20c  # noqa: E402

    ok_text = (
        "## 会话终验（R20）\n- 满足：落地\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持（证据：pytest）\n"
        "- 影响范围：已审查 CRG get_impact_radius\n结论：DONE"
    )
    ok, reason = r20c.replay_ok(ok_text)
    check("portable r20 pass", ok is True, reason)
    bad, _ = r20c.replay_ok("## 会话终验（R20）\n- 满足：x\n- 遗漏：无\n- 错改：无\n- 漏改：无文档影响\n- 原功能：保持（证据：x）\n结论：DONE")
    check("portable r20 missing 影响范围", bad is False)


def main() -> int:
    print("test_graph_freshness_cli")
    test_status_nongit()
    test_ensure_and_refresh_json()
    test_missing_cli_blocks()
    test_disabled_config()
    test_plugin_once_markers()
    test_r20_check_portable()
    print(f"passed checks, failed={FAILED}")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
