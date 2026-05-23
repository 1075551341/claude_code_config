# SPEC.md — 配置索引与溯源

> CLAUDE.md 为路由层（≤200 行）；本文件为法典索引。设计源：`spec/claude-config-integration/`

---

## PRIMARY 公式（五柱架构 v1.1）

```
RUNTIME = superpowers + ECC(cherry-pick) + anthropics/skills + best-practice + claude-mem
PROJECT = OpenSpec + GSD-redux + spec/轻量（三轨互斥）
OPTIMIZATION = RTK(hook) + caveman(skill)
REVIEW = gstack(eng/ceo/designer/qa/security agents)
CONTEXT = GSD(read-before-edit + <40%/50%/70% 三级阈值)
```

---

## 规模约束

| 类型 | 上限 | 当前 |
|------|------|------|
| 全局 skills | ≤20 | 17（13 workflow + 4 meta） |
| 全局 agents | ≤15 | 8 core |
| 全局 rules | 8 文件 | CORE/SECURITY/GIT/WORKFLOW/AGENTS/MCP/DESIGN + README |
| CLAUDE.md | ≤200 行 | 144 |

---

## P0 强制 Skill（4）

| Skill | 来源 | 触发 |
|-------|------|------|
| using-superpowers | obra/superpowers | 会话开始 |
| brainstorming | obra/superpowers | 方案/架构 |
| verification-before-completion | obra/superpowers | 完成/验收 |
| systematic-debugging | obra/superpowers | 调试/bug |

---

## Workflow Skills（13）

using-superpowers, brainstorming, writing-plans, executing-plans, verification-before-completion, systematic-debugging, test-driven-development, subagent-driven-development, using-git-worktrees, receiving-code-review, requesting-code-review, finishing-a-development-branch, writing-skills

来源：**obra/superpowers**

---

## Meta Skills（4）

| Skill | 来源 |
|-------|------|
| memory-compression | claude-mem + GSD-redux |
| spec-validation | Fission-AI/OpenSpec |
| karpathy-guidelines | forrestchang/andrej-karpathy-skills |
| caveman-compress | JuliusBrussee/caveman |

---

## 核心 Agents（8）

| Agent | 预加载 skills | 来源 |
|-------|---------------|------|
| planner | writing-plans | superpowers |
| code-explorer | — | ECC |
| code-reviewer | requesting/receiving-code-review | superpowers |
| build-error-resolver | systematic-debugging | ECC |
| architect | brainstorming | ECC |
| spec-reviewer | spec-validation | OpenSpec |
| context-manager | memory-compression, caveman-compress | claude-mem |
| agentic-orchestrator | subagent-driven-development | ECC |

领域 agent → `catalog/agents/`（按需复制到项目）

### gstack 审查角色（catalog/agents/）

| Agent | 触发 |
|-------|------|
| eng-reviewer | 所有变更（必须） |
| ceo-reviewer | 产品/新功能 |
| designer | UI/UX 变更 |
| qa | 测试充分性审查 |
| security | 安全敏感变更 |

---

## 全局 Rules（8）

| 文件 | 内容 | alwaysApply |
|------|------|-------------|
| CORE.md | 编码规范 + Karpathy 四原则 | ✅ |
| SECURITY.md | OWASP | lazy |
| GIT.md | 分支/Commit/PR | lazy |
| WORKFLOW.md | discuss→ship | lazy |
| AGENTS.md | 多 Agent 互斥 | lazy |
| MCP.md | .mcp.json 权威 | lazy |
| DESIGN.md | DESIGN.md 规范 | lazy |

语言/领域规则 → `catalog/rules/`（项目 lazy-load）

---

## 规格三轨

| 轨道 | 路径 | 模板 |
|------|------|------|
| OpenSpec | `openspec/changes/<id>/` | templates/openspec/ |
| GSD-redux | `.planning/phases/` | templates/planning/ |
| 轻量 | `spec/<project>/` | templates/spec/ |

决策树 → `spec/README.md`

---

## MCP 分组

| 分组 | 文件 | 服务器 |
|------|------|--------|
| core | mcp-configs/core.json | memory, thinking, fs, fetch, time |
| dev | mcp-configs/dev.json | gh, git, ctx7, pw, crawl, chrome-devtools |
| ops | mcp-configs/ops.json | redis, sqlite, docker, postgres, supabase |
| search | mcp-configs/search.json | brave, exa |
| collab | mcp-configs/collab.json | figma, linear, notion, slack |

完整分组 → `mcp/servers.json` | 权威 → `.mcp.json`

---

## Catalog（领域能力库）

| 目录 | 规模 | 用途 |
|------|------|------|
| catalog/skills/ | 97 | 按需 `migrate-from-legacy.py --skill` |
| catalog/agents/ | 43 | 按需 `--agent`（含 5 gstack 角色） |
| catalog/rules/ | ~15 | 按需 `--rule` |

