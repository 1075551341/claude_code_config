#!/usr/bin/env python3
"""
Stop Hook: 每日工作总结生成器
每天第一次会话结束时，汇总当日操作日志生成工作摘要
保存到 ~/.claude/daily_summary/ 目录，方便写周报
"""
import json
import sys
import os
import re
import io
from datetime import datetime, date
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOG_FILE    = os.path.join(os.path.expanduser("~"), ".claude", "logs", "operations.log")
SUMMARY_DIR = os.path.join(os.path.expanduser("~"), ".claude", "daily_summary")
TODAY_FLAG  = os.path.join(os.path.expanduser("~"), ".claude", "last_summary_date.txt")

def already_summarized_today():
    """今天是否已经生成过总结"""
    try:
        if os.path.exists(TODAY_FLAG):
            with open(TODAY_FLAG) as f:
                last = f.read().strip()
            return last == str(date.today())
    except Exception:
        pass
    return False

def mark_summarized():
    try:
        os.makedirs(os.path.dirname(TODAY_FLAG), exist_ok=True)
        with open(TODAY_FLAG, "w") as f:
            f.write(str(date.today()))
    except Exception:
        pass

def parse_today_logs():
    """解析今日操作日志"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    edited_files = []
    bash_commands = []
    sessions = set()

    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                if not line.startswith(f"[{today_str}"):
                    continue

                m = re.match(r'\[(.+?)\] \[(.+?)\] (\w+)\s+(.+)', line.strip())
                if not m:
                    continue

                ts, session, tool, content = m.groups()
                sessions.add(session)

                if tool in ("Edit", "Write", "MultiEdit"):
                    edited_files.append(content.strip())
                elif tool == "Bash":
                    bash_commands.append(content.strip())
    except Exception:
        pass

    return {
        "edited_files": edited_files,
        "bash_commands": bash_commands,
        "session_count": len(sessions),
        "total_edits": len(edited_files),
    }

def analyze_work(logs):
    """分析工作内容"""
    # 统计改动文件类型
    ext_counter = Counter()
    for f in logs["edited_files"]:
        ext = os.path.splitext(f)[1].lower() or "其他"
        ext_counter[ext] += 1

    # 提取涉及的主要目录/模块
    dirs = Counter()
    for f in logs["edited_files"]:
        parts = f.replace("\\", "/").split("/")
        if len(parts) >= 2:
            dirs[parts[-2]] += 1  # 取父目录

    # 分析执行的命令类型
    cmd_types = Counter()
    for cmd in logs["bash_commands"]:
        if cmd.startswith("git"):
            cmd_types["Git 操作"] += 1
        elif any(cmd.startswith(p) for p in ["npm", "pnpm", "yarn"]):
            cmd_types["包管理/构建"] += 1
        elif any(cmd.startswith(p) for p in ["python", "pytest", "vitest", "jest"]):
            cmd_types["测试运行"] += 1
        elif any(cmd.startswith(p) for p in ["docker", "kubectl"]):
            cmd_types["容器/部署"] += 1
        else:
            cmd_types["其他命令"] += 1

    return {
        "file_types": ext_counter.most_common(5),
        "main_modules": dirs.most_common(5),
        "cmd_types": dict(cmd_types),
    }

def generate_summary(logs, analysis):
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]

    # 文件类型统计
    file_type_str = "  ".join(
        f"`{ext}` × {count}" for ext, count in analysis["file_types"]
    ) or "无"

    # 主要模块
    modules_str = "、".join(
        m for m, _ in analysis["main_modules"]
    ) or "无"

    # 命令统计
    cmd_str = "\n".join(
        f"- {k}：{v} 次" for k, v in analysis["cmd_types"].items()
    ) or "- 无"

    # 编辑文件列表（去重，最多 20 个）
    unique_files = list(dict.fromkeys(logs["edited_files"]))[:20]
    files_str = "\n".join(f"- `{f}`" for f in unique_files) or "- 无"

    return f"""# 工作日报 · {today}（{weekday}）

> 由 Claude Code 自动生成，请补充具体工作内容后发送

---

## 📊 工作概览

| 指标 | 数值 |
|------|------|
| 编辑文件数 | {logs['total_edits']} 个文件 |
| 涉及模块 | {modules_str} |
| 文件类型 | {file_type_str} |
| AI 会话数 | {logs['session_count']} 个 |

## 🛠️ 执行操作

{cmd_str}

## 📁 变更文件

{files_str}

---

## ✅ 今日完成（请补充）

- [ ] 
- [ ] 

## 🔄 明日计划（请补充）

- [ ] 
- [ ] 

## ⚠️ 遇到的问题（请补充）

- 

---

*生成时间：{datetime.now().strftime("%H:%M:%S")}  ·  Claude Code 自动生成*
"""

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    stop_reason = data.get("stop_reason", "")
    if stop_reason not in ("end_turn", "stop_sequence", ""):
        sys.exit(0)

    # 今天已生成过则跳过
    if already_summarized_today():
        sys.exit(0)

    logs = parse_today_logs()

    # 没有足够操作则跳过
    if logs["total_edits"] < 3:
        sys.exit(0)

    analysis = analyze_work(logs)
    summary  = generate_summary(logs, analysis)

    # 保存
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    today_file = os.path.join(
        SUMMARY_DIR,
        f"{datetime.now().strftime('%Y-%m-%d')}_daily.md"
    )
    with open(today_file, "w", encoding="utf-8") as f:
        f.write(summary)

    mark_summarized()

    result = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"📋 今日工作摘要已生成：{today_file}\n"
                f"共编辑 {logs['total_edits']} 个文件，"
                f"涉及模块：{', '.join(m for m, _ in analysis['main_modules'][:3])}"
            )
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
