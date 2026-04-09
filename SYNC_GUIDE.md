---
description: 跨编辑器配置同步指南
---

# Claude 配置跨编辑器同步指南

## 配置结构

```text
~/.claude/
├── CLAUDE.md           # ✅ 同步 - 核心规则
├── rules/              # ✅ 同步 - 各类规则文件
├── agents/             # ✅ 同步 - 智能体定义
├── skills/             # ✅ 同步 - 技能库
├── hooks/              # ❌ 不同步 - Claude Code 专用
├── .mcp.json           # ❌ 不同步 - 各编辑器独立配置
├── .claude.json        # ❌ 不同步 - Claude Code 专用
└── experiences/        # ⚠️ 可选 - 经验记录
```


## 同步策略

### 完全同步项（rules/, agents/, skills/, CLAUDE.md）

这些文件使用标准 Markdown + YAML Frontmatter 格式，兼容：
- ✅ Claude Desktop (Projects)
- ✅ Cursor (.cursorrules)
- ✅ Windsurf (.windsurfrules)
- ✅ Trae / Qoder
- ✅ GitHub Copilot

### 不同步项

| 文件 | 原因 |
|------|------|
| hooks/ | 防止干扰编辑器内模型调用逻辑 |
| .mcp.json | 各编辑器 MCP 配置格式不同 |
| .claude.json | Claude Code 专用设置 |
| sync.ps1 | 同步脚本本身只在主环境使用 |


## 各编辑器配置方式

### Claude Code (主环境)

```bash
# 原生支持 ~/.claude 目录
claude config set allowNestedBashCommands true
```

### Cursor
1. 打开 Settings → Rules for AI
2. 添加 `.cursorrules` 文件（CLAUDE.md + rules/ 合并）

### Windsurf
1. 创建 .windsurfrules 文件
2. 内容 = CLAUDE.md + 合并后的 rules/

### Trae / Qoder
1. 设置  AI 规则
2. 导入 CLAUDE.md 和 rules/

## 编辑器检测机制

_editor_hook_launcher.py 会自动检测运行环境：
- 检测到编辑器环境  跳过 hook 执行
- 纯 Claude Code CLI  正常执行 hooks

检测逻辑包括：
- 环境变量检查（VSCODE_PID, CURSOR_CHANNEL, WINDSURF_APP_VERSION）
- 进程链分析
- 工作目录检测

## 同步脚本使用

```powershell
# Windows
~/.claude/sync.ps1

# 功能
- 复制 rules/, agents/, skills/ 到各编辑器配置目录
- 合并 CLAUDE.md 到各编辑器规则文件
- 自动排除 hooks/ 和配置文件
- 保留备份
```

## 更新流程

1. 在 ~/.claude/ 修改配置
2. 运行 sync.ps1 同步到各编辑器
3. 重启编辑器生效
4. 定期从参考仓库拉取更新

---

_版本：v3.0 | 更新：2026-04-09_
