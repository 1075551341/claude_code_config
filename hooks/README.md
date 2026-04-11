# Hooks 钩子系统

47 个自动化钩子，覆盖开发全流程。

---

## 架构概览

```
hooks/
├── _editor_hook_launcher.py  # 核心：编辑器检测 + 调度器
│
├── PreToolUse/               # 工具执行前
│   ├── pre-context-injector.py           # 上下文注入
│   ├── pre-task-planner.py               # 复杂任务计划生成
│   ├── pre-dep-checker.py                # 依赖安全检查
│   ├── pre-bash-guard.py                 # 危险命令拦截
│   ├── pre-commit-quality.py            # Git 提交质量检查
│   ├── pre-git-push-reminder.py         # Git push 前提醒审查
│   ├── pre-doc-file-warning.py          # 非标准文档文件警告
│   ├── pre-config-protection.py         # 配置文件保护
│   ├── pre-tool-matcher.py              # 智能工具匹配推荐
│   ├── pre-dev-server-blocker.py        # Dev Server tmux 拦截
│   ├── pre-tmux-reminder.py             # 长时间运行命令 tmux 提醒
│   ├── pre-mcp-health-check.py          # MCP 服务器健康检查
│   ├── pre-token-budget.py              # Token 预算预警
│   ├── pre-suggest-compact.py           # 手动压缩建议
│   ├── pre-observe-tool.py              # 工具使用观察（持续学习）
│   └── pre-git-hook-bypass-block.py     # 阻止 git --no-verify
│
├── PostToolUse/              # 工具执行后
│   ├── post-edit-format.py             # 自动格式化
│   ├── post-edit-lint.py               # Lint + 类型检查
│   ├── post-operation-log.py           # 操作日志
│   ├── post-secret-detector.py         # 密钥泄露检测
│   ├── post-doc-reminder.py            # 文档注释提醒
│   ├── post-test-runner.py             # 自动测试运行
│   ├── post-auto-commit.py             # 自动提交（可选）
│   ├── post-edit-console-warn.py       # Console.log 警告
│   ├── post-command-log-audit.py       # Bash 命令日志审计
│   ├── post-dependency-audit.py        # 依赖审计
│   ├── post-pr-logger.py               # PR 创建日志记录
│   ├── post-build-analysis.py          # 构建分析
│   ├── post-governance-capture.py      # 治理事件捕获
│   ├── post-cost-tracker.py            # 成本追踪
│   ├── post-record-js-edits.py         # 记录 JS/TS 编辑
│   └── post-observe-result.py          # 工具结果观察（持续学习）
│
├── SessionStart/             # 会话启动
│   └── session-start-bootstrap.py      # 会话启动引导
│
├── PreCompact/               # 上下文压缩前
│   └── pre-compact-state.py          # 压缩前状态保存
│
├── SessionEnd/               # 会话结束
│   └── stop-session-end-marker.py     # 会话结束标记
│
└── Stop/                     # 会话结束
    ├── stop-notify.py                # 系统通知
    ├── stop-daily-summary.py         # 每日工作总结
    ├── stop-readme-updater.py        # README 自动更新
    ├── stop-debug-checker.py         # 调试检查
    ├── stop-session-summary.py       # 会话总结
    ├── stop-pattern-extraction.py    # 模式提取
    ├── stop-cost-tracker.py          # 成本追踪
    ├── stop-batch-format-typecheck.py # 批量格式化类型检查
    ├── stop-persist-session.py       # 持久化会话状态
    └── stop-evaluate-patterns.py     # 评估可提取模式
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
| `pre-commit-quality` | Bash | Git 提交质量检查 | 15s |
| `pre-git-push-reminder` | Bash | Git push 前提醒审查 | 5s |
| `pre-doc-file-warning` | Write | 非标准文档文件警告 | 3s |
| `pre-config-protection` | Write/Edit/MultiEdit | 配置文件保护 | 5s |
| `pre-tool-matcher` | Skill | 智能工具匹配推荐 | 5s |
| `pre-dev-server-blocker` | Bash | Dev Server tmux 拦截 | 5s |
| `pre-tmux-reminder` | Bash | 长时间运行命令 tmux 提醒 | 3s |
| `pre-mcp-health-check` | MCP 工具 | MCP 服务器健康检查 | 5s |
| `pre-token-budget` | 多种工具 | Token 预算预警 | 3s |
| `pre-suggest-compact` | 多种工具 | 手动压缩建议（约 50 次调用后） | 3s |
| `pre-observe-tool` | 多种工具 | 工具使用观察（持续学习） | 3s |
| `pre-git-hook-bypass-block` | Bash | 阻止 git --no-verify 标志 | 3s |

### PostToolUse（工具执行后）

| Hook | 触发器 | 功能 | 超时 |
|------|--------|------|------|
| `post-edit-format` | Edit/Write/MultiEdit | Prettier/Ruff/gofmt 格式化 | 30s |
| `post-edit-lint` | Edit/Write/MultiEdit | ESLint/tsc/ruff 检查 | 60s |
| `post-operation-log` | 多种工具 | 操作日志记录 | 10s |
| `post-secret-detector` | Edit/Write/MultiEdit | 密钥泄露检测 | 10s |
| `post-doc-reminder` | Edit/Write/MultiEdit | 函数文档注释提醒 | 10s |
| `post-test-runner` | Edit/Write/MultiEdit | 自动运行测试 | 120s |
| `post-edit-console-warn` | Edit/Write/MultiEdit | Console.log 警告 | 5s |
| `post-command-log-audit` | Bash | 命令日志审计 | 3s |
| `post-dependency-audit` | Bash | 依赖审计 | 10s |
| `post-pr-logger` | Bash | PR 创建日志记录 | 5s |
| `post-build-analysis` | Bash | 构建分析 | 15s |
| `post-governance-capture` | 多种工具 | 治理事件捕获 | 5s |
| `post-cost-tracker` | Bash | 成本追踪（bash 工具使用） | 3s |
| `post-record-js-edits` | Edit/Write/MultiEdit | 记录 JS/TS 文件编辑 | 3s |
| `post-observe-result` | 多种工具 | 工具结果观察（持续学习） | 3s |

### SessionStart（会话启动）

| Hook | 功能 | 超时 |
|------|------|------|
| `session-start-bootstrap` | 会话启动引导，检测包管理器 | 10s |

### PreCompact（上下文压缩前）

| Hook | 功能 | 超时 |
|------|------|------|
| `pre-compact-state` | 压缩前状态保存 | 5s |

### SessionEnd（会话结束）

| Hook | 功能 | 超时 |
|------|------|------|
| `stop-session-end-marker` | 会话结束生命周期标记（非阻塞） | 3s |

### Stop（会话结束）

| Hook | 功能 | 超时 |
|------|------|------|
| `stop-notify` | 系统通知弹窗 | 5s |
| `stop-daily-summary` | 每日工作总结 | 15s |
| `stop-readme-updater` | README 自动更新 | 30s |
| `stop-debug-checker` | 调试检查 | 10s |
| `stop-session-summary` | 会话总结 | 15s |
| `stop-pattern-extraction` | 模式提取 | 10s |
| `stop-cost-tracker` | 成本追踪 | 5s |
| `stop-batch-format-typecheck` | 批量格式化类型检查（JS/TS） | 60s |
| `stop-persist-session` | 持久化会话状态 | 5s |
| `stop-evaluate-patterns` | 评估可提取模式 | 10s |

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
| PreToolUse | 16 |
| PostToolUse | 15 |
| SessionStart | 1 |
| PreCompact | 1 |
| SessionEnd | 1 |
| Stop | 10 |
| 辅助脚本 | 3（launcher + safe_guard + compact-state） |
| **总计** | **47 个 .py 文件** |

---

## Hook 来源说明

基于以下 GitHub 仓库优化补全：

- **affaan-m/everything-claude-code**: 提供了完整的 hooks 系统架构和实现参考，新增了持续学习、成本追踪、批量格式化等 hooks
- **obra/superpowers**: 提供了 hooks 最佳实践和跨平台兼容方案，参考了 SessionStart hook 的实现
- **anthropics/skills**: 官方技能系统规范
- **ComposioHQ/awesome-claude-skills**: 技能集合和 marketplace 架构

新增 hooks 主要参考 affaan-m/everything-claude-code 的实现，并结合实际需求进行了本地化优化。去除了与 React hooks 相关的内容（bytedance/deer-flow 和 Chalarangelo/30-seconds-of-code），因为这些是前端 React hooks，与 Claude Code 的 hooks 系统无关。

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
