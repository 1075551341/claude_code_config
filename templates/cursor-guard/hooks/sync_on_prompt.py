#!/usr/bin/env python3
"""beforeSubmitPrompt: /sync、同步配置 等关键词触发显式同步。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_prompt,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from impact_sync import rules_out_of_sync
from maintenance_check import index_drift_report
from sync_runner import run_full_sync


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        prompt = extract_prompt(data).lower()
        keywords = [k.lower() for k in cfg["sync"]["prompt_keywords"]]
        if not any(k in prompt for k in keywords):
            return

        claude_home = cfg["sync"]["claude_home"]
        ok, msg = run_full_sync(force=True)
        stale, stale_msg = rules_out_of_sync(claude_home)
        drift = index_drift_report(claude_home)

        parts = [msg]
        parts.append(stale_msg if stale else f"rules 检测: {stale_msg}")
        if drift:
            parts.append("INDEX 粗检:")
            parts.extend(f"  - {d}" for d in drift)
        else:
            parts.append("INDEX 粗检: 未发现明显过期")

        body = "【Cursor Guard · 显式同步】\n" + "\n".join(f"  • {p}" for p in parts)
        if ok:
            write_json({"additional_context": body})
        else:
            print(body, file=sys.stderr)
    except Exception as e:
        print(f"sync_on_prompt: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
