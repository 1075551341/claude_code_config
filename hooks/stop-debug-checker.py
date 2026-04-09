#!/usr/bin/env python3
"""
Stop Hook: Debug产物检测器
任务完成前检查修改的文件是否遗留debug代码

exit 0 = 允许完成（无debug产物或检查通过）
exit 2 = 阻止完成（发现debug产物）

检测内容：
- JavaScript/TypeScript: console.log, debugger, alert
- Python: print调试, pdb.set_trace, breakpoint, import pdb
- Go: fmt.Println调试代码
- 通用: TODO DEBUG, FIXME, HACK标记
"""
import json
import sys
import io
import re
import subprocess
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# Debug产物检测模式
DEBUG_PATTERNS = {
    r'\.js$': [
        r'console\.(log|warn|error|debug|info)\(',
        r'debugger;?',
        r'alert\(',
    ],
    r'\.(ts|tsx|jsx|mjs|cjs)$': [
        r'console\.(log|warn|error|debug|info)\(',
        r'debugger;?',
        r'alert\(',
        r'//\s*DEBUG',
        r'/\*\s*DEBUG',
    ],
    r'\.py$': [
        r'pdb\.set_trace\(',
        r'breakpoint\(',
        r'import\s+pdb',
        r'from\s+pdb\s+import',
        r'print\(["\']DEBUG',
        r'#\s*DEBUG',
        r'##\s*TODO.*debug',
    ],
    r'\.(go|golang)$': [
        r'fmt\.Println\(',
        r'fmt\.Printf\(',
        r'log\.Println\(',
        r'//\s*DEBUG',
    ],
    r'\.(java|kt)$': [
        r'System\.out\.print',
        r'Log\.d\(',
        r'//\s*DEBUG',
    ],
    r'\.(rb|ruby)$': [
        r'puts\s+[\'"].*debug',
        r'p\s+',
        r'require\s+[\'"]debug',
        r'byebug',
        r'debugger',
    ],
    r'\.(php)$': [
        r'var_dump\(',
        r'print_r\(',
        r'die\(',
        r'exit\(',
        r'//\s*DEBUG',
    ],
}

# 通用标记检测（所有文件类型）
GENERAL_MARKERS = [
    r'TODO\s*[:\-]?\s*DEBUG',
    r'FIXME\s*[:\-]?\s*debug',
    r'HACK\s*[:\-]?\s*',
    r'XXX\s*[:\-]?\s*',
    r'BUG\s*[:\-]?\s*',
]


def get_modified_files():
    """获取git中修改的文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="ignore"
        )
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            return [f for f in files if f]
    except Exception:
        pass
    return []


def check_file_for_debug_patterns(filepath, patterns):
    """检查单个文件是否包含debug模式"""
    found = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        found.append({
                            'line': i,
                            'content': line.strip()[:100],
                            'pattern': pattern
                        })
                        break
    except Exception:
        pass
    return found


def check_general_markers(filepath):
    """检查通用标记"""
    found = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                for pattern in GENERAL_MARKERS:
                    if re.search(pattern, line, re.IGNORECASE):
                        found.append({
                            'line': i,
                            'content': line.strip()[:100],
                            'marker': pattern
                        })
                        break
    except Exception:
        pass
    return found


def main():
    try:
        # 读取stdin（Stop hook的参数）
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            data = {}

        # 检查是否手动跳过了hook
        stop_hook_active = data.get("stop_hook_active", False)
        if stop_hook_active:
            sys.exit(0)

        modified_files = get_modified_files()
        if not modified_files:
            sys.exit(0)

        debug_findings = []

        for filepath in modified_files:
            if not os.path.isfile(filepath):
                continue

            # 检查特定语言的debug模式
            for ext_pattern, patterns in DEBUG_PATTERNS.items():
                if re.search(ext_pattern, filepath, re.IGNORECASE):
                    findings = check_file_for_debug_patterns(filepath, patterns)
                    if findings:
                        debug_findings.append({
                            'file': filepath,
                            'findings': findings
                        })
                    break
            else:
                # 检查通用标记
                findings = check_general_markers(filepath)
                if findings:
                    debug_findings.append({
                        'file': filepath,
                        'findings': findings
                    })

        if debug_findings:
            msg_lines = ["[Debug产物检测] 发现修改文件中存在调试代码，请清理后再完成：\n"]
            for item in debug_findings:
                msg_lines.append(f"\n📁 {item['file']}")
                for finding in item['findings']:
                    msg_lines.append(f"   第{finding['line']}行: {finding['content'][:80]}")

            msg_lines.append("\n如需跳过此检查完成任务，请明确告知'允许包含debug代码完成'")

            sys.stderr.write('\n'.join(msg_lines) + "\n")
            sys.stderr.flush()
            sys.exit(2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
