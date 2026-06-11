#!/usr/bin/env python3
"""beforeSubmitPrompt: 压缩=放行(同/summarize)；提取=结构化摘要制品。"""
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
from session_handoff import extract_session_id, set_compress_pending

DEFAULT_COMPRESS_KEYWORDS = [
    "压缩上下文",
    "压缩 上下文",
    "compact context",
    "compact 上下文",
]

DEFAULT_EXTRACT_KEYWORDS = [
    "提取上下文",
    "提取 上下文",
    "extract context",
    "extract 上下文",
]

# Cursor 原生命令 — Guard 不拦截
NATIVE_PASS = {"/summarize", "/compress", "summarize", "compress"}


def _matches_any(text: str, keywords: list[str]) -> bool:
    tl = text.lower()
    return any(k in tl for k in keywords)


def main() -> None:
    try:
        data = read_stdin()
        prompt = extract_prompt(data).strip()
        pl = prompt.lower()

        if pl in NATIVE_PASS or pl.startswith("/summarize") or pl.startswith("/compress"):
            return

        cfg = load_guard_config()
        comp = cfg.get("compression", {})
        compress_kws = [
            k.lower()
            for k in comp.get("compress_prompt_keywords", DEFAULT_COMPRESS_KEYWORDS)
        ]
        extract_kws = [
            k.lower()
            for k in comp.get("extract_prompt_keywords", DEFAULT_EXTRACT_KEYWORDS)
        ]

        # 「压缩上下文」与 /summarize 等效 — Guard 不拦截，由 Cursor 原生压缩处理
        if _matches_any(pl, compress_kws):
            return

        if not _matches_any(pl, extract_kws):
            return

        session_id = extract_session_id(data)
        set_compress_pending(session_id, prompt)

        write_json(
            {
                "continue": True,
                "user_message": (
                    "【Cursor Guard · 提取上下文已启动】\n"
                    "本回合 Agent 将输出结构化会话摘要（已完成/进行中/待定/路径），"
                    "并写入 ~/.cursor/.state/session-digest.md。\n"
                    "此操作不压缩上下文环；需要压缩请发送 /summarize 或「压缩上下文」。"
                ),
            }
        )
    except Exception as e:
        print(f"compress_on_prompt: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
