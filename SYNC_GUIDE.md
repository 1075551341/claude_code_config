---
description: 跨编辑器配置同步指南
---

# Claude 配置跨编辑器同步指南

> **目的**：将 `~/.claude` 配置通过软链接同步到 Cursor、Windsurf、Trae 等编辑器，确保跨编辑器体验一致且安全。

## 配置结构

```text
~/.claude/                    # 主配置目录（仅 Claude Code 使用完整功能）
├── CLAUDE.md                 # ✅ 同步 - 核心规则（所有编辑器）
├── rules/                    # ✅ 同步 - 各类规则文件
│   ├── RULES_CORE.md         #     核心规则（alwaysApply）
│   ├── RULES_FRONTEND.md     #     前端规则
│   ├── RULES_BACKEND.md     #     后端规则
│   └── ...
├── agents/                   # ✅ 同步 - Agent 定义
│   ├── code-review-workflow.md
│   ├── debugger.md
│   └── ...
├── skills/                   # ✅ 同步 - 技能库（Markdown 格式）
├── hooks/                    # ❌ 不同步 - Claude Code 专用
│   ├── _editor_hook_launcher.py    # 编辑器检测（v3.0）
│   ├── pre-bash-guard.py
│   └── ...
├── .mcp.json                 # ❌ 不同步 - 各编辑器独立配置
├── settings.json             # ❌ 不同步 - Claude Code 专用
├── .claude.json              # ❌ 不同步 - Claude Code 专用
├── TOOL_MATCHING_GUIDE.md    # ✅ 同步 - 工具匹配指南
├── SYNC_GUIDE.md             # 📘 本文件
└── sync.ps1                  # 🚀 Windows 同步脚本
```

## 同步策略

### ✅ 完全同步项

| 目录/文件 | 同步方式 | 目标位置 | 说明 |
|-----------|---------|---------|------|
| `CLAUDE.md` | 软链接/复制 | 各编辑器 rules 目录 | 核心行为规范 |
| `rules/*.md` | 软链接/复制 | 各编辑器 rules 目录 | 分类规则文件 |
| `agents/*.md` | 软链接/复制 | 各编辑器 agents 目录 | Agent 定义 |
| `skills/*.md` | 软链接/复制 | 各编辑器 skills 目录 | 技能库 |
| `TOOL_MATCHING_GUIDE.md` | 复制 | 各编辑器目录 | 工具匹配参考 |

### ❌ 不同步项（Claude Code 专用）

| 文件 | 原因 | 风险说明 |
|------|------|---------|
| `hooks/` | 防止干扰编辑器内模型调用 | **高风险**：Hooks 在编辑器中运行可能导致无限循环、响应延迟、工具调用冲突 |
| `.mcp.json` | 各编辑器 MCP 配置格式不同 | Cursor/Windsurf 使用不同的 MCP 配置格式 |
| `settings.json` | 包含 Claude Code 专属设置 | 包含 hooks 配置、权限设置等编辑器不支持的选项 |
| `.claude.json` | Claude Code 状态文件 | 编辑器无法识别 |
| `sync.ps1` | 仅在主环境使用 | 无需同步 |

## 软链接创建方式

### Windows (PowerShell - 管理员权限)

```powershell
# 创建符号链接（需要管理员权限）
# Cursor
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.cursor\rules\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" `
    -Force

# 复制规则文件（不推荐软链接，避免权限问题）
Copy-Item "$env:USERPROFILE\.claude\rules\*" `
    -Destination "$env:USERPROFILE\.cursor\rules\" `
    -Recurse -Force

# Windsurf
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.windsurf\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" `
    -Force

# Trae
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.trae\rules\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" `
    -Force
