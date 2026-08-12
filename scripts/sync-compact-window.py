#!/usr/bin/env python3
"""按当前模型同步 settings.json autoCompactWindow（不超出模型最大上下文）。

命令：
    python scripts/sync-compact-window.py             # 计算并写入 settings.json
    python scripts/sync-compact-window.py --dry-run   # 只打印结果，不写盘

模型上下文表在 config/model-context-windows.json；新模型未登记会走后缀兜底，
出现 validate_config 的 V17 告警时先补该表再跑本脚本。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (OSError, ValueError):
        pass

HOOKS_LIB = Path(__file__).resolve().parent.parent / "hooks" / "_lib"
sys.path.insert(0, str(HOOKS_LIB))

from context_thresholds import (  # noqa: E402
    active_model_name,
    recommended_autocompact_window,
    resolve_model_context_tokens,
    sync_settings_compact_window,
)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    result = sync_settings_compact_window(write=not dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    model = result["model"] or active_model_name()
    print(
        f"model={model!r} max_context={resolve_model_context_tokens(model)} "
        f"autoCompactWindow→{result['resolved_window']}"
    )
    if dry_run and result["updated"]:
        print("(dry-run: 未写入 settings.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
