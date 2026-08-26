#!/usr/bin/env python3
"""验证门多端薄入口（v11.4）— 供 opencode 插件经子进程复用本仓校验 SSOT。

设计约束（防实现漂移）：所有判定逻辑仍唯一居于 hooks/_lib/*.py；本文件只做
CLI 参数解析与状态读写转发，禁止在此新增任何校验规则。
状态文件与 Claude Code/Cursor 同源：~/.claude/.state/verification-gate.json。

子命令：
  capture-req  --session S (--prompt TEXT | --prompt-file -)
  track-edit   --session S --paths p1,p2[,...]
  track-cmd    --session S --command "..."
  check-idle   --session S            -> {"unverified":bool,"edited":n}
  check-r20    (stdin 正文)           -> {"ok":bool}

由 ~/<config>/opencode/plugins/verify-gate.ts 经 Bun.spawn 调用；Cursor 端走
import_claude_lib 直载同源模块，三端共享同一份 replay_ok/coverage 判定。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _entry(state: dict, session_id: str) -> dict:
    return state.setdefault(session_id, {})


def cmd_capture_req(args) -> int:
    from req_fingerprint import save_requirements

    prompt = args.prompt
    if prompt is None and args.prompt_file == "-":
        prompt = sys.stdin.read()
    elif prompt is None:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read()
    save_requirements(args.session, prompt or "")
    print(json.dumps({"ok": True}, ensure_ascii=False))
    return 0


def cmd_track_edit(args) -> int:
    from req_fingerprint import load_gate_state, save_gate_state

    state = load_gate_state()
    now = time.time()
    entry = _entry(state, args.session)
    entry.setdefault("started_ts", now)
    entry["ts"] = now
    edited = entry.setdefault("edited_files", [])
    for p in [x.strip() for x in args.paths.split(",") if x.strip()]:
        edited.append({"path": p, "ts": now})
    # opencode 端不参与 impact_manifest_gate（platforms 仅 claude-code/cursor），不记 git_baseline
    del edited[:-400]
    save_gate_state(state)
    print(json.dumps({"ok": True, "tracked": len(edited)}, ensure_ascii=False))
    return 0


def cmd_track_cmd(args) -> int:
    from r20_replay import has_unverified_edits  # noqa: F401  仅确保依赖可载
    from req_fingerprint import load_gate_state, save_gate_state

    state = load_gate_state()
    now = time.time()
    entry = _entry(state, args.session)
    entry["ts"] = now
    cmds = entry.setdefault("verify_commands", [])
    cmds.append({"command": (args.command or "")[:300], "ts": now})
    del cmds[:-200]
    save_gate_state(state)
    print(json.dumps({"ok": True}, ensure_ascii=False))
    return 0


def cmd_check_idle(args) -> int:
    from r20_replay import has_unverified_edits
    from req_fingerprint import load_gate_state

    state = load_gate_state()
    entry = state.get(args.session) or {}
    print(
        json.dumps(
            {"unverified": bool(has_unverified_edits(entry)), "edited": len(entry.get("edited_files") or [])},
            ensure_ascii=False,
        )
    )
    return 0


def cmd_check_rml(args) -> int:
    from r20_replay import replay_ok

    text = sys.stdin.read()
    print(json.dumps({"ok": bool(replay_ok(text))}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="gate_cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("capture-req")
    p.add_argument("--session", required=True)
    p.add_argument("--prompt")
    p.add_argument("--prompt-file")
    p.set_defaults(func=cmd_capture_req)

    p = sub.add_parser("track-edit")
    p.add_argument("--session", required=True)
    p.add_argument("--paths", required=True)
    p.set_defaults(func=cmd_track_edit)

    p = sub.add_parser("track-cmd")
    p.add_argument("--session", required=True)
    p.add_argument("--command", required=True)
    p.set_defaults(func=cmd_track_cmd)

    p = sub.add_parser("check-idle")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_check_idle)

    p = sub.add_parser("check-r20")
    p.set_defaults(func=cmd_check_rml)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:  # noqa: BLE001 — 门工具失败只降级打印（R16 显式暴露）
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
