#!/usr/bin/env python3
"""beforeSubmitPrompt: 粘贴密钥检测。"""
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
from secret_patterns import find_secrets


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["secrets"]["scan_prompts"]:
            return

        prompt = extract_prompt(data)
        hits = find_secrets(prompt)
        if not hits:
            return

        msg = (
            "【Cursor Guard · 密钥警告】检测到疑似敏感信息: "
            + ", ".join(hits)
            + "。请移除后再发送。"
        )
        if cfg["secrets"]["block_on_match"]:
            write_json(
                {
                    "permission": "deny",
                    "user_message": msg,
                    "agent_message": msg,
                }
            )
        else:
            write_json({"agent_message": msg})
    except Exception as e:
        print(f"prompt_secret_scan: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
