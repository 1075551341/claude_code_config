#!/usr/bin/env python3
"""
PostToolUse Hook: 依赖安全审计
在 package.json / requirements.txt 等依赖文件修改后自动运行安全审计

exit 0 = 允许继续
exit 2 = 发现高危漏洞（仅警告，不阻止）
"""
import json
import sys
import io
import subprocess
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# 依赖文件模式
DEPENDENCY_FILES = {
    "package.json": ("npm", ["npm", "audit", "--json"]),
    "package-lock.json": ("npm", ["npm", "audit", "--json"]),
    "yarn.lock": ("yarn", ["yarn", "audit", "--json"]),
    "pnpm-lock.yaml": ("pnpm", ["pnpm", "audit", "--json"]),
    "requirements.txt": ("pip", ["pip", "audit", "--format", "json"]),
    "pyproject.toml": ("pip", ["pip", "audit", "--format", "json"]),
    "poetry.lock": ("poetry", ["poetry", "show", "--json"]),
    "Gemfile.lock": ("bundler", ["bundle", "audit", "check", "--format", "json"]),
}


def run_audit(cmd: list, cwd: str) -> dict | None:
    """运行依赖审计命令"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        # npm audit 返回非0表示有漏洞
        if result.stdout.strip():
            return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "审计超时"}
    except FileNotFoundError:
        return {"error": f"命令未找到: {cmd[0]}"}
    except json.JSONDecodeError:
        return {"error": "输出解析失败"}
    except Exception as e:
        return {"error": str(e)}
    return None


def count_vulnerabilities(audit_result: dict, pkg_manager: str) -> dict:
    """统计漏洞数量"""
    counts = {"critical": 0, "high": 0, "moderate": 0, "low": 0, "info": 0}

    if pkg_manager == "npm":
        # npm audit 格式
        metadata = audit_result.get("metadata", {})
        vulns = metadata.get("vulnerabilities", {})
        counts["critical"] = vulns.get("critical", 0)
        counts["high"] = vulns.get("high", 0)
        counts["moderate"] = vulns.get("moderate", 0)
        counts["low"] = vulns.get("low", 0)
        counts["info"] = vulns.get("info", 0)

    elif pkg_manager == "pip":
        # pip audit 格式
        for vuln in audit_result.get("vulnerabilities", []):
            severity = vuln.get("severity", "low").lower()
            if severity in counts:
                counts[severity] += 1

    return counts


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in ("Edit", "Write", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # 检查是否为依赖文件
        file_name = os.path.basename(file_path)
        if file_name not in DEPENDENCY_FILES:
            sys.exit(0)

        pkg_manager, audit_cmd = DEPENDENCY_FILES[file_name]
        cwd = os.path.dirname(os.path.abspath(file_path)) or os.getcwd()

        # 运行审计
        audit_result = run_audit(audit_cmd, cwd)

        if not audit_result or "error" in audit_result:
            # 审计失败，静默退出
            sys.exit(0)

        # 统计漏洞
        counts = count_vulnerabilities(audit_result, pkg_manager)
        total = sum(counts.values())

        if total == 0:
            sys.exit(0)

        # 构建警告消息
        warnings = [f"📦 依赖安全审计 ({pkg_manager})"]

        if counts["critical"] > 0:
            warnings.append(f"  🔴 Critical: {counts['critical']}")
        if counts["high"] > 0:
            warnings.append(f"  🟠 High: {counts['high']}")
        if counts["moderate"] > 0:
            warnings.append(f"  🟡 Moderate: {counts['moderate']}")
        if counts["low"] > 0:
            warnings.append(f"  🔵 Low: {counts['low']}")

        if counts["critical"] > 0 or counts["high"] > 0:
            warnings.append("  ⚠️ 建议运行修复命令:")
            if pkg_manager == "npm":
                warnings.append("     npm audit fix")
            elif pkg_manager == "yarn":
                warnings.append("     yarn audit")
            elif pkg_manager == "pip":
                warnings.append("     pip-audit --fix")

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(warnings),
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