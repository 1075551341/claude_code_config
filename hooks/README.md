# Hooks 钩子系统

17 个自动化钩子，覆盖开发全流程。

---

## 架构概览

```
hooks/
├── _editor_hook_launcher.py  # 核心：编辑器检测 + 调度器
│
├── PreToolUse/               # 工具执行前
│   ├── pre-context-injector.py   # 上下文注入
│   ├── pre-task-planner.py       # 复杂任务计划生成
│   ├── pre-dep-checker.py        # 依赖安全检查
│   └── pre-bash-guard.py         # 危险命令拦截
│
├── PostToolUse/              # 工具执行后
│   ├── post-edit-format.py       # 自动格式化
│   ├── post-edit-lint.py         # Lint + 类型检查
│   ├── post-operation-log.py     # 操作日志
│   ├── post-secret-detector.py   # 密钥泄露检测
│   ├── post-doc-reminder.py      # 文档注释提醒
│   ├── post-test-runner.py       # 自动测试运行
│   └── post-auto-commit.py       # 自动提交（可选）
│
└── Stop/                     # 会话结束
    ├── stop-notify.py            # 系统通知
    ├── stop-daily-summary.py     # 每日工作总结
    └── stop-readme-updater.py    # README 自动更新
```

---

## 编辑器兼容机制

### 核心原理

`_editor_hook_launcher.py` 实现了完善的编辑器检测：

```python
# Windows: GetConsoleWindow API（O(1)）
if sys.platform == "win32" and _win_has_no_console():
    return True  # 编辑器环境，跳过 hooks

# Linux/macOS: TTY 检测 + Electron 父进程
if sys.platform != "win32":
    if _unix_has_no_tty() and _is_electron_parent():
        return True  # 编辑器环境，跳过 hooks
```

### 检测优先级

1. **环境变量覆盖** (`CLAUDE_HOOK_FORCE_CLI`)
2. **入口点检测** (`CLAUDE_CODE_ENTRYPOINT`)
3. **控制台检测** (Windows API / Unix TTY)
4. **编辑器标记** (`CLAUDE_IN_EDITOR`)
5. **路径检测** (CWD 包含编辑器路径)
6. **环境变量标记** (VSCODE_*, CURSOR_*, etc.)
7. **父进程链** (检测 Electron 进程)
8. **stdin 载荷** (路径检查)

### 同步策略

```markdown
同步到编辑器时：
- skills/ → 软连接
- agents/ → 软连接
- rules/ → 软连接
- CLAUDE.md → 复制
- hooks/ → 不同步（由 _editor_hook_launcher.py 处理跳过）
- settings.json → 不覆盖（保留编辑器模型配置）
```

---

## Hook 详细说明

### PreToolUse（工具执行前）

| Hook | 触发器 | 功能 | 超时 |
|------|--------|------|------|
| `pre-context-injector` | Task/Bash/Write/Edit | 会话首次运行注入上下文 | 5s |
| `pre-task-planner` | Task/Bash/Write | 复杂任务自动生成计划 | 15s |
| `pre-dep-checker` | Bash | npm/pip 依赖安全检查 | 10s |
| `pre-bash-guard` | Bash | 危险命令拦截 | 5s |

### PostToolUse（工具执行后）

| Hook | 触发器 | 功能 | 超时 |
|------|--------|------|------|
| `post-edit-format` | Edit/Write/MultiEdit | Prettier/Ruff/gofmt 格式化 | 30s |
| `post-edit-lint` | Edit/Write/MultiEdit | ESLint/tsc/ruff 检查 | 60s |
| `post-operation-log` | 多种工具 | 操作日志记录 | 10s |
| `post-secret-detector` | Edit/Write/MultiEdit | 密钥泄露检测 | 10s |
| `post-doc-reminder` | Edit/Write/MultiEdit | 函数文档注释提醒 | 10s |
| `post-test-runner` | Edit/Write/MultiEdit | 自动运行测试 | 120s |

### Stop（会话结束）

| Hook | 功能 | 超时 |
|------|------|------|
| `stop-notify` | 系统通知弹窗 | 5s |
| `stop-daily-summary` | 每日工作总结 | 15s |
| `stop-readme-updater` | README 自动更新 | 30s |

---

## 配置示例

### settings.json 配置

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/_editor_hook_launcher.py ~/.claude/hooks/post-edit-format.py",
            "timeout": 30000
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/_editor_hook_launcher.py ~/.claude/hooks/pre-bash-guard.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

---

## Hook 开发指南

### 模板

```python
#!/usr/bin/env python3
"""
Hook 类型: PreToolUse / PostToolUse / Stop
功能描述: [一句话说明]
"""
import json
import sys

def main():
    try:
        # 读取 stdin
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        # Hook 逻辑
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 处理逻辑...

        # exit 0 = 允许继续
        # exit 2 = 阻止执行，stderr 内容发送给 Claude
        sys.exit(0)

    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### 返回格式

```json
// 阻止执行（仅 PreToolUse）
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "阻止原因说明"
  }
}
```

---

## 统计

| 类型 | 数量 |
|------|------|
| PreToolUse | 4 |
| PostToolUse | 6 |
| Stop | 3 |
| **总计** | **13 个活跃钩子** |

---

## 新增 Hook

| Hook | 触发 | 功能 |
|------|------|------|
| pre-tool-matcher | PreToolUse | 智能工具匹配推荐 |

## Hook 编辑器兼容性

**关键机制**: _editor_hook_launcher.py 提供环境检测

`python
# 检测逻辑
1. 检查 CLAUDE_IN_EDITOR 环境变量
2. 检查 VSCODE_* / CURSOR_* / WINDSURF_* 环境变量
3. 检查进程链中的编辑器进程
4. 检查工作目录是否包含编辑器路径

# 结果
if 编辑器环境:
    跳过执行，直接返回 continue
else:
    正常执行 Hook 逻辑
`

这确保：
-  Claude Code CLI: 完整 Hook 功能
-  Cursor/Windsurf/Trae: 跳过可能影响模型的 Hooks

---

_更新：2026-04-09 | 总计: 13  14 Hooks_
