#!/usr/bin/env python3
"""
PostToolUse Hook: Record Edited JS/TS File Paths
记录编辑过的 JavaScript/TypeScript 文件路径，用于 Stop 事件时批量格式化和类型检查

exit 0 = 正常结束
"""
import json
import sys
import io
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# JS/TS 编辑记录文件
JS_EDITS_FILE = os.path.expanduser("~/.claude/js-edits-session.json")


def record_js_edit(file_path):
    """记录 JS/TS 文件编辑"""
    try:
        os.makedirs(os.path.dirname(JS_EDITS_FILE), exist_ok=True)
        
        # 加载现有记录
        edits = []
        if os.path.exists(JS_EDITS_FILE):
            try:
                with open(JS_EDITS_FILE, "r", encoding="utf-8") as f:
                    edits = json.load(f)
            except Exception:
                pass
        
        # 添加新记录（去重）
        if file_path not in edits:
            edits.append(file_path)
        
        # 保存记录
        with open(JS_EDITS_FILE, "w", encoding="utf-8") as f:
            json.dump(edits, f, indent=2)
    except Exception:
        pass


def is_js_ts_file(file_path):
    """判断是否为 JS/TS 文件"""
    js_ts_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
    return os.path.splitext(file_path)[1].lower() in js_ts_extensions


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        # 检查编辑类工具
        if tool_name in ["Edit", "Write", "MultiEdit"]:
            file_path = tool_input.get("file_path", "")
            if file_path and is_js_ts_file(file_path):
                record_js_edit(file_path)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
