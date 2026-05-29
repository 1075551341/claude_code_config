---
description: 跨编辑器配置同步指南
---

# Claude 配置跨编辑器同步指南

> **目的**：将 `~/.claude` 配置通过软链接同步到 Cursor、Windsurf、Trae 等编辑器，确保跨编辑器体验一致且安全。

## 配置结构

```text
~/.claude/                    # 主配置目录（仅 Claude Code 使用完整功能）
├── CLAUDE.md                 # ✅ 同步 - 文件软链接（v11）
├── AGENTS.md                 # ✅ 同步 - 跨编辑器 autodiscovery 镜像
├── rules/                    # ✅ 同步 - 格式转换复制到编辑器原生规则目录
│   ├── CORE.md               #     核心规则（alwaysApply，skeleton）
│   ├── BESTPRACTICE.md       #     配置最佳实践（alwaysApply，skeleton）
│   ├── SECURITY.md           #     安全规则（supplement）
│   └── ...（共 9 文件）
├── agents/                   # ✅ 同步 - Agent 定义（目录链接，含 gstack 5 角色）
│   ├── eng-reviewer.md       #     gstack 工程审查
│   ├── ceo-reviewer.md       #     gstack CEO 审查
│   ├── designer.md           #     gstack 设计审查
│   ├── qa.md                 #     gstack QA 审查
│   ├── security-reviewer.md  #     gstack 安全审查
│   └── ...（core 8 + gstack 12，共 20）
├── skills/                   # ✅ 同步 - 技能库（目录链接）
├── commands/                 # ❌ 不同步 - Claude Code 专用
├── hooks/                    # ❌ 不同步 - Claude Code 专用
├── .mcp.json                 # ❌ 不同步 - 各编辑器独立配置
├── settings.json             # ❌ 不同步 - Claude Code 专用
├── .claude.json              # ❌ 不同步 - Claude Code 专用
├── TOOL_MATCHING_GUIDE.md    # ❌ 不同步 - 各编辑器独立
├── SYNC_GUIDE.md             # ❌ 不同步 - 各编辑器独立
└── scripts/sync.ps1          # 🚀 Windows 同步脚本
```

## 同步策略

### ✅ 完全同步项

| 目录/文件 | 同步方式 | 目标位置 | 说明 |
|-----------|---------|---------|------|
| `CLAUDE.md` | 文件链接 | 各编辑器根目录 | 路由层入口，SSOT |
| `AGENTS.md` | 文件链接 | 各编辑器根目录 | autodiscovery 镜像 |
| `skills/` | 目录链接 | 各编辑器目录 | 技能库 |
| `agents/` | 目录链接 | 各编辑器目录 | Agent 定义 |
| `rules/*.md` | 格式转换复制 | 各编辑器原生规则目录 | Cursor `.mdc` / Windsurf `.md` / Trae `user_rules/` |

### ❌ 不同步项（Claude Code 专用或各编辑器独立）

| 文件 | 原因 | 风险说明 |
|------|------|---------|
| `commands/` | 各编辑器 slash 命令格式不同 | 避免兼容性问题 |
| `TOOL_MATCHING_GUIDE.md` | 编辑器无关 | 无需同步 |
| `SYNC_GUIDE.md` | 编辑器无关 | 无需同步 |
| `hooks/` | 防止干扰编辑器内模型调用 | **高风险**：Hooks 在编辑器中运行可能导致无限循环、响应延迟、工具调用冲突 |
| `.mcp.json` | 各编辑器 MCP 配置格式不同 | Cursor/Windsurf 使用不同的 MCP 配置格式 |
| `settings.json` | 包含 Claude Code 专属设置 | 包含 hooks 配置、权限设置等编辑器不支持的选项 |
| `.claude.json` | Claude Code 状态文件 | 编辑器无法识别 |
| `scripts/sync.ps1` | 仅在主环境使用 | 无需同步 |

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

**配置路径**：`~/.windsurf/`（项目级规则）+ `~/.codeium/windsurf/memories/global_rules.md`（全局规则，6000字符限制）

```powershell
# 1. 创建目录
mkdir -Force "$env:USERPROFILE\.windsurf\rules"

# 2. 复制 CLAUDE.md（完整版；Windsurf 会通过脚本自动处理 global_rules.md）
Copy-Item "$env:USERPROFILE\.claude\CLAUDE.md" `
    -Destination "$env:USERPROFILE\.windsurf\CLAUDE.md" -Force

# 3. 复制 rules（项目级）
Copy-Item "$env:USERPROFILE\.claude\rules\*.md" `
    -Destination "$env:USERPROFILE\.windsurf\rules\" -Force
```

**Windsurf global_rules.md 策略**：
- 优先写入完整 `CLAUDE.md`
- 若超过 6000 字符限制：自动生成精简速查（仅含铁律、文件落点、工具优先），不注入 `rules/` 内容
- 完整规则请查看 `~/.claude/CLAUDE.md` 与 `~/.claude/SPEC.md`

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

### _editor_hook_launcher.py v2.0

Hooks 经 launcher 调用；主判定 **GetConsoleWindow()**（Windows 无控制台 = 编辑器 → 跳过）。

