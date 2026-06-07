#!/usr/bin/env python3
"""
PreToolUse Hook: read-before-edit 安全检查（源自 GSD）
在 Edit/Write/MultiEdit 前检查目标文件是否已在本会话中读取。
依赖 CLAUDE_SESSION_READ_FILES 环境变量（若不存在则跳过）。

exit 0 = 允许
exit 2 = 阻止（stderr 发送给 Claude）
"""
# source: open-gsd/gsd-core (原 gsd-build/get-shit-done 已归档)
import json
import sys
import io
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in ("Edit", "Write", "MultiEdit", "str_replace_editor"):
            sys.exit(0)

        session_files_raw = os.environ.get("CLAUDE_SESSION_READ_FILES", "")
        if not session_files_raw:
            sys.exit(0)

        try:
            session_files = json.loads(session_files_raw)
        except Exception:
            sys.exit(0)

        if tool_name == "MultiEdit":
            file_paths = [e.get("file_path", "") for e in tool_input.get("edits", [])]
        else:
            file_paths = [tool_input.get("file_path", tool_input.get("path", ""))]

        unread = [f for f in file_paths if f and f not in session_files]
        if not unread:
            sys.exit(0)

        msg = "[read-before-edit] 以下文件未在本会话中读取过：\n"
        for f in unread:
            msg += f"  - {f}\n"
        msg += "请先用 Read 工具读取后再编辑。\n"

        sys.stderr.write(msg)
        sys.stderr.flush()
        sys.exit(2)

    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
