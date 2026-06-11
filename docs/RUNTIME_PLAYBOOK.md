---
description: 运行时 SSOT — 五阶段加载、调研三档、上下文治理、R16
---

# Runtime Playbook（v9.2）

> 加载等级详图 → [CLAUDE.md](../CLAUDE.md) L0–L4 | 路由 → [using-superpowers/SKILL.md](../skills/using-superpowers/SKILL.md)

## 任务入口

```
用户输入
  → R18: claude-mem search?（相关则先查）
  → L1 using-superpowers 分类
  → 简单(≤3文件)? → L1 change-impact → 改 → 轻量验证
  → Bug? → L3 triage → L2 systematic-debugging
  → 非简单 → L2 brainstorming → 五阶段全链
```

**简单旁路**：不 Read `executing-plans` / `subagent-driven-development`。

## 非简单五阶段（L2 门控 Read）

| 阶段 | 命令 | 强制 Read | 规划内嵌（①） |
|------|------|-----------|---------------|
| ① 规划 | /discuss | brainstorming | codegraph；调研 L1–L3；adr |
| ② 规格 | /plan | writing-plans → spec-validation | 三轨判定 |
| ③ 执行 | /execute | executing-plans + subagent-driven | — |
| ④ 验证 | /verify | verification-before-completion | — |
| ⑤ 学习 | /compact | — | claude-mem pattern |

### brainstorming 纪律

- **Relentless interview**：沿设计树逐枝澄清，一次一问
- **每个问题附带推荐答案**
- **HARD-GATE**：用户书面批准前禁止实现

### 门控

| 转换 | 条件 | 失败 |
|------|------|------|
| ①→② | 用户批准设计 | 回到 ① |
| ②→③ | spec-validation 通过 | BLOCKED，禁止 execute |
| ③→④ | 构建/类型/lint 通过 | BLOCKED + R16 |
| ④→⑤ | verification 清单全绿 | DONE_WITH_CONCERNS 需说明 |

## 调研三档（① 内嵌或显式）

**前置**：claude-mem search → 项目内代码用 codegraph（禁止先用 Firecrawl 探本地代码）。

| 档 | 场景 | 工具 | 验证 |
|----|------|------|------|
| L1 | 单点 API/事实 | Context7 / Exa 单次 | 1 权威源 |
| L2 | 方案对比 | Exa + Firecrawl 单页 | ≥2 源 |
| L3 | /deep-research、选型 | Read deep-research + Firecrawl + Exa + Context7 | ≥2 独立源；矛盾显式列出 |

**升级**：L1 不足 → L2 → L3。禁止无因跳级（除非用户 `/deep-research`）。

## 代码探索（R17）

```
codegraph_explore / impact  →  Grep 精确定位  →  Read 补洞
```

禁止未探索就大范围 Read。UA 仅在 codegraph 不足时 L3 升级。

## 上下文治理

| 使用率 | Cursor | Claude Code |
|--------|--------|-------------|
| <70% | 正常 | 正常 |
| 70% | `/summarize` | `/compact` |
| 90% | 强制摘要或新子 Agent | 同上 |

⛔ 绝不允许 100%。

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

| 能力 | Claude Code | Cursor |
|------|-------------|--------|
| 代码探索 | codegraph MCP | user-codegraph |
| 网页调研 | crawl MCP | firecrawl skill / user-crawl |
| 搜索 | — | plugin Exa |
| 文档 | — | plugin Context7 |
| GitHub | git MCP | user-gh |

详见 [CURSOR_MCP_PROFILE.md](CURSOR_MCP_PROFILE.md)、[TOOL_MATCHING_GUIDE.md](TOOL_MATCHING_GUIDE.md)。