**检测优先级**：
1. **环境变量**
   - `CLAUDE_HOOK_SKIP=1` - 强制跳过
   - `CLAUDE_HOOK_FORCE_CLI=1` - 强制执行

2. **控制台检测**（Windows，主判定）
   - `GetConsoleWindow() == 0` → 无控制台 → 编辑器环境 → 跳过

3. **stdin / 路径 / 父进程链**（补充判定）
   - 工作目录含 `.cursor/`、`.windsurf/` 等
   - 父进程含 cursor/windsurf/trae 可执行名

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
~/.claude/scripts/sync.ps1

# 功能
- [✓] 链接 CLAUDE.md、AGENTS.md、skills/、agents/
- [✓] 格式转换复制 rules/ 到各编辑器原生规则目录
- [✗] 排除 hooks/ scripts/（安全保护）
- [✗] 排除 commands/ MCP配置（各编辑器独立）
- [✓] 创建备份
- [✓] 生成同步报告
```

**完整参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-DryRun` | 开关 | `$false` | 预览模式，不写入文件，仅输出变更报告 |
| `-FormatConvert` | 开关 | `$false` | 启用格式转换（移除 `_comment`/`_note`/hooks 等 Claude 专用字段） |
| `-Rollback` | 开关 | `$false` | 回滚到上次同步的备份 |
| `-Editors` | string[] | `@('Cursor','Windsurf','Trae')` | 指定目标编辑器，默认全部 |
| `-SkipBackup` | 开关 | `$false` | 跳过备份创建（加速同步） |
| `-Verbose` | 开关 | `$false` | 详细输出每个文件操作 |

**示例**：

```powershell
# 仅同步到 Cursor，预览模式
~/.claude/scripts/sync.ps1 -DryRun -Editors @('Cursor')

# 同步并转换格式，跳过备份
~/.claude/scripts/sync.ps1 -FormatConvert -SkipBackup

# 回滚 Windsurf 的配置
~/.claude/scripts/sync.ps1 -Rollback -Editors @('Windsurf')

# 详细输出
~/.claude/scripts/sync.ps1 -Verbose
```

### 手动同步检查清单

```markdown
□ 1. 备份现有配置
□ 2. 创建软链接（skills/、agents/）
□ 3. 复制并转换 rules/*.md 到编辑器原生规则目录
□ 4. 验证文件权限
□ 5. 重启编辑器
□ 6. 测试工具调用
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
1. 检查 `_editor_hook_launcher.py` 版本（应为 v2.0+，含 GetConsoleWindow）
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
│    - 目录链接 skills/ agents/                                 │
│    - 格式转换复制 rules/                                      │
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

## 格式转换（Claude Code → 编辑器）

### 使用 -FormatConvert 参数

```powershell
# 同步并转换格式
~/.claude/scripts/sync.ps1 -FormatConvert

# 转换但不写入（预览）
~/.claude/scripts/sync.ps1 -DryRun -FormatConvert
```

### 转换内容

| 源格式 | 目标格式 | 说明 |
|--------|---------|------|
| `_comment` 字段 | `//` 注释 | JSON 注释移除 |
| `_note` 字段 | `//` 注释 | JSON 注释移除 |
| `hooks` 配置 | 移除 | 编辑器不支持 |
| Claude 特定字段 | 清理/移除 | 保留通用配置 |

## 回滚操作

### 从备份恢复

```powershell
# 回滚到上次同步
~/.claude/scripts/sync.ps1 -Rollback

# 回滚（预览）
~/.claude/scripts/sync.ps1 -DryRun -Rollback
```

### 备份位置

```
~/.claude/backups/sync-YYYYMMDD-HHmmss/
├── Cursor/
├── Windsurf/
└── Trae/
```

## 参考仓库

- [anthropics/skills](https://github.com/anthropics/skills) - Claude 官方技能
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - 完整配置参考
- [obra/superpowers](https://github.com/obra/superpowers) - 多平台增强技能
- [deer-flow](https://github.com/bytedance/deer-flow) - 工作流模式
- [claude-context](https://github.com/zilliztech/claude-context) - 上下文管理
- [garrytan/gstack](https://github.com/garrytan/gstack) - 角色审查
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - 上下文工程
- [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) - 规格驱动
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) - 跨会话记忆

## 已知限制

1. **Windows 软链接需管理员/开发者模式**：非管理员需开启 Windows 开发者模式
2. **hooks 不同步**：编辑器中无 hook 执行环境，由 `_editor_hook_launcher.py` 自动检测跳过
3. **MCP 不同步**：各编辑器 MCP 配置格式不同，需独立配置
4. **rules 格式转换**：frontmatter 字段名可能不同（Claude: `alwaysApply` vs 编辑器: `autoApply`）
5. **catalog 不同步**：catalog/ 为领域能力库，仅在 Claude Code 环境可用
6. **SKILL.md 来源标注**：同步后 `source:` frontmatter 保留，编辑器忽略该字段
7. **软链接更新需重新同步**：源文件变更自动传播，但新增/删除文件需重新运行 sync.ps1

---

_版本：v7.3 | 更新：2026-05-28 | sync.ps1 v12.0_
