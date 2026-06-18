# 五柱骨架深度分析 v7.0

> 日期: 2026-06-07 | 基于 28 仓库全量 README 分析

---

## 五柱定义

```
Superpowers → 方法论: 如何构建软件 (HOW)
GSD         → 上下文工程: 如何管理 token/上下文 (CONTEXT)
OpenSpec    → 规格格式: 如何定义"完成" (WHAT)
gstack      → 角色 Agent: 如何分工协作 (WHO)
claude-mem  → 跨会话记忆: 如何延续上下文 (MEMORY)
```

---

## Pillar 1: Superpowers — 方法论引擎

### 为什么是骨架
Superpowers 提供了**完整的开发方法论流程** — 不是零散的工具集合，而是从需求到交付的完整链。

### 核心流程链
```
brainstorming (HARD-GATE 用户批准)
  → using-git-worktrees (隔离工作空间)
    → writing-plans (2-5min 原子任务)
      → subagent-driven-development (fresh context 执行)
        → test-driven-development (RED-GREEN-REFACTOR)
          → requesting-code-review (两阶段审查: spec + 质量)
            → finishing-a-development-branch (merge/PR/discard)
```

### 哪些应该被吸收
1. **HARD-GATE 模式**: 非简单任务必须先设计审批
2. **两阶段审查**: spec 合规 + 代码质量
3. **原子任务 (2-5min)**: writing-plans 输出精确到文件路径、完整代码、验证步骤
4. **子 agent 隔离**: 每个任务 fresh context
5. **自动技能触发**: 骨架层 skill (brainstorming, verification-before-completion, systematic-debugging)

### 哪些不重复吸收（已有）
- 本地 skills/ 已有 13 个同名 skill（精简版覆盖完整版）
- 触发机制已通过 SessionStart hook 实现
- Subagent 编排已有 deer-flow/agentic-orchestrator

---

## Pillar 2: GSD (get-shit-done) — 上下文工程

### 为什么是骨架
GSD 提供了**上下文管理的第一性原理** — 上下文是最稀缺的资源，管理好上下文比写好代码更重要。

### 核心概念
1. **三级阈值**: <40% 正常 / 50% compact / 70% 强制压缩
2. **三态制品通信**: openspec/ + .planning/ + memory/
3. **DAG 编排**: 无依赖并行，有依赖等待
4. **Trust-But-Verify**: Agent 自述不可信，API 直接验证
5. **Canonical Source Precedence**: 规范文档 > ADR > 制品 > Agent 记忆
6. **Read-Before-Edit**: 编辑前必须 Read

### 当前落地状态
- ✅ rules/CONTEXT.md: 三级阈值 + DAG + 制品
- ✅ rules/CORE.md: 阈值简表
- ✅ hooks/: pre-compact-state, pre-context-injector, pre-read-before-edit
- ⚠️ GSD 原仓库已归档，新家 open-gsd/gsd-core

### 建议增强
- Trust-But-Verify 机制显式化到 pre-manifest-validator
- Canonical Source 引用链显式化到 subagent prompt 模板

---

## Pillar 3: OpenSpec — 规格格式

### 为什么是骨架
OpenSpec 提供了**规格的标准化格式** — 人和 AI 在写代码前对齐期望。

### 核心工作流
```
/opsx:propose → proposal.md + specs/ + design.md + tasks.md
/opsx:apply   → 逐任务实现
/opsx:archive → 归档 + spec 更新
```

### 关键设计决策
- **brownfield 优先**: 不像 Spec Kit 假设 greenfield
- **fluid not rigid**: 无刚性阶段门禁
- **变更级隔离**: 每个 change 独立文件夹
- **25+ AI 工具**: 不锁定平台

### 当前落地状态
- ✅ spec/ 目录
- ✅ spec-validation skill
- ✅ 三轨规格 (OpenSpec / GSD Redux / 轻量)
- ⚠️ opsx CLI 未安装 (可选)

### 建议增强
- 安装 @fission-ai/openspec CLI 获得 opsx 命令
- 集成 opsx archive 机制到 stop-quality-gate

---

## Pillar 4: gstack — 角色 Agent 工厂

### 为什么是骨架
gstack 提供了**完整的虚拟工程团队** — 23 个专业角色覆盖从规划到发布的完整 Sprint。

### 角色分层

