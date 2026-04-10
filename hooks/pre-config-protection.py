#!/usr/bin/env python3
"""
PreToolUse Hook: 配置文件保护
阻止修改 linter/formatter 配置文件，引导修复代码而非削弱配置

exit 0 = 允许
exit 2 = 阻止（stderr 内容会发送给 Claude）
"""
import json
import sys
import io
import os
import re

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# 受保护的配置文件
PROTECTED_CONFIGS = [
    # ESLint
    r"\.eslintrc(?:\.(json|js|yaml|yml))?$",
    r"eslint\.config\.(js|ts|mjs|cjs)$",
    # Prettier
    r"\.prettierrc(?:\.(json|js|yaml|yml|toml))?$",
    r"prettier\.config\.(js|ts|mjs|cjs)$",
    # TypeScript
    r"tsconfig(?:\.base)?\.json$",
    # Python
    r"\.flake8$",
    r"\.pylintrc$",
    r"pyproject\.toml$",
    r"setup\.cfg$",
    r"tox\.ini$",
    # Go
    r"\.golangci\.lint\.yaml$",
    r"\golangci\.yml$",
    # Rust
    r"\.clippy\.toml$",
    # General
    r"\editorconfig$",
]


def is_protected_config(file_path: str) -> tuple[bool, str]:
    """检查是否为受保护的配置文件"""
    basename = os.path.basename(file_path)
    
    for pattern in PROTECTED_CONFIGS:
        if re.match(pattern, basename, re.IGNORECASE):
            return True, pattern
    
    return False, ""


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

        # 处理 Write/Edit/MultiEdit
        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        if tool_name == "MultiEdit":
            file_paths = [e.get("file_path", "") for e in tool_input.get("edits", [])]
        else:
            file_paths = [tool_input.get("file_path", "")]

        protected_files = []
        for file_path in file_paths:
            if not file_path:
                continue
            is_protected, pattern = is_protected_config(file_path)
            if is_protected:
                protected_files.append((file_path, pattern))

        if not protected_files:
            sys.exit(0)

        # 构建阻止消息
        error_msg = "🛡️ 配置文件保护：阻止修改以下配置文件\n\n"
        for file_path, pattern in protected_files:
            error_msg += f"- `{os.path.basename(file_path)}` (匹配: {pattern})\n"
        
        error_msg += "\n**原因：** 修改 linter/formatter 配置可能导致代码质量标准降低。\n\n"
        error_msg += "**建议做法：**\n"
        error_msg += "1. 修复代码以符合现有配置标准\n"
        error_msg += "2. 如确需调整配置，先在团队中讨论并获得同意\n"
        error_msg += "3. 使用 `--no-verify` 跳过此检查（不推荐）\n\n"
        error_msg += "请修复代码问题而非削弱配置。"

        sys.stderr.write(error_msg + "\n")
        sys.stderr.flush()
        sys.exit(2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
