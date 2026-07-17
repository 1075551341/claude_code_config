---
description: 运行时 SSOT — 五阶段加载、调研三档、上下文治理、R16
---

# Runtime Playbook（v10.4）

> 加载等级详图 → [CLAUDE.md](../CLAUDE.md) L0–L3 | 路由 → [using-superpowers/SKILL.md](../skills/using-superpowers/SKILL.md)

## Git 禁令（v10）

Agent **禁止** `git stash`；**禁止自动** `git commit`（仅用户显式「提交」+ Guard 确认）。见 `rules/GIT.md`。

## 任务入口

```
用户输入
  → R18: claude-mem search?（相关则先查）
  → L1 using-superpowers 分类
  → 简单(≤3文件)? → L1 change-impact → 改 → 轻量验证
  → Bug? → L3 triage → L2 systematic-debugging
  → 非简单 → L1 brainstorming → 五阶段全链
```

**简单旁路**：不 Read `executing-plans` / `subagent-driven-development`。

## 非简单五阶段（L1 常驻 + L2 门控 Read）

| 阶段   | 命令     | 强制 Read                         | 规划内嵌（①）              |
| ------ | -------- | --------------------------------- | -------------------------- |
| ① 规划 | /discuss | brainstorming (L1)                | codegraph；调研 L1–L3；adr |
| ② 规格 | /plan    | writing-plans → spec-validation   | 三轨判定                   |
| ③ 执行 | /execute | executing-plans + subagent-driven | —                          |
| ④ 验证 | /verify  | verification-before-completion    | —                          |
| ⑤ 学习 | /compact | —                                 | claude-mem pattern         |

### brainstorming 纪律

- **Relentless interview**：沿设计树逐枝澄清，一次一问
- **每个问题附带推荐答案**
- **HARD-GATE**：用户书面批准前禁止实现

### 门控

| 转换 | 条件                  | 失败                      |
| ---- | --------------------- | ------------------------- |
| ①→②  | 用户批准设计          | 回到 ①                    |
| ②→③  | spec-validation 通过  | BLOCKED，禁止 execute     |
| ③→④  | 构建/类型/lint 通过   | BLOCKED + R16             |
| ④→⑤  | verification 清单全绿 | DONE_WITH_CONCERNS 需说明 |

## 调研三档（① 内嵌或显式）

**前置**：claude-mem search → 项目内代码：codegraph（R17）→ cbm L4（架构/ADR/变更，已启用时）→ Grep。禁止先用 Firecrawl 探本地代码。

| 档  | 场景                 | 工具                                            | 验证                    |
| --- | -------------------- | ----------------------------------------------- | ----------------------- |
| L1  | 单点 API/事实        | Context7 / Exa 单次                             | 1 权威源                |
| L2  | 方案对比             | Exa + Firecrawl 单页                            | ≥2 源                   |
| L3  | /deep-research、选型 | Read deep-research + Firecrawl + Exa + Context7 | ≥2 独立源；矛盾显式列出 |

**升级**：L1 不足 → L2 → L3。禁止无因跳级（除非用户 `/deep-research`）。

## 代码探索（R17 + L4 双引擎）

```
codegraph init（首次/新项目）
  → codegraph_explore / blast-radius / impact
  →（L4 已 merge）codebase-memory: get_architecture / detect_changes / manage_adr
  → Grep 精确定位
  → Read 补洞
```

未索引时 MCP 降级为 Grep；`validate_config.py` V16 检查 `~/.claude/.codegraph/` 就绪。

禁止未探索就大范围 Read。探索链：codegraph → cbm(L4) → Grep → Read（**UA removed v10.5**）。

### codegraph init（mandate — 全局 + 项目按需）

```bash
# 全局配置仓库（已 index）
cd ~/.claude && codegraph init && codegraph index

# 业务项目（按需，进入项目根后执行）
codegraph init && codegraph index

# 业务项目 L4 可选（merge optional-dev.json 或 .mcp.json 已含 cbm）：
# Windows: .\scripts\cbm-index.ps1 D:\your-project
# 或: npx -y codebase-memory-mcp@0.8.1 cli index_repository (Get-Content -Raw index.json)
```

**策略（访谈）**：mandate `~/.claude` 全局索引；各业务仓库按需 init；cbm 见 `rules/CONTEXT.md` 启用条件。

## 上下文治理

| 使用率 | Cursor               | Claude Code |
| ------ | -------------------- | ----------- |
| <70%   | 正常                 | 正常        |
| 70%    | `/summarize`         | `/compact`  |
| 90%    | 强制摘要或新子 Agent | 同上        |

**GSD 逻辑断点 70%**：完成原子任务 / 切换子 Agent / 写制品 — 不替代上表压缩。

⛔ 绝不允许 100%。

**Claude Code auto-compact**（模型感知，不写死窗口）：

| 键                                          | 说明                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------- |
| `config/model-context-windows.json`         | 模型/后缀 → token 映射 SSOT；可扩展新模型                               |
| `autoCompactWindow`                         | 由 `scripts/sync-compact-window.py` 或 SessionStart 按当前 `model` 同步 |
| `env.CLAUDE_CODE_MAX_CONTEXT_TOKENS`        | 可选：强制覆盖模型最大窗口（路由非标准模型时）                          |
| `env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`       | `"70"` — 70% 触发原生自动 `/compact`（提质；hook 仍 90% 强制提醒）      |
| `env.CLAUDE_COMPACT_WARN_PCT` / `FORCE_PCT` | hook 70% / 90%                                                          |

⛔ 勿在 `env` 写死 `CLAUDE_CODE_AUTO_COMPACT_WINDOW`；勿设 `autoCompactWindow` 超过模型支持值。

Hook SSOT：`hooks/_lib/context_thresholds.py`。换模型后：`python scripts/sync-compact-window.py` 或重启会话。

Cursor 侧独立：`templates/cursor-guard/guard-config.json`（`window_tokens` 默认 200K）。

修改后需 **完全重启** Claude Code。HUD 与 `until auto-compact` 应基于同一解析窗口。

**制品跨会话**：`session-digest.md`、`.planning/`、`openspec/changes/` — 新会话 `@` 引用。

## 错误暴露（R16）

门控/执行失败输出：

```
BLOCKED | 原因 | 已尝试 | 建议下一步
```

- 禁止裸 `except:pass`（hooks V10 扫描）
- 禁止静默缩 scope
- 子 Agent 异常：主 Agent 决定重试/报告/中止

## 双平台工具

| 能力           | Claude Code              | Cursor                       |
| -------------- | ------------------------ | ---------------------------- |
| 代码探索       | codegraph MCP            | user-codegraph               |
| 架构/ADR（L4） | codebase-memory optional | merge optional-dev 后        |
| 网页调研       | crawl MCP                | firecrawl skill / user-crawl |
| 搜索           | —                        | plugin Exa                   |
| 文档           | —                        | plugin Context7              |
| GitHub         | git MCP                  | user-gh                      |

详见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)、[TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md)。