```

### macOS / Linux

```bash
# Cursor
ln -sf ~/.claude/CLAUDE.md ~/.cursor/rules/CLAUDE.md
ln -sf ~/.claude/rules/* ~/.cursor/rules/

# Windsurf
ln -sf ~/.claude/CLAUDE.md ~/.windsurf/CLAUDE.md

# Trae
ln -sf ~/.claude/CLAUDE.md ~/.trae/rules/CLAUDE.md
```

## 各编辑器配置详情

### Claude Code (主环境)

```bash
# 原生支持 ~/.claude 目录
# 所有功能完整可用：hooks、MCP、agents、rules
claude config set allowNestedBashCommands true
```

### Cursor

**配置路径**：`~/.cursor/rules/`

```powershell
# 1. 创建目录
mkdir -Force "$env:USERPROFILE\.cursor\rules"
mkdir -Force "$env:USERPROFILE\.cursor\agents"

# 2. 软链接核心文件
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.cursor\rules\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" -Force

# 3. 复制规则文件（批量）
Copy-Item "$env:USERPROFILE\.claude\rules\*.md" `
    -Destination "$env:USERPROFILE\.cursor\rules\" -Force

# 4. 复制 agents
Copy-Item "$env:USERPROFILE\.claude\agents\*.md" `
    -Destination "$env:USERPROFILE\.cursor\agents\" -Force
```

**Cursor 特有配置**：
- 支持 `.cursorrules` 文件（单文件模式）
- 支持 `.cursor/rules/` 目录（多文件模式，推荐）

### Windsurf

**配置路径**：`~/.windsurf/`

```powershell
# 1. 创建目录
mkdir -Force "$env:USERPROFILE\.windsurf\rules"

# 2. 软链接或复制
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.windsurf\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" -Force

# 3. 复制 rules
Copy-Item "$env:USERPROFILE\.claude\rules\*.md" `
    -Destination "$env:USERPROFILE\.windsurf\rules\" -Force
```

### Trae

**配置路径**：`~/.trae/rules/`

```powershell
# 1. 创建目录
mkdir -Force "$env:USERPROFILE\.trae\rules"

# 2. 软链接
New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.trae\rules\CLAUDE.md" `
    -Target "$env:USERPROFILE\.claude\CLAUDE.md" -Force

# 3. 复制 rules
Copy-Item "$env:USERPROFILE\.claude\rules\*.md" `
    -Destination "$env:USERPROFILE\.trae\rules\" -Force
```

## 编辑器安全保护机制

### _editor_hook_launcher.py v3.0

Hooks 使用多层检测确保在编辑器环境中安全跳过：

**检测优先级**：
1. **环境变量**（最高优先级）
   - `CLAUDE_HOOK_SKIP=1` - 强制跳过
   - `CLAUDE_HOOK_FORCE_CLI=1` - 强制执行
   - `CLAUDE_CODE_ENTRYPOINT` - 入口点识别

2. **控制台检测**（Windows）
   - `GetConsoleWindow() == 0` → 无控制台 → 编辑器环境 → 跳过

3. **TTY 检测**（Unix）
   - `!isatty(0)` + VS Code 环境标记 → 编辑器环境 → 跳过

4. **环境标记检测**
   - `VSCODE_PID`, `CURSOR_CHANNEL`, `WINDSURF_APP_VERSION`

5. **工作目录检测**
   - 路径包含 `.cursor/`, `.windsurf/`, `.trae/` 等

**安全输出**：
- 编辑器环境：`{"continue": true, "skipped": true}`
- CLI 环境：执行真实 hook

## 工具匹配跨编辑器兼容

### 工具名称映射

| 功能 | Claude Code | Cursor | Windsurf | Gemini CLI | Copilot CLI |
|------|-------------|--------|----------|------------|-------------|
| 读取文件 | `Read` | `read_file` | `read_file` | `view` | `view` |
| 编辑文件 | `Edit` | `apply_diff` | `edit_file` | `replace` | `edit` |
| 创建文件 | `Write` | `write_file` | `write_file` | `create` | `write` |
| 搜索代码 | `Grep` | `search_files` | `search` | `grep` | `search` |
| 查找文件 | `Glob` | `list_dir` | `glob` | `ls` | `glob` |
| 执行命令 | `Bash` | `run_terminal_cmd` | `run_command` | `bash` | `bash` |
| 调用 Agent | `Task` | `agent` | `agent` | N/A | `agent` |
| 调用 Skill | `Skill` | N/A | N/A | `activate_skill` | `skill` |

### 自然语言工具匹配

在各编辑器中，使用自然语言描述任务，模型自动匹配工具：

```
"查 React 文档" → ctx7 (Claude) / web_search (Cursor)
"搜索这个错误" → brave / web_search
"测试这个页面" → pw / playwright
"查看 Git 记录" → git
"发 Slack 通知" → slack
```

## 同步脚本使用

### Windows (sync.ps1)

```powershell
# 运行同步脚本
~/.claude/sync.ps1

# 功能
- [✓] 软链接 CLAUDE.md 到各编辑器
- [✓] 复制 rules/ 到各编辑器
- [✓] 复制 agents/ 到各编辑器
- [✓] 复制 skills/ 到各编辑器
- [✗] 排除 hooks/（安全保护）
- [✗] 排除 .mcp.json（各编辑器独立）
- [✓] 创建备份
- [✓] 生成同步报告
```

### 手动同步检查清单

```markdown
□ 1. 备份现有配置
□ 2. 创建软链接（CLAUDE.md）
□ 3. 复制 rules/*.md
□ 4. 复制 agents/*.md
□ 5. 复制 skills/*.md
□ 6. 验证文件权限
□ 7. 重启编辑器
□ 8. 测试工具调用
```

## 故障排除

### 软链接权限问题

```powershell
# Windows 需要管理员权限或开发者模式
# 检查开发者模式是否开启
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" `
    -Name "AllowDevelopmentWithoutDevLicense"

# 如果值为 1，则无需管理员权限即可创建软链接
```

### 编辑器不识别配置

1. **检查文件路径**：确保软链接指向正确的目标
2. **重启编辑器**：配置更改后需要重启
3. **检查文件编码**：确保 UTF-8 无 BOM
4. **验证 YAML Frontmatter**：agents/skills 需要正确的 frontmatter

### 工具调用冲突

**症状**：编辑器中工具调用异常、响应延迟
**原因**：hooks 未正确跳过
**解决**：
1. 检查 `_editor_hook_launcher.py` 版本（应为 v3.0+）
2. 验证环境变量 `CLAUDE_HOOK_SKIP` 是否设置
3. 查看 launcher 检测日志

## 更新流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 在 ~/.claude/ 修改配置                                     │
├─────────────────────────────────────────────────────────────┤
│ 2. 本地测试（Claude Code）                                     │
│    - 验证 hooks 正常工作                                      │
│    - 确认 MCP 工具可用                                        │
├─────────────────────────────────────────────────────────────┤
│ 3. 运行 sync.ps1 同步到各编辑器                               │
│    - 软链接 CLAUDE.md                                        │
│    - 复制 rules/agents/skills                                │
├─────────────────────────────────────────────────────────────┤
│ 4. 在各编辑器中验证                                           │
│    - 检查规则是否加载                                        │
│    - 测试工具自动匹配                                        │
├─────────────────────────────────────────────────────────────┤
│ 5. 定期更新                                                   │
│    - 从参考仓库拉取最新配置                                   │
│    - 更新 skills 库                                           │
└─────────────────────────────────────────────────────────────┘
```

## 参考仓库

- [anthropics/skills](https://github.com/anthropics/skills) - Claude 官方技能
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 完整配置参考
- [obra/superpowers](https://github.com/obra/superpowers) - 多平台增强技能

---

_版本：v4.0 | 更新：2026-04-09_
