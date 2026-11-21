#!/usr/bin/env python3
"""Smoke/regression tests for the kept hooks. Run: python hooks/tests/test_hooks.py"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1]


def run_hook(name: str, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_bash_guard() -> None:
    blocked = [
        "git stash",
        "git commit -m x",
        "git push origin main",
        "git push --force origin main",
        "git --no-pager commit -m x",
        "git -p commit",
        "git --no-optional-locks commit",
        "git --no-pager stash list",
        "git push origin main; echo --dry-run",
        "git.exe commit -m x",
        "`git commit -m x`",
        "X=$(git commit -m x)",
        "bash -c 'git commit -m x'",
        "(git commit -m x)",
        'sh -c "git stash"',
        'pwsh -Command "git commit -m x"',
        'g"it" commit -m x',
        'git comm"it" -m x',
        '$(g"it" commit -m x)',
        "sudo git commit -m x",
        "env FOO=bar git stash",
        "timeout 10 git commit -m x",
        "nice -n 5 git commit -m x",
        'powershell.exe -Command "git commit -m x"',
        '/bin/bash -c "git commit -m x"',
        "then git commit -m x",
        "do git commit -m x",
    ]
    for command in blocked:
        denied = run_hook("pre-bash-guard.py", {"tool_name": "Bash", "tool_input": {"command": command}})
        expect(denied.returncode == 2, f"{command} should be blocked, got {denied.returncode}")
    allowed = [
        "git status",
        "git log --oneline",
        "git push --dry-run origin main",
        "git.exe status",
        'echo "git commit"',
        'grep -r "git commit" .',
        "git log --grep commit",
        'echo "a; git commit"',
    ]
    for command in allowed:
        result = run_hook("pre-bash-guard.py", {"tool_name": "Bash", "tool_input": {"command": command}})
        expect(result.returncode == 0, f"{command} should pass, got {result.returncode}")


def test_git_quoted_options() -> None:
    # Reproduce real shell words, not malformed unquoted paths. Every payload
    # is inspected by the hook subprocess; none of these commands is executed.
    blocked = [
        "git --git-dir='C:/Project With Spaces/.git' push",
        r'git --git-dir "C:\Project With Spaces\.git" push',
        'git --work-tree="C:/Project With Spaces" commit -m fixture',
        r'git --work-tree "C:\Project With Spaces" stash',
        "git -C 'C:/Project With Spaces' commit -m fixture",
        r'git -C"C:\Project With Spaces" commit -m fixture',
        'git --git-dir="C:/Project With Spaces/.git" --work-tree="C:/Project With Spaces" push',
        '& "C:/Program Files/Git/bin/git.exe" -C "C:/Project With Spaces" commit -m fixture',
        "pwsh -Command 'git -C x commit -m fixture'",
        'echo "$(git commit)"',
    ]
    allowed = [
        "git --git-dir='C:/Project With Spaces/.git' status",
        r'git --work-tree="C:\Project With Spaces" diff',
        "git -C 'C:/Project With Spaces' log --oneline",
        "echo 'git commit'",
        'echo "git push"',
        'Write-Output "git --git-dir=fixture push"',
        "echo '$(git commit)'",
        'git config --get alias.commit',
        'git config --get-all alias.push',
        'git config get alias.stash',
        'rg "alias.commit" README.md',
        'printf "%s" "alias.commit"',
        'git config alias.history "log --oneline"',
        'git -c alias.history="log --oneline" history',
        'git config alias.note "log --grep=commit"',
    ]
    blocked.extend([
        "git -c alias.run='!git push' run",
        'git -c alias.c=commit c',
        'git -calias.s=stash s',
        'git config alias.c commit',
        'git config --global alias.run "!git push"',
        'git config set alias.s stash',
    ])
    for tool in ("Bash", "PowerShell", "Shell"):
        for command in blocked:
            result = run_hook("pre-bash-guard.py", {"tool_name":tool,"tool_input":{"command":command}})
            expect(result.returncode == 2, f"{tool} quoted Git mutation variant must be blocked: {command}")
        for command in allowed:
            result = run_hook("pre-bash-guard.py", {"tool_name":tool,"tool_input":{"command":command}})
            expect(result.returncode == 0, f"{tool} read-only/literal variant must pass: {command}")
    powershell_literal = run_hook("pre-bash-guard.py", {"tool_name":"PowerShell","tool_input":{"command":'Write-Output "`$(git commit)"'}})
    expect(powershell_literal.returncode == 0, "PowerShell escaped dollar signs must stay literal")
    bash_literal = run_hook("pre-bash-guard.py", {"tool_name":"Bash","tool_input":{"command":r'echo "\$(git commit)"'}})
    expect(bash_literal.returncode == 0, "Bash escaped dollar signs must stay literal")


def test_secret_detector() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "config.py"
        target.write_text(
            'API_KEY = "sk-ant-abcdefghijklmnopqrstuvwx"\n'
            'OTHER = "sk-ant-bbbbbbbbbbbbbbbbbbbbbbbb"\n',
            encoding="utf-8",
        )
        result = run_hook("post-secret-detector.py", {"tool_name": "Write", "tool_input": {"file_path": str(target)}})
        expect(result.returncode == 0, "secret detector must never block")
        expect("密钥" in result.stdout or "风险" in result.stdout, f"secret not reported: {result.stdout!r}")
        expect("sk-ant-abcdefghijklmnopqrstuvwx" not in result.stdout, "first secret must be redacted")
        expect("sk-ant-bbbbbbbbbbbbbbbbbbbbbbbb" not in result.stdout, "second secret must be redacted")

        clean = Path(tmp) / "clean.py"
        clean.write_text("VALUE = 1\n", encoding="utf-8")
        clean_result = run_hook("post-secret-detector.py", {"tool_name": "Write", "tool_input": {"file_path": str(clean)}})
        expect(clean_result.returncode == 0 and not clean_result.stdout.strip(), "clean file should stay silent")

        mcp_target = Path(tmp) / "mcp_config.py"
        mcp_target.write_text('TOKEN = "sk-ant-dddddddddddddddddddddddd"\n', encoding="utf-8")
        mcp_result = run_hook(
            "post-secret-detector.py",
            {
                "tool_name": "mcp__serena__replace_symbol_body",
                "tool_input": {"relative_path": str(mcp_target)},
                "cwd": tmp,
            },
        )
        expect(mcp_result.returncode == 0, "MCP secret detector must not block")
        expect("密钥" in mcp_result.stdout or "风险" in mcp_result.stdout, "MCP write should be scanned")

        env_target = Path(tmp) / ".env"
        env_target.write_text("DB_PASSWORD=supersecret123\n", encoding="utf-8")
        env_result = run_hook("post-secret-detector.py", {"tool_name": "Write", "tool_input": {"file_path": str(env_target)}})
        expect(env_result.returncode == 0, ".env scan must not block")
        expect("密钥" in env_result.stdout or "风险" in env_result.stdout, ".env should be scanned")

        env_local = Path(tmp) / ".env.local"
        env_local.write_text("API_TOKEN=abcdefghijklmnop\n", encoding="utf-8")
        env_local_result = run_hook(
            "post-secret-detector.py",
            {"tool_name": "Write", "tool_input": {"file_path": str(env_local)}},
        )
        expect(env_local_result.returncode == 0, ".env.local scan must not block")
        expect("密钥" in env_local_result.stdout or "风险" in env_local_result.stdout, ".env.local should be scanned")

        env_meta = Path(tmp) / ".env.meta"
        env_meta.write_text("API_KEY_HEADER=X-Api-Key\nTOKEN_EXPIRY=86400000\n", encoding="utf-8")
        env_meta_result = run_hook(
            "post-secret-detector.py",
            {"tool_name": "Write", "tool_input": {"file_path": str(env_meta)}},
        )
        expect(env_meta_result.returncode == 0, ".env.meta scan must not block")
        expect("风险" not in env_meta_result.stdout, "metadata keys must not be reported")

        env_export = Path(tmp) / ".env.export"
        env_export.write_text("export DB_PASSWORD=supersecret123\n", encoding="utf-8")
        env_export_result = run_hook(
            "post-secret-detector.py",
            {"tool_name": "Write", "tool_input": {"file_path": str(env_export)}},
        )
        expect(env_export_result.returncode == 0, ".env.export scan must not block")
        expect("密钥" in env_export_result.stdout or "风险" in env_export_result.stdout, "export KEY=VALUE should be scanned")

        test_file = Path(tmp) / "test_config.py"
        test_file.write_text('TOKEN = "sk-ant-ffffffffffffffffffffffff"\n', encoding="utf-8")
        test_result = run_hook("post-secret-detector.py", {"tool_name": "Write", "tool_input": {"file_path": str(test_file)}})
        expect(test_result.returncode == 0 and not test_result.stdout.strip(), "test files should stay silent")

        # Only fixed risk metadata may leave the hook, including when an adjacent
        # short secret does not match any pattern. All values below are synthetic.
        production = Path(tmp) / "private-production-name.py"
        aws = "AKIA" + "A" * 16
        adjacent = "Z7!bQ9?"
        production.write_text(f'AWS="{aws}"; password="{adjacent}"\n', encoding="utf-8")
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(production)}}
        warning = run_hook("post-secret-detector.py", payload)
        expect(warning.returncode == 0 and "AWS Access Key ID" in warning.stdout, "recognized risk must remain visible")
        for value in (aws, adjacent, "AKIA***", str(production), production.name, 'AWS='):
            expect(value not in warning.stdout + warning.stderr, "output must contain no source line, partial token or path")
        expect("编辑文件1，行1" in warning.stdout, "risk must identify ordinal and line")

        synthetic = "a7B9m3N8q2R6t4U5w1V0k9L8"
        for field in ("api_key", "password", "client_secret", "access_token", "jwt_secret"):
            for prefix in ("", "description='sample'\n", "# TODO: configure env later\n", "mode = 'process.env.SETTING'\n"):
                production.write_text(prefix + json.dumps({field: synthetic}) + "\n", encoding="utf-8")
                warning = run_hook("post-secret-detector.py", payload)
                expect(warning.returncode == 0 and "风险" in warning.stdout, "JSON quoted fields must survive unrelated safe-looking context")
                expect(synthetic not in warning.stdout + warning.stderr, "JSON values must never be printed")
        for content in (
            'API_KEY_HEADER="X-Api-Key-Header"\nTOKEN_EXPIRY=86400000\n',
            json.dumps({"API_KEY_HEADER": synthetic, "TOKEN_EXPIRY": "86400000"}),
            'api_key="your_api_key_here"\npassword="CHANGEME"\n',
            'API_KEY=${PROJECT_API_KEY}\nAPI_TOKEN=process.env.PROJECT_API_TOKEN\n',
            'API_KEY=os.getenv("PROJECT_API_KEY")\n',
        ):
            production.write_text(content, encoding="utf-8")
            quiet = run_hook("post-secret-detector.py", payload)
            expect(quiet.returncode == 0 and not (quiet.stdout + quiet.stderr).strip(), "metadata, explicit placeholders and environment references should remain quiet")

        # A missing/unreadable candidate is visible and does not skip later files.
        unreadable = Path(tmp) / "unreadable-private-name.py"
        unreadable.mkdir()
        production.write_text(f'KEY="{aws}"\n', encoding="utf-8")
        partial = run_hook("post-secret-detector.py", {"tool_name": "Write", "tool_input": {"paths": [str(unreadable), str(production)]}})
        expect(partial.returncode == 0 and "检查未完成" in partial.stderr and "AWS Access Key ID" in partial.stdout, "read failure must warn and continue scanning remaining files")
        expect(unreadable.name not in partial.stderr and str(unreadable) not in partial.stderr, "read failure must hide paths")
        for invalid in ('{"secret-input-sentinel":', '["secret-input-sentinel"]', '"secret-input-sentinel"'):
            failed = subprocess.run([sys.executable, str(HOOKS / "post-secret-detector.py")], input=invalid, capture_output=True, text=True, encoding="utf-8", timeout=10)
            expect(failed.returncode == 0 and "检查未完成" in failed.stderr, "malformed/non-object input must produce a visible nonblocking warning")
            expect("secret-input-sentinel" not in failed.stdout + failed.stderr, "invalid input must never be echoed")
        unrelated = run_hook("post-secret-detector.py", {"tool_name": "Read", "tool_input": {"file_path": str(production)}})
        expect(unrelated.returncode == 0 and not (unrelated.stdout + unrelated.stderr).strip(), "unrelated tools must remain quiet")


def test_encoding_guard() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "broken.py"
        target.write_text("value = '\ufffd'\n", encoding="utf-8")
        snapshot = run_hook("pre-encoding-snapshot.py", {"tool_name": "Edit", "tool_input": {"file_path": str(target)}})
        expect(snapshot.returncode == 0, "snapshot must not block")
        check = run_hook("post-encoding-check.py", {"tool_name": "Edit", "tool_input": {"file_path": str(target)}})
        expect(check.returncode == 0, "encoding check must not block")
        expect(bool(check.stdout.strip()), "replacement character should be reported")


def test_native_hook_registration() -> None:
    root = HOOKS.parent
    for filename in ("settings.json", "settings.example.json"):
        data = json.loads((root / filename).read_text(encoding="utf-8"))
        expect(set(data["hooks"]) == {"PreToolUse", "PostToolUse"}, "automatic session/stop hooks must be absent")
        records = [(event, group.get("matcher", ""), hook) for event, groups in data["hooks"].items() for group in groups for hook in group["hooks"]]
        expect(not any("post-edit-format" in h["command"] for _, _, h in records), "formatter must not activate globally")
        for tool in ("Bash", "PowerShell"):
            import re
            expect(any(event == "PreToolUse" and re.fullmatch(matcher, tool) and "pre-bash-guard" in h["command"] for event, matcher, h in records), f"missing safety hook for {tool}")
        expect(all(1 <= h["timeout"] <= 30 for _, _, h in records), "timeouts must be seconds")
    result = run_hook("pre-bash-guard.py", {"tool_name": "PowerShell", "tool_input": {"command": "git commit -m sample"}})
    expect(result.returncode == 2, "PowerShell Git mutation must be blocked")
    for command in (r'Remove-Item -LiteralPath C:\ -Recurse -Force', r'Remove-Item -Recurse -LiteralPath $HOME', r'git -C "C:/project with spaces" commit -m fixture'):
        denied = run_hook("pre-bash-guard.py", {"tool_name":"PowerShell", "tool_input":{"command":command}})
        expect(denied.returncode == 2, "root deletion / Git mutation variants must be blocked")
    safe = run_hook("pre-bash-guard.py", {"tool_name": "PowerShell", "tool_input": {"command": "git status"}})
    expect(safe.returncode == 0, "PowerShell read-only Git must pass")
    data = run_hook("pre-bash-guard.py", {"tool_name": "Bash", "tool_input": {"command": "git commit -m secret-value-that-must-not-be-echoed"}})
    expect("secret-value-that-must-not-be-echoed" not in data.stderr, "guard must not echo potentially sensitive command arguments")
    malformed = run_hook("pre-bash-guard.py", {"tool_name":"Bash", "tool_input":"malformed-private-payload"})
    expect(malformed.returncode == 1 and bool(malformed.stderr), "malformed hook data must report a visible non-blocking error")
    expect("malformed-private-payload" not in malformed.stderr, "error reports must not echo arbitrary payloads")


def test_encoding_parallel_sessions() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        targets = [Path(tmp) / f"parallel-{i}.txt" for i in range(8)]
        payloads = []
        for i, target in enumerate(targets):
            target.write_bytes(b"before\r\n")
            payloads.append({"session_id":f"parallel-{i}","tool_use_id":f"edit-{i}","tool_name":"Edit","tool_input":{"file_path":str(target)}})
        with ThreadPoolExecutor(max_workers=8) as pool:
            before = list(pool.map(lambda data: run_hook("pre-encoding-snapshot.py", data), payloads))
        expect(all(p.returncode == 0 for p in before), "parallel pre hooks must run")
        for target in targets:target.write_bytes(b"after\n")
        with ThreadPoolExecutor(max_workers=8) as pool:
            after = list(pool.map(lambda data: run_hook("post-encoding-check.py", data), payloads))
        expect(all("EOL" in p.stdout for p in after), "each independent session must retain its own pre-edit signature")
        expect(all(p.returncode == 0 for p in after), "encoding warnings must not block")
        repeat = run_hook("post-encoding-check.py", payloads[0])
        expect(not repeat.stdout.strip(), "consumed snapshots must not affect a later edit")


def test_encoding_same_file_isolation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "shared.txt"
        first = {"session_id":"one","tool_use_id":"first","tool_name":"Edit","tool_input":{"file_path":str(target)}}
        second = {**first, "session_id":"two", "tool_use_id":"second"}
        target.write_bytes(b"before\r\n")
        run_hook("pre-encoding-snapshot.py", first)
        target.write_bytes(b"middle\n")
        run_hook("pre-encoding-snapshot.py", second)
        warning = run_hook("post-encoding-check.py", first)
        clean = run_hook("post-encoding-check.py", second)
        expect("EOL" in warning.stdout, "one session must not consume another's snapshot")
        expect(not clean.stdout.strip(), "the second session must compare against its own LF signature")
        first["session_id"] = second["session_id"] = "same-session"
        target.write_bytes(b"again\r\n")
        run_hook("pre-encoding-snapshot.py", first)
        target.write_bytes(b"again\n")
        run_hook("pre-encoding-snapshot.py", second)
        expect("EOL" in run_hook("post-encoding-check.py", first).stdout, "tool_use_id must isolate overlapping edits in one session")
        expect(not run_hook("post-encoding-check.py", second).stdout.strip(), "second invocation must retain its own snapshot")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_formatter_project_opt_in_and_failure() -> None:
    module = load_module("project_formatter", HOOKS / "post-edit-format.py")
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        target = project / "sample.py"
        target.write_text("value=1\n", encoding="utf-8")
        config = project / "pyproject.toml"
        config.write_text('[project]\nname = "fixture"\n', encoding="utf-8")
        with patch.object(module.shutil, "which", return_value="installed-globally"):
            expect(module.formatter(target, project) is None, "global formatter must not activate without project configuration")
        config.write_text("[tool.ruff]\nline-length = 88\n", encoding="utf-8")
        with patch.object(module.shutil, "which", return_value=sys.executable):
            command = module.formatter(target, project)
        expect(command is not None and command[1] == "format", "project Ruff configuration must opt in")
        marker = project / "formatter-ran.txt"
        import io
        from contextlib import redirect_stderr
        errors = io.StringIO()
        with redirect_stderr(errors):
            failed = module.run([sys.executable, "-c", "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran'); print('private-source-fragment',file=sys.stderr); sys.exit(7)", str(marker)], project)
        expect(marker.read_text() == "ran", "formatter subprocess must actually execute")
        expect(not failed and "exit=7" in errors.getvalue(), "failed formatter must report actual exit status")
        expect("private-source-fragment" not in errors.getvalue(), "formatter diagnostics must not echo arbitrary sensitive source")
        expect(module.run([sys.executable, "-c", "pass"], project), "successful formatter process must be recognized")


def test_checker_rejects_broken_contracts() -> None:
    checker = load_module("config_checker", HOOKS.parent / "scripts/check-config.py")
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp)
        for folder in ("skills","agents","commands","templates","snippets","hooks","mcp-configs","tools"):
            source = HOOKS.parent / folder
            if source.exists():shutil.copytree(source, fixture / folder, ignore=shutil.ignore_patterns("*.private.json", "__pycache__"))
        for filename in ("CLAUDE.md","README.md","package.json","settings.example.json",".mcp.json"):
            shutil.copy2(HOOKS.parent / filename, fixture / filename)
        # Paths in the example are deliberately placeholders, so only the example is checked.
        before, _ = checker.check(fixture)
        expect(not before, f"valid fixture failed contract checks: {before}")
        sample = next((fixture / "skills").glob("*/SKILL.md"))
        original_sample = sample.read_text(encoding="utf-8")
        with sample.open("a", encoding="utf-8") as stream:stream.write("\nRead `skills/missing-skill/SKILL.md` before use.\n")
        errors, _ = checker.check(fixture)
        expect(any("broken local reference" in e for e in errors), "checker must reject a broken internal reference")
        sample.write_text(original_sample + "\nRun `tools/missing-tool.py` before use.\n", encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("broken local reference" in e and "tools/missing-tool.py" in e for e in errors), "checker must reject a broken tools reference")
        sample.write_text(original_sample + "\n内部核对七维。\n", encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("retired reference" in e and "七维" in e for e in errors), "checker must reject retired dual-track wording")
        sample.write_text(original_sample, encoding="utf-8")
        (fixture / "AGENTS.md").write_text("# Duplicate entry\n", encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("AGENTS.md" in e for e in errors), "checker must reject a global AGENTS.md entry")
        (fixture / "AGENTS.md").unlink()
        original_claude = (fixture / "CLAUDE.md").read_text(encoding="utf-8")
        (fixture / "CLAUDE.md").write_text("@AGENTS.md\n" + original_claude, encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("@AGENTS.md" in e for e in errors), "checker must reject @AGENTS.md import in CLAUDE.md")
        (fixture / "CLAUDE.md").write_text(original_claude, encoding="utf-8")
        original_pkg = (fixture / "package.json").read_text(encoding="utf-8")
        (fixture / "package.json").write_text(json.dumps({"name":"claude-config","version":"0.0.1"}), encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("version mismatch" in e for e in errors), "checker must reject version mismatch between package.json and README.md")
        (fixture / "package.json").write_text(original_pkg, encoding="utf-8")
        cat_sample = fixture / "catalog" / "skills" / "sample" / "SKILL.md"
        cat_sample.parent.mkdir(parents=True, exist_ok=True)
        cat_sample.write_text("# Sample\n参见 `RULES_SECURITY.md`，via claude-mem，路径 `~/.codex/skills`。\n", encoding="utf-8")
        (fixture / "catalog" / "INDEX.md").write_text("# 索引\n## 技能（1）\n- [sample](skills/sample/SKILL.md)：一键部署，发布到生产\n## 角色（0）\n## 规则（0）\n", encoding="utf-8")
        (fixture / "catalog" / "agents").mkdir(parents=True, exist_ok=True)
        (fixture / "catalog" / "rules").mkdir(parents=True, exist_ok=True)
        errors, _ = checker.check(fixture)
        expect(any("retired reference" in e and "RULES_SECURITY.md" in e for e in errors), "checker must reject retired refs in catalog")
        expect(any("retired reference" in e and ("一键部署" in e or "发布到生产" in e) for e in errors), "checker must reject stale index phrases in catalog/INDEX.md")
        expect(any("executor/tool binding" in e and "claude-mem" in e for e in errors), "checker must reject executor tool bindings in catalog")
        expect(any("cross-tool runtime dependency" in e for e in errors), "checker must reject cross-tool paths in catalog")
        shutil.rmtree(fixture / "catalog")
        data = json.loads((fixture / "settings.example.json").read_text(encoding="utf-8"))
        data["hooks"]["PreToolUse"][0]["hooks"][0]["timeout"] = 5000
        (fixture / "settings.example.json").write_text(json.dumps(data), encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("invalid hook config" in e for e in errors), "checker must reject millisecond-sized timeout values")
        public = fixture / "mcp-configs/credential-fixture.json"
        public.write_text(json.dumps({"mcpServers":{"fixture":{"command":"fixture-command","env":{"API_KEY":"literal-credential-that-must-stay-private"}}}}), encoding="utf-8")
        errors, _ = checker.check(fixture)
        expect(any("credential environment value" in e for e in errors), "checker must reject literal credentials in public optional definitions")
        expect(not any("literal-credential-that-must-stay-private" in e for e in errors), "checker errors must not leak rejected values")


def test_error_redaction() -> None:
    guard = load_module("encoding_guard", HOOKS / "_lib/encoding_guard.py")
    import io
    from contextlib import redirect_stderr
    with tempfile.TemporaryDirectory() as tmp:
        unreadable = Path(tmp) / "private-secret-path-sentinel.py"
        unreadable.mkdir()
        err = io.StringIO()
        with redirect_stderr(err):
            snap = guard.snapshot_signature(str(unreadable))
            issues, data = guard.analyze_file(str(unreadable))
        expect(snap is None and issues == [] and data == b"", "unreadable file must fail safely")
        err_text = err.getvalue()
        expect("encoding_guard:" in err_text, "encoding_guard errors must remain visible on stderr")
        expect("private-secret-path-sentinel" not in err_text and str(tmp) not in err_text, "encoding_guard stderr must redact file paths")

        for hook_name in ("pre-encoding-snapshot.py", "post-encoding-check.py"):
            res = subprocess.run(
                [sys.executable, str(HOOKS / hook_name)],
                input="{malformed-private-payload-sentinel",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            expect(res.returncode == 0 and bool(res.stderr.strip()), f"{hook_name} must warn non-blockingly on malformed input")
            expect("malformed-private-payload-sentinel" not in res.stdout + res.stderr, f"{hook_name} must not echo malformed payload")
            dir_res = run_hook(hook_name, {"tool_name": "Edit", "tool_input": {"file_path": str(unreadable)}})
            expect(dir_res.returncode == 0, f"{hook_name} must not block on unreadable target")
            expect("private-secret-path-sentinel" not in dir_res.stdout + dir_res.stderr, f"{hook_name} must not leak unreadable path")


def main() -> int:
    tests = [
        test_bash_guard,
        test_git_quoted_options,
        test_secret_detector,
        test_encoding_guard,
        test_native_hook_registration,
        test_encoding_parallel_sessions,
        test_encoding_same_file_isolation,
        test_formatter_project_opt_in_and_failure,
        test_checker_rejects_broken_contracts,
        test_error_redaction,
    ]
    # Keep every hook cache isolated from the user runtime.
    test_state = tempfile.TemporaryDirectory()
    previous_state = os.environ.get("CLAUDE_HOOK_STATE_DIR")
    os.environ["CLAUDE_HOOK_STATE_DIR"] = test_state.name
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:  # noqa: BLE001 - test runner reports all failures
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    if previous_state is None:os.environ.pop("CLAUDE_HOOK_STATE_DIR", None)
    else:os.environ["CLAUDE_HOOK_STATE_DIR"] = previous_state
    test_state.cleanup()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