**必须 (每次变更)**:
- `/review` (Staff Engineer) — 发现生产级 bug
- `/cso` (Chief Security Officer) — OWASP + STRIDE

**条件触发**:
- 产品/新功能 → `/office-hours` + `/plan-ceo-review` + `/plan-eng-review`
- UI/UX → `/design-review` + `/design-shotgun`
- 发布 → `/ship` + `/canary`
- 调试 → `/investigate`

### 独有优势
- **品味记忆**: 学习用户 UI 偏好
- **ML 注入防御**: 三层防护
- **多 Agent 浏览器共享**: `/pair-agent`
- **Sprint 流程**: Think→Plan→Build→Review→Test→Ship→Reflect

### 当前落地状态
- ✅ agents/ 目录: 22 个 agent (eng-reviewer, ceo-reviewer, designer, qa, security-reviewer 等)
- ✅ 审查路由规则 (AGENTS.md)
- ⚠️ gstack 部分角色本地 agent 未覆盖: design-shotgun, pair-agent, land-and-deploy

### 建议增强
- 补充 gstack 独有角色到 agents/: design-shotgun, pair-agent, land-and-deploy
- 集成 gstack 品味记忆机制

---

## Pillar 5: claude-mem — 跨会话记忆

### 为什么是骨架
claude-mem 提供了**跨会话知识持续性** — 项目上下文不因会话结束而丢失。

### 三层搜索 (~10x token 节省)
```
search (compact index) → timeline (context) → get_observations (full detail)
```

### 核心特性
- **自动捕获**: 无需手动操作
- **渐进式披露**: 先索引后详情
- **Web Viewer**: http://localhost:37777
- **隐私控制**: `<private>` 标签
- **Endless Mode**: 仿生记忆架构

### 当前落地状态
- ✅ 已安装为 plugin
- ✅ MCP tools: search_nodes, read_graph, open_nodes, add_observations 等
- ✅ SessionStart hook 注入

### 建议增强
- 启用 Chroma 向量搜索 (当前可能未开启)
- 配置 Endless Mode (长会话场景)

---

## 五柱协同矩阵

```
         ┌──────────┐
         │  需求输入  │
         └─────┬────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐
│OpenSpec│ │GSD   │ │Superpowers│
│  WHAT  │ │CTX   │ │   HOW     │
└───┬────┘ └──┬───┘ └─────┬─────┘
    │         │            │
    └─────────┼────────────┘
              │ 规格 + 上下文 + 方法
              ▼
    ┌─────────────────────┐
    │   gstack 角色工厂    │
    │   WHO: 审查/测试/安全 │
    └──────────┬──────────┘
               │ 验证通过
               ▼
    ┌─────────────────────┐
    │   claude-mem 持久化  │
    │   MEMORY: 跨会话继承  │
    └─────────────────────┘
```

## 架构约束

```
五柱:
  - 每个柱子解决一个独立维度
  - 柱子间通过三态制品通信（不通过对话历史）
  - 禁止柱子间功能重叠

横切:
  - L1 治理: ECC MANIFEST 防止 agent 互博 + deer-flow DAG 编排
  - L2 优化: RTK shell + caveman 输出 + 三级阈值
  - L3 洞察: codegraph 静态 + UA 交互 + Firecrawl/Exa 外部
```

---

## 与业界其他框架对比

| 维度 | 五柱架构 | Spec Kit (GitHub) | BMAD | Kiro (AWS) |
|------|----------|-------------------|------|------------|
| 方法论 | Superpowers (完整链) | 规格驱动 | Agent 驱动 | IDE 内置 |
| 上下文 | GSD (三级阈值) | 无显式管理 | 无 | 黑盒 |
| 规格 | OpenSpec (fluid) | 刚性门禁 | 无标准 | 内置 |
| 审查 | gstack (23 角色) | 依赖 PR | 有限 | IDE 内 |
| 记忆 | claude-mem (渐进式) | 无 | 无 | 会话级 |
| 平台 | 25+ AI 工具 | GitHub 生态 | 平台限定 | 仅 Kiro IDE |
| 开源性 | 完全开源 | 开源 | 闭源/有限 | 闭源 |

**结论**: 五柱架构是唯一覆盖 [方法论 + 上下文 + 规格 + 审查 + 记忆] 全维度的开源方案。
