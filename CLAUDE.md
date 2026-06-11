---
description: 
alwaysApply: true
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 路由→`SPEC.md` | 归属→`MANIFEST.yaml` | **v9.2**

**五柱**：Superpowers(方法论) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)
**三横切**：L1 ECC+deer-flow | L2 RTK+caveman+阈值 | L3 codegraph+UA+Firecrawl/Exa

---

## 优先级链

```
用户显式指令 > CLAUDE.md > 激活skill > lazy规则 > alwaysApply > 默认
工具路由: codegraph_explore > Grep | claude-mem search > 重复Read
```

---

## 五阶段

```
简单(≤3文件) → L1 change-impact → 执行 → 轻量验证
Bug → triage → L2 debugging
非简单 → ①规划 → ②规格 → ③执行 → ④验证 → ⑤学习
```

<HARD-GATE>用户批准设计前禁止实现 → Read skill/brainstorming</HARD-GATE>

**SDD+TDD**：spec→writing-plans(原子)→subagent(两阶段审查)→verify | RED→GREEN→REFACTOR

---

## 铁律 R1–R18

| # | 约束 | 核心 |
|---|------|------|
| R1 | 任务完成 | 验证通过才算完成 |
| R2 | 修改确认 | Read→Edit→Read |
| R3 | Bug修复 | Grep全修→确认 |
| R4 | 配置变更 | Grep引用→构建 |
| R5 | 重试上限 | 同方案≤2次 |
| — | 变更彻底 | 改前codegraph_impact+Grep；改后残留→CORE.md |
| R6 | 非简单 | ①→⑤全流程 |
| R7 | 交叉验证 | 完成前验证清单 |
| R8 | 高危确认 | 删数据/强推main前确认 |
| R9 | 命令安全 | 禁cd+重定向/powershell -Command |
| R10 | 简洁优先 | 高内聚低耦合 |
| R11 | 安全默认 | 不信任输入、无硬编码密钥 |
| R12 | 子Agent隔离 | fresh context+制品通信 |
| R13 | 制品存活 | 跨会话持久化 |
| R14 | 版本克制 | 非必要不升major |
| R15 | 包管理器 | pnpm优先；npm兜底 |
| R16 | 错误暴漏 | 禁止裸except:pass |
| R17 | 代码探索 | codegraph_explore首选→Grep |
| R18 | 记忆优先 | claude-mem先于重复分析 |

> R12–R18 扩展、变更三阶段、编码规范 → `rules/CORE.md` | Karpathy → skill/karpathy-guidelines

---

## 加载等级 L0–L4

| 等级 | 内容 | 机制 |
|------|------|------|
| L0 | CLAUDE-ROUTER + CLAUDE + CORE | alwaysApply |
| L1 | using-superpowers, change-impact-analysis | 会话常驻；修改时 Read change-impact 全文 |
| L2 | 阶段 skill（见下表） | 进入阶段 Read 全文；同会话不重复 Read |
| L3 | supplement skills / lazy rules | slash、关键词、路由后 Read |
| L4 | agents(Task)、MCP、claude-mem | 显式调用 |

### P0 路由集（5）= L1×2 + L2 门控×3

| Skill | 等级 | 触发 |
|-------|------|------|
| using-superpowers | L1 | 会话开始、分类路由 |
| change-impact-analysis | L1 | 任何修改/变更 |
| brainstorming | L2 | 非简单、方案、架构（HARD-GATE） |
| verification-before-completion | L2 | 完成、验收、ship |
| systematic-debugging | L2 | 调试、测试失败 |

非简单 ② 追加 L2：writing-plans → spec-validation（门控）→ executing-plans + subagent-driven-development

### 调研三档（①内嵌或显式）

| 档 | 场景 | 工具 |
|----|------|------|
| L1 | 单点事实、API | Context7 / Exa 单次 |
| L2 | 方案对比、最佳实践 | Exa + Firecrawl 单页 |
| L3 | 深度选型、/deep-research | skills/deep-research + Firecrawl + Exa 双源 |

代码探索：**codegraph > UA > Read**（禁止未探索大范围 Read）

### 规格三轨（自动判定，互斥）

`/workstream`→GSD | `openspec/changes/` 或 brownfield→OpenSpec | ≤3 文件→轻量 `spec/` | 默认>3 文件→OpenSpec

---

## Tool-First 路由

```
MANIFEST → P0路由集 → 全局 skill → catalog → agent → MCP
```

**五轨**：codegraph(R17) | UA全貌 | Context7 | Firecrawl+Exa | claude-mem(R18)
**Token**：RTK(shell) + caveman(输出) + codegraph(探索)
**阈值**：<70%正常 | 70%压缩 | 90%强制 | ⛔100%
**压缩**：Cursor→`/summarize`；Claude Code→`/compact`（见 CORE）

---

## 审查路由

```
所有变更→eng-reviewer | 产品→+ceo | UI/UX→+designer+dx-reviewer
安全→+security-reviewer | iOS→+ios-specialist | 跨模型→+codex-reviewer
```

---

## 命令速查

| 命令 | 阶段 | 作用 |
|------|------|------|
| /discuss /plan /execute /verify /ship | ①-⑤ | 五阶段 |
| /deep-research | 调研 L3 | Firecrawl+Exa |
| /deer-flow | L3 | 外部编排（>30min 自主任务） |
| /workstream | GSD | 并行任务流 |
| /adr | ① | 架构决策 |

---

## 指针

| 内容 | 位置 |
|------|------|
| 法典/插件/加载 | SPEC.md (v9.1) |
| 加载等级详图 | spec/claude-config-integration/plan-v9.1-token-loading.md |
| 铁律/阶段/编码 | rules/CORE.md |
| 工作流 | rules/WORKFLOW.md |
| 同步 | docs/SYNC_GUIDE.md |
| MCP | docs/TOOL_MATCHING_GUIDE.md, docs/CURSOR_MCP_PROFILE.md |
| Git/PR 流程 | skills/git-workflow, skills/pr-workflow |

**插件**：~/.claude 15启用；Cursor 禁用 compound-engineering（与本地 agents 重叠）。
**同步**：`scripts/sync.ps1` 软链 skills/agents/rules；hooks/MCP/plugins 不同步。

@RTK.md
