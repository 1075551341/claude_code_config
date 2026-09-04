#!/usr/bin/env python3
"""
PostToolUse Hook: 密钥泄露检测器
文件写入后扫描是否包含硬编码的密钥、Token、密码

模式表 SSOT → hooks/_lib/secret_patterns.py（v12 与 Cursor Guard 共用）
"""
# source: shanraisshan/claude-code-best-practice
import json
import sys
import io
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))
from secret_patterns import (  # noqa: E402
    SAFE_FILE_PATTERNS,
    SECRET_PATTERNS,
    is_safe_context,
)

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)


def scan_file(file_path: str) -> list[dict]:
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return issues

    lines = content.splitlines()

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--", "/*")) or not stripped:
            continue

        ctx_start = max(0, line_num - 3)
        ctx_end   = min(len(lines), line_num + 2)
        surrounding = "\n".join(lines[ctx_start:ctx_end])

        for pattern, desc, severity in SECRET_PATTERNS:
            try:
                for m in re.finditer(pattern, line):
                    matched_str = m.group(0)
                    if not is_safe_context(matched_str, surrounding):
                        issues.append({
                            "line":     line_num,
                            "desc":     desc,
                            "severity": severity,
                            "content":  line.strip()[:100],
                        })
                        break
            except re.error:
                continue

        if len(issues) >= 10:
            break

    return issues


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            sys.exit(0)

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (
            ".ts", ".tsx", ".js", ".jsx", ".py", ".go",
            ".java", ".rs", ".php", ".rb", ".cs",
            ".env", ".yaml", ".yml", ".toml", ".json", ".sh", ".bash",
            ".conf", ".config", ".ini", ".properties",
        ):
            sys.exit(0)

        basename = os.path.basename(file_path).lower()
        if any(re.search(p, basename) for p in SAFE_FILE_PATTERNS):
            sys.exit(0)

        issues = scan_file(file_path)
        if not issues:
            sys.exit(0)

        severity_order = {"critical": 0, "high": 1, "medium": 2}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 9))

        severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "💡"}
        issue_lines = []
        for issue in issues:
            emoji = severity_emoji.get(issue["severity"], "⚠️")
            issue_lines.append(
                f"  {emoji} 第 {issue['line']} 行 [{issue['desc']}]：\n"
                f"     `{issue['content']}`"
            )

        feedback = (
            f"🔐 密钥泄露检测：{os.path.basename(file_path)} 发现 {len(issues)} 处风险\n\n"
            + "\n".join(issue_lines)
            + "\n\n**请立即修复**：\n"
            "1. 将硬编码值移至 `.env` 文件\n"
            "2. 代码改为 `process.env.KEY_NAME` 或 `os.environ.get('KEY_NAME')`\n"
            "3. 确认 `.env` 已加入 `.gitignore`\n"
            "4. 若已提交到 git，需 rotate 密钥（历史提交无法撤销泄露）"
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": feedback,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
