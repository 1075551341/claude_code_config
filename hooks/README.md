# Hooks 钩子系统

> Claude Code 专用，其他编辑器通过 `_editor_hook_launcher.py` 跳过
>
> 整合自：
>
> - [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 60KB+ hooks配置
> - [obra/superpowers](https://github.com/obra/superpowers) - SessionStart钩子
> - [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - Profile-based hooks

---

## 设计原则（来自 everything-claude-code）

### 1. 事件驱动自动化

```
User request → Claude picks tool → PreToolUse hook → Tool executes → PostToolUse hook
```

### 2. Profile-based 钩子控制

通过环境变量切换钩子集合：

```bash
ECC_HOOK_PROFILE=minimal   # 仅保留生命周期和安全钩子
ECC_HOOK_PROFILE=standard # 默认：平衡质量和安全
ECC_HOOK_PROFILE=strict   # 启用额外提醒和更严格guardrails
```

### 3. 平台自适应输出

```bash
if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
  printf '{ "additional_context": "%s" }\n'
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
  printf '{ "hookSpecificOutput": { "additionalContext": "%s" }\n}'
else
  printf '{ "additionalContext": "%s" }\n'
fi
```

### 4. 跨平台兼容性

Hook 实现使用 **Node.js** 而非纯 shell，确保 Windows 兼容性。

---

## 钩子分类概览

| 类型         | 数量   | 说明       |
| ------------ | ------ | ---------- |
| PreToolUse   | 16     | 工具执行前 |
| PostToolUse  | 15     | 工具执行后 |
| Stop         | 10     | 会话结束   |
| SessionStart | 1      | 会话启动   |
| PreCompact   | 1      | 压缩前     |
| **总计**     | **43** |            |

---

## PreToolUse Hooks

| Hook                        | 功能                     | 触发            | 优先级 | 来自                   |
| --------------------------- | ------------------------ | --------------- | ------ | ---------------------- |
| `pre-context-injector`      | 上下文注入               | Task/Write/Edit | HIGH   | superpowers            |
| `pre-task-planner`          | 任务规划                 | Task/Bash/Write | HIGH   | -                      |
| `pre-bash-guard`            | Bash危险命令拦截         | Bash            | HIGH   | everything-claude-code |
| `pre-dep-checker`           | 依赖安全检查             | Bash            | HIGH   | -                      |
| `pre-config-protection`     | 配置文件保护             | Write/Edit      | MEDIUM | -                      |
| `pre-token-budget`          | Token预算检查            | 全局            | MEDIUM | claude-context         |
| `pre-git-hook-bypass-block` | 阻止git --no-verify      | Bash            | HIGH   | -                      |
| `pre-commit-quality`        | 提交前质量检查           | Bash            | MEDIUM | -                      |
| `pre-dev-server-blocker`    | 阻止tmux外运行dev server | Bash            | LOW    | -                      |
| `pre-git-push-reminder`     | push前提醒               | Bash            | LOW    | -                      |
| `pre-doc-file-warning`      | 文档文件警告             | Write           | LOW    | -                      |
| `pre-mcp-health-check`      | MCP健康检查              | Bash            | LOW    | -                      |
| `pre-compact-state`         | 压缩前状态保存           | PreCompact      | MEDIUM | -                      |
| `pre-tool-matcher`          | 工具匹配                 | 全局            | MEDIUM | -                      |
| `pre-observe-tool`          | 工具执行观察             | 全局            | LOW    | -                      |
| `pre-suggest-compact`       | 建议压缩                 | 全局            | LOW    | -                      |

### 核心 PreToolUse Hooks

#### pre-bash-guard

**功能**: 拦截危险的 Bash 命令

```bash
# 阻止的命令
git push --force
rm -rf /system
curl -X POST http://internal/  # SSRF 风险
```

#### pre-git-hook-bypass-block

**功能**: 阻止 git --no-verify 绕过钩子

```bash
git commit --no-verify  # 阻止
git push --no-verify     # 阻止
```

#### pre-context-injector

**功能**: 在 SessionStart 时注入 using-superpowers

```xml
<EXTREMELY_IMPORTANT>
You have superpowers.
**Below is the full content of your 'superpowers:using-superpowers' skill**
</EXTREMELY_IMPORTANT>
```

---

## PostToolUse Hooks

| Hook                          | 功能            | 触发        | 优先级 | 来自 |
| ----------------------------- | --------------- | ----------- | ------ | ---- |
| `post-edit-format`            | 代码格式化      | Edit/Write  | HIGH   | -    |
| `post-edit-lint`              | Lint+类型检查   | Edit/Write  | HIGH   | -    |
| `post-secret-detector`        | 密钥泄露检测    | Edit/Write  | HIGH   | -    |
| `post-test-runner`            | 自动测试运行    | Bash        | HIGH   | -    |
| `post-operation-log`          | 操作日志        | 全局        | MEDIUM | -    |
| `post-auto-commit`            | 自动提交格式    | Bash        | MEDIUM | -    |
| `post-build-analysis`         | 构建分析        | Bash        | LOW    | -    |
| `post-command-log-audit`      | 命令日志审计    | Bash        | LOW    | -    |
| `post-cost-tracker`           | 成本追踪        | Stop        | LOW    | -    |
| `post-dependency-audit`       | 依赖审计        | Bash        | LOW    | -    |
| `post-doc-reminder`           | 文档更新提醒    | Stop        | LOW    | -    |
| `post-edit-console-warn`      | console.log警告 | Edit        | MEDIUM | -    |
| `post-governance-capture`     | 治理捕获        | Stop        | LOW    | -    |
| `post-observe-result`         | 结果观察        | PostToolUse | LOW    | -    |
| `post-pr-logger`              | PR日志          | Bash        | LOW    | -    |
| `post-record-js-edits`        | JS编辑记录      | Edit        | LOW    | -    |
| `post-batch-format-typecheck` | 批量格式化检查  | Stop        | MEDIUM | -    |

### 核心 PostToolUse Hooks

#### post-secret-detector

**功能**: 检测密钥、Token、密码泄露

```bash
# 检测模式
password=
api_key=
token=
secret=
ghp_xxx  # GitHub Token
sk-xxx   # OpenAI Key
```

#### post-edit-format

**功能**: 编辑后自动格式化

```bash
# 支持的格式化
prettier eslint ruff black
```

#### post-edit-lint

**功能**: 编辑后运行 Lint + 类型检查

```bash
# 典型命令
npm run lint
tsc --noEmit
ruff check
```

---

## Stop Hooks

| Hook                      | 功能         | 优先级 |
| ------------------------- | ------------ | ------ |
| `stop-notify`             | 桌面通知     | MEDIUM |
| `stop-daily-summary`      | 每日总结     | HIGH   |
| `stop-readme-updater`     | README更新   | LOW    |
| `stop-debug-checker`      | Debug检查    | MEDIUM |
| `stop-session-summary`    | 会话摘要     | MEDIUM |
| `stop-session-end-marker` | 会话结束标记 | LOW    |
| `stop-pattern-extraction` | 模式提取     | MEDIUM |
| `stop-persist-session`    | 会话持久化   | LOW    |
| `stop-cost-tracker`       | 成本追踪     | LOW    |
| `stop-evaluate-patterns`  | 模式评估     | LOW    |

### 核心 Stop Hooks

#### stop-daily-summary

**功能**: 生成每日工作总结

```
今日完成：
- [任务1]
- [任务2]

明日计划：
- [任务1]

遇到的问题：
- [问题描述]
```

#### stop-pattern-extraction

**功能**: 从会话中提取可复用的模式

```markdown
---
name: pattern-name
date: 2026-04-15
confidence: 0.85
source: session
---

# Pattern Name

## 背景

[什么场景]

## 模式

[发现什么]
```

---

## SessionStart Hooks

| Hook                      | 功能         | 优先级 |
| ------------------------- | ------------ | ------ |
| `session-start-bootstrap` | 会话启动引导 | HIGH   |

### session-start-bootstrap

**功能**: 会话启动时执行初始化

```bash
# 典型操作
1. 读取 using-superpowers 内容
2. 检测编辑器环境
3. 注入上下文
```

---

## Hook 开发指南

### 标准 Hook 格式

```python
#!/usr/bin/env python3
"""功能描述"""
import json, sys

def main():
    data = json.loads(sys.stdin.read() or "{}")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 处理逻辑...

    # 允许继续
    sys.exit(0)
    # 或阻止执行
    # sys.exit(2)

if __name__ == "__main__":
    main()
```

### 输入数据结构

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git status"
  },
  "session_id": "xxx",
  "workspace_dir": "/path/to/workspace"
}
```

### 退出码

| 退出码 | 含义         |
| ------ | ------------ |
| 0      | 允许继续执行 |
| 2      | 阻止执行     |

---

## Profile 配置

通过环境变量切换钩子集合，无需修改文件：

```bash
export CLAUDE_HOOK_PROFILE=minimal   # 仅保留生命周期和安全钩子
export CLAUDE_HOOK_PROFILE=standard  # 默认：平衡质量和安全
export CLAUDE_HOOK_PROFILE=strict    # 完整配置：所有钩子启用
export CLAUDE_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"  # 禁用特定钩子
```

### minimal

仅保留：pre-context-injector, pre-bash-guard, post-secret-detector

### standard

平衡配置：所有 HIGH + 核心 MEDIUM 钩子

### strict

完整配置：所有钩子启用

## 跨平台兼容性

Hook 实现使用 **Python 3** 而非纯 shell，确保 Windows/macOS/Linux 兼容性。
编辑器适配通过 `_editor_hook_launcher.py` 自动检测环境：
- Claude Code 环境 → 执行 hooks
- Cursor / Windsurf / Trae 环境 → 跳过 hooks（避免冲突）

---

## 编辑器安全

`_editor_hook_launcher.py` v3.0 自动检测编辑器环境并跳过 hooks。

```python
# 检测逻辑
if os.environ.get("CURSOR_PLUGIN_ROOT"):
    # Cursor 环境
    skip_hooks()
elif os.environ.get("CLAUDE_PLUGIN_ROOT"):
    # Claude Code 环境
    run_hooks()
```

---

## 来源

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Profile Hooks、Secret检测、Instinct系统
- [obra/superpowers](https://github.com/obra/superpowers) - SessionStart 钩子、Iron Law、证据优先
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - Profile-based Hooks、Phase工作流
- [zilliztech/claude-context](https://github.com/zilliztech/claude-context) - Token预算检查、上下文压缩
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) - 跨会话记忆持久化

---

## 统计

| 类型         | 数量   |
| ------------ | ------ |
| PreToolUse   | 16     |
| PostToolUse  | 15     |
| Stop         | 10     |
| SessionStart | 1      |
| PreCompact   | 1      |
| **总计**     | **43** |
