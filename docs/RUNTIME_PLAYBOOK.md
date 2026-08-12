---
description: 运行时 SSOT — 五阶段加载、调研三档、上下文治理、R16
---

# Runtime Playbook（v10.17.0）

> 加载等级详图 → [CLAUDE.md](../CLAUDE.md) L0–L3 | 路由 → [using-superpowers/SKILL.md](../skills/using-superpowers/SKILL.md)

## Git 禁令（v10）

Agent **禁止** `git stash`；**禁止自动** `git commit`（仅用户显式「提交」+ Guard 确认）。见 `rules/GIT.md`。

## 任务入口

```
用户输入
  → R18: claude-mem search?（相关则先查）
  → L1 using-superpowers + task-triage（Phase0 前置盘点）
  → 简单? → L1 change-impact → 一次改齐 → ④验证(比例)
      简单 = Phase0 已盘点 + 关联需改≤2 + 白名单 + 六维全低 + 模型匹配低 + attempt=1（缺一不可）
  → 持续处理(attempt≥2/首轮未解决)? → 执行升档非简单 + verify_tier=全量
  → 非简单 Bug(多文件/根因不明) → L3 triage → L2 systematic-debugging → 全量验证
  → 非简单 功能/架构/配置/删除 → grill 访谈(一次一问+推荐答案，≤5问)
        → L1 brainstorming(HARD-GATE) → 五阶段全链 → 全量验证
  → 非简单 调研 → deep-research（L3 双源）
```

> 判定条件与六维矩阵的唯一 SSOT 是 [skills/task-triage/SKILL.md](../skills/task-triage/SKILL.md)，本文件只做流程速查，**不复制矩阵正文**。

**简单旁路**：仅 attempt=1；不 Read `executing-plans` / `subagent-driven-development`；完成前仍须 verification（比例）。

## 非简单五阶段（L1 常驻 + L2 门控 Read）

| 阶段   | 命令     | 强制 Read                         | 规划内嵌（①）              |
| ------ | -------- | --------------------------------- | -------------------------- |
| ① 规划 | /discuss | grill 访谈 → brainstorming (L1)   | codegraph；调研 L1–L3；adr |
| ② 规格 | /plan    | writing-plans → spec-validation   | 三轨判定                   |
| ③ 执行 | /execute | executing-plans                   | subagent-driven **仅用户显式要求**（v10.15 默认关） |
| ④ 验证 | /verify  | verification-before-completion    | —                          |
| ⑤ 学习 | /compact | —                                 | claude-mem pattern         |

> **TDD/SDD 默认关闭（v10.15）**：仅用户显式要求（TDD/测试先行/子Agent派发）才 Read `test-driven-development` / `subagent-driven-development`；否则非简单任务由主会话按五阶段骨架直接执行。

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

**前置**：claude-mem search → 项目内代码：codegraph（R17）→ Grep。禁止先用 Firecrawl 探本地代码。（cbm 已禁用 v10.10+）

| 档  | 场景                 | 工具                                            | 验证                    |
| --- | -------------------- | ----------------------------------------------- | ----------------------- |
| L1  | 单点 API/事实        | Context7 / Exa 单次                             | 1 权威源                |
| L2  | 方案对比             | Exa + Firecrawl 单页                            | ≥2 源                   |
| L3  | /deep-research、选型 | Read deep-research + Firecrawl + Exa + Context7 | ≥2 独立源；矛盾显式列出 |

**升级**：L1 不足 → L2 → L3。禁止无因跳级（除非用户 `/deep-research`）。

## 代码探索（R17 单引擎 — cbm 已禁用 v10.10+）

```
codegraph init（首次/新项目）
  → codegraph_explore / blast-radius / impact
  → Grep 精确定位
  → Read 补洞
```

未索引时 MCP 降级为 Grep；`validate_config.py` V16 检查 `~/.claude/.codegraph/` 就绪。

禁止未探索就大范围 Read。探索链：codegraph → Grep → Read（**cbm 已禁用 v10.10+**；**UA removed v10.5**）。

### codegraph init（mandate — 全局 + 项目按需）

```bash
# 全局配置仓库（已 index）
cd ~/.claude && codegraph init && codegraph index

# 业务项目（按需，进入项目根后执行）
codegraph init && codegraph index

# codebase-memory 已禁用（全盘索引爆内存）；勿跑 cbm-index；仅实验可设 KG_SYNC_CBM=1
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

| 能力           | Claude Code                    | Cursor                             |
| -------------- | ------------------------------ | ---------------------------------- |
| 代码探索       | codegraph MCP                  | user-codegraph                     |
| 架构/ADR       | codegraph_explore              | 同左（cbm 已禁用）                 |
| 变更后审查     | code-review-graph MCP          | user-code-review-graph             |
| 符号级编辑     | serena MCP                     | user-serena                        |
| 网页调研       | firecrawl MCP                  | user-firecrawl / firecrawl skill   |
| 搜索           | exa MCP                        | Exa **plugin**（勿双挂 mcp 条目）  |
| 文档           | context7 MCP                   | user-context7                      |
| 跨仓代码搜索   | grep MCP                       | user-grep                          |
| GitHub         | github MCP（官方远端）/ `gh`   | user-github                        |
| 浏览器         | playwright **插件**            | 内置 `cursor-ide-browser`          |

详见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)、[TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md)。
