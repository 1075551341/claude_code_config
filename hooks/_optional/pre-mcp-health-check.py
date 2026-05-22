#!/usr/bin/env python3
"""
PreToolUse Hook: MCP Health Check
在调用 MCP 工具前检查 MCP 服务器健康状态

exit 0 = 允许执行
exit 2 = 阻止执行（MCP 不健康时）
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


def is_mcp_tool(tool_name: str) -> bool:
    """检测是否为 MCP 工具调用"""
    return tool_name.startswith("mcp") or tool_name.startswith("mcp_")


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name = data.get("tool_name", "")

        # 仅检查 MCP 工具
        if not is_mcp_tool(tool_name):
            sys.exit(0)

        # 检查 MCP 配置文件是否存在
        mcp_config_path = os.path.expanduser("~/.claude/.mcp.json")
        if not os.path.exists(mcp_config_path):
            # 无 MCP 配置，无需检查
            sys.exit(0)

        # 这里可以添加更复杂的健康检查逻辑
        # 例如：尝试连接 MCP 服务器、检查进程状态等
        # 目前简化处理：仅检查配置文件存在性

        sys.exit(0)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
