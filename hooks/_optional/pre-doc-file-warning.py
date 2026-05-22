#!/usr/bin/env python3
"""
PreToolUse Hook: 文档文件警告
警告非标准文档文件的创建（exit 0，仅警告）
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

# 标准文档文件名
STANDARD_DOCS = {
    "README", "CHANGELOG", "LICENSE", "CONTRIBUTING",
    "AUTHORS", "HISTORY", "RELEASES", "INSTALL",
    "FAQ", "TROUBLESHOOTING", "UPGRADING",
}

# 标准文档扩展名
STANDARD_EXT = {".md", ".txt", ".rst", ".adoc"}


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 仅处理 Write 工具
        if tool_name != "Write":
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        basename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(basename)[0].upper()
        ext = os.path.splitext(basename)[1].lower()

        # 检查是否为文档文件
        if ext not in STANDARD_EXT:
            sys.exit(0)

        # 检查是否为标准文档名
        if name_without_ext in STANDARD_DOCS:
            sys.exit(0)

        # 检查是否在 docs/ 目录下
        parent_dir = os.path.basename(os.path.dirname(file_path))
        if parent_dir.lower() in ["docs", "doc", "documentation"]:
            sys.exit(0)

        # 触发警告
        warning = (
            f"📄 创建非标准文档文件：`{basename}`\n\n"
            f"建议使用标准文档命名：\n"
            f"- README.md - 项目主文档\n"
            f"- CHANGELOG.md - 变更日志\n"
            f"- CONTRIBUTING.md - 贡献指南\n"
            f"- docs/ 目录 - 详细文档\n\n"
            f"或考虑将此内容合并到现有文档中。"
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": warning,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