优点保留在 catalog（97 skills / 43 agents）；已删记录 → `experiences/rejected/deletion-candidates.md`

---

## 归属与互斥

完整 concern → owner 映射 → `MANIFEST.yaml`

Harness 启用清单 → `agent.yaml`

---

## Hooks（Claude Code 专用，不同步编辑器）

| 事件 | Hook | 职责 |
|------|------|------|
| SessionStart | session-start-bootstrap | 唯一启动注入 |
| PreCompact | pre-compact-state | 压缩前快照 |
| PreToolUse/Bash | pre-rtk-rewrite → pre-bash-guard | RTK + 安全 |
| PreToolUse/Edit | pre-read-before-edit | GSD read-before-edit |
| PreToolUse/* | pre-context-injector | 项目上下文（每会话一次） |
| Stop | stop-quality-gate, stop-pattern-extraction | 质量门 + 模式提取 |

**已禁用（互博）**：hook/pre-task-planner → 由 skill/writing-plans + /plan 替代

Profile：`ECC_HOOK_PROFILE=minimal|standard|strict`（见 hooks/README.md）

目录：`hooks/`（standard 21 个）| `_optional/`（strict 27 个）| `_deprecated/`（已废弃 1 个）

---

## 防互博速查

| 场景 | Owner | 禁止 |
|------|-------|------|
| 计划 | writing-plans | pre-task-planner, planning-expert |
| 审查 | requesting/receiving-code-review | 独立 code-review skill |
| 记忆 | claude-mem plugin | memory MCP 作 SSOT |
| Shell token | pre-rtk-rewrite | skill 重复压缩 shell |
| 输出 token | caveman-compress | RTK 压缩 agent 文本 |

---

## 同步架构

| 同步 | 方式 |
|------|------|
| CLAUDE.md, AGENTS.md, skills/, agents/ | 软链接（sync.ps1 v11） |
| rules/ | 格式转换复制到编辑器原生目录 |
| hooks/, commands/, MCP | ❌ 不同步（Claude Code 专用） |

详见 `SYNC_GUIDE.md`

---

## 23 仓库映射

### 骨架 PRIMARY（五柱 + 基础）

| 仓库 | 采纳 |
|------|------|
| obra/superpowers | 13 workflow skills + P0 skills + commands |
| gsd-build/get-shit-done | planning 模板 + /compact + 上下文阈值 + read-before-edit |
| Fission-AI/OpenSpec | openspec 模板 + spec-validation skill |
| garrytan/gstack | 5 catalog agents (eng/ceo/designer/qa/security) + /review |
| thedotmack/claude-mem | memory plugin SSOT + 跨会话记忆 |

### 结构 + 格式

| 仓库 | 采纳 |
|------|------|
| affaan-m/ECC | 目录结构、MANIFEST、agents 薄编排、hook profile |
| anthropics/skills | SKILL.md 格式规范 |
| shanraisshan/claude-code-best-practice | CLAUDE.md ≤200 行、config 模式、rules lazy-load |
| forrestchang/andrej-karpathy-skills | karpathy-guidelines skill + CORE.md 四原则 |

### 优化 + 工具

| 仓库 | 采纳 |
|------|------|
| rtk-ai/rtk | pre-rtk-rewrite hook + RTK.md |
| JuliusBrussee/caveman | caveman-compress skill |
| github/github-mcp-server | gh MCP server |
| anthropics/claude-code-action | templates/github-actions/claude-review.yml |
| VoltAgent/awesome-design-md | DESIGN.md 模板 |
| nextlevelbuilder/ui-ux-pro-max | catalog/skills/ui-ux-pro-max |

### 参考索引

| 仓库 | 采纳 |
|------|------|
| eyaltoledano/claude-task-master | 任务分解模式参考（由 writing-plans + executing-plans 覆盖） |
| ComposioHQ/awesome-claude-skills | catalog skill 发现索引 |
| zilliztech/claude-context | 上下文管理策略参考（由 GSD 阈值覆盖） |
| hesreallyhim/awesome-claude-code | 配置最佳实践参考 |
| x1xhlol/system-prompts-and-models-of-ai-tools | 系统提示参考 |
| Chalarangelo/30-seconds-of-code | 代码片段参考 |
| bytedance/deer-flow | 子 Agent 编排四阶段模式（已整合到 WORKFLOW.md） |

---

## 验证命令

```powershell
python C:\Users\DELL\.claude\scripts\validate_config.py
powershell -ExecutionPolicy Bypass -File C:\Users\DELL\.claude\scripts\sync.ps1 -DryRun
(Get-Content C:\Users\DELL\.claude\CLAUDE.md).Count  # ≤200
```
