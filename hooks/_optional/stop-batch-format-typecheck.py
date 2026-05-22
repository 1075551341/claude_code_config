#!/usr/bin/env python3
"""
Stop Hook: Batch Format and Typecheck All JS/TS Files
批量格式化和类型检查所有编辑过的 JavaScript/TypeScript 文件
在 Stop 事件时运行一次，而不是每次 Edit 后都运行

exit 0 = 正常结束
"""
import json
import sys
import io
import os
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# JS/TS 编辑记录文件
JS_EDITS_FILE = os.path.expanduser("~/.claude/js-edits-session.json")


def load_js_edits():
    """加载 JS/TS 编辑记录"""
    try:
        if os.path.exists(JS_EDITS_FILE):
            with open(JS_EDITS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def clear_js_edits():
    """清空 JS/TS 编辑记录"""
    try:
        if os.path.exists(JS_EDITS_FILE):
            os.remove(JS_EDITS_FILE)
    except Exception:
        pass


def format_files(file_paths):
    """格式化文件"""
    formatted = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
        
        try:
            # 尝试使用 Prettier
            result = subprocess.run(
                ["npx", "prettier", "--write", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                formatted.append(file_path)
        except Exception:
            try:
                # 回退到 Biome
                result = subprocess.run(
                    ["npx", "biome", "format", "--write", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    formatted.append(file_path)
            except Exception:
                pass
    
    return formatted


def typecheck_files(file_paths):
    """类型检查文件"""
    errors = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
        
        # 只检查 .ts 和 .tsx 文件
        if not file_path.endswith(('.ts', '.tsx')):
            continue
        
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", file_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0 and result.stderr:
                errors.append(f"{file_path}: {result.stderr}")
        except Exception:
            pass
    
    return errors


def main():
    try:
        # 加载编辑记录
        js_edits = load_js_edits()
        
        if not js_edits:
            sys.exit(0)
        
        # 格式化文件
        formatted = format_files(js_edits)
        
        # 类型检查
        type_errors = typecheck_files(js_edits)
        
        # 清空记录
        clear_js_edits()
        
        # 输出结果
        if formatted or type_errors:
            output = []
            if formatted:
                output.append(f"✅ 已格式化 {len(formatted)} 个 JS/TS 文件")
            if type_errors:
                output.append(f"⚠️ 类型检查发现 {len(type_errors)} 个错误")
                output.extend(type_errors[:5])  # 只显示前 5 个
            
            if output:
                print("\n" + "\n".join(output))

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
