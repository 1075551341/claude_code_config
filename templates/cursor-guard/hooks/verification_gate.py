#!/usr/bin/env python3
"""beforeSubmitPrompt: 完成验证门（v10.7.0）。
prompt 命中完成类关键词时注入 verification-before-completion 强制指令。
幂等无状态；永不阻断。"""
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
from gate_messages import load_gate

DEFAULT_KEYWORDS = ["完成", "修好", "测试通过", "done", "搞定", "fixed"]


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["verification"]["enabled"]:
            return
        keywords = [k.lower() for k in cfg["verification"]["prompt_keywords"]]
        prompt = extract_prompt(data).lower()
        if not prompt or not any(k in prompt for k in keywords):
            return
        write_json(
            {"additional_context": load_gate("verify", cfg["sync"]["claude_home"])}
        )
    except Exception as e:
        print(f"verification_gate: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
