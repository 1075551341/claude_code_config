#!/usr/bin/env python3
"""初次修改验收门：每个文件首次成功编辑后注入一次（v11.3.4）。

状态写入 verification-gate.json 的 first_edit_nudged，避免第三套 state。
"""
from __future__ import annotations

from pathlib import Path

MAX_TRACKED = 200


def load_first_edit_message(claude_home: str | Path | None = None) -> str:
    from gate_reader import load_gate

    return load_gate("first_edit", claude_home)


def fresh_edit_paths(entry: dict, paths: list[str]) -> list[str]:
    """返回尚未注入过初次验收的路径，并记入 entry['first_edit_nudged']。"""
    nudged = entry.setdefault("first_edit_nudged", [])
    fresh = [p for p in paths if p and p not in nudged]
    if not fresh:
        return []
    nudged.extend(fresh)
    del nudged[:-MAX_TRACKED]
    return fresh


def compose_message(base: str, fresh: list[str]) -> str:
    names = ", ".join(Path(p).name for p in fresh[:8])
    more = f" 等 {len(fresh)} 个" if len(fresh) > 8 else ""
    return (
        f"{base}\n\n（首次编辑后验收触发文件：{names}{more} — "
        "须覆盖该文件 + blast-radius 全部相关项，禁止只勾当前文件、勿沿用上一文件结论）"
    )
