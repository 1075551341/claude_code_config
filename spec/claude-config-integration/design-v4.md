# Design v4.0 — 26 仓库全量整合

> 日期: 2026-05-27 | 五柱×五阶段×三层 | 基于 design-round3.md 增量

## 架构公式

```
RUNTIME = superpowers(methodology) + GSD(context) + OpenSpec(spec) + gstack(review) + claude-mem(memory)
STRUCTURE = ECC(manifest) + anthropics/skills(format) + best-practice(entry)
OPTIMIZATION = RTK(shell) + caveman(output)
REVIEW = gstack 5角色 + gstack 7补全
```

## 五柱声明（精确版本）

| 柱 | 来源 | 版本 | 职责 | 本地位置 |
|----|------|------|------|----------|
| Superpowers | obra/superpowers | 5.1.0 | 方法论 + P0 skill + HARD-GATE | plugins/cache/.../superpowers/5.1.0/skills/ |
| GSD | gsd-build/get-shit-done | latest | 上下文工程 + 三级阈值 + read-before-edit | rules/CONTEXT.md, templates/planning/ |
| OpenSpec | Fission-AI/OpenSpec | latest | 规格格式 proposal→spec→tasks | templates/openspec/, spec-validation |
| gstack | garrytan/gstack | latest | 角色审查 5+7 + 浏览器QA | agents/ (12个) |
| claude-mem | thedotmack/claude-mem | latest | 跨会话记忆 SSOT + 渐进式披露 | plugins/marketplaces/thedotmack/ |

---

## 执行计划 — 七层顺序

### Layer 1: 骨架层

**CLAUDE.md** (≤300行):
- 五柱声明对齐各仓库最新 README
- 优先级链: `用户指令 > CLAUDE.md > plugin > skill > lazy rules > alwaysApply rules > default`
- 铁律新增: R12(子Agent隔离) R13(制品存活)
- 命令速查去重 GSD 已有命令

**SPEC.md**:
- 26仓库完整映射更新(补充遗漏: claude-code-action, github-mcp-server)
- 规模约束表刷新为实际数字
- 防互博速查扩展: plugin/hook 互斥场景
- Catalog 规模更新

**MANIFEST.yaml**:
- version: 4.0
- concerns 增加: plugin归属, deer-flow工作流, claude-code-action CI, claude-context
- 互斥声明扩展

**agent.yaml**:
- version: 4.0
- skills 分类对齐 anthropics/skills 最新格式

### Layer 2: 规则层 (rules/*)

**CORE.md**:
- Karpathy 四原则移至独立 skill，CORE.md 仅保留引用指针
- 新增 R12(子Agent隔离) R13(制品存活)
- 注释规则精简(去冗余模板)

**CONTEXT.md** (重点):
- 三级阈值精确化(<40%/50%/70%)
- 子Agent调度: DAG依赖图规则
- claude-context 启用条件更新
- 三态制品: openspec/ + .planning/ + memory/
- 长任务: 30分钟拆分为独立Agent

**WORKFLOW.md**:
- DAG编排四阶段(拆解→调度→整合→验证)确认完整
- 质量门: Schema Drift + Security Anchor + Scope Reduction
- 状态机: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
- 编排互斥: planner vs agentic-orchestrator 精确边界

**AGENTS.md**:
- 审查路由表对齐 gstack 最新 5+7
- 委派条件精确化
- 禁止项: agent间共享可变状态扩展场景

**SECURITY.md**:
- OS Sandbox 三层防御保持
- STRIDE 对齐 OWASP Agentic 2026
- 渐进硬化 Checklist 统一

**GIT.md / DESIGN.md / MCP.md / BESTPRACTICE.md / README.md**:
- 轻量增量更新，无结构性变化

### Layer 3: Agent 层 (agents/*)

| Agent | 变更点 |
|-------|--------|
| agentic-orchestrator | DAG依赖调度规则 |
| context-manager | 三态制品感知 |
| security-reviewer | STRIDE 2026 威胁模型 |
| release-engineer | CI模板引用 |
| 其余16个 | 格式确认 |

### Layer 4: Hook 层 (hooks/*)

| Hook | 变更点 |
|------|--------|
| pre-manifest-validator | plugin vs skill 互斥检查 |
| pre-context-injector | 三态制品加载 |
| stop-pattern-extraction | DAG执行模式提取 |
| pre-compact-state | openspec/ 状态快照 |
| 其余11个 | 逻辑确认 |

### Layer 5: Skill 层 (skills/*)

| Skill | 变更点 |
|-------|--------|
| brainstorming | 视觉伴侣路径更新 |
| writing-plans | 三轨选择逻辑增强 |
| subagent-driven-development | DAG调度替代平铺 |
| context-engineering | 三态制品管理 |
| caveman-compress | 四级压缩确认 |
| karpathy-guidelines | 从CORE.md独立完整化 |
| 其余 | 格式对齐 anthropics/skills |

### Layer 6: MCP 层

- .mcp.json: 增加 claude-context 可选
- mcp/servers.json: 分组增加 optional.claude-context

### Layer 7: 模板/目录层

- templates/openspec/: 对齐 OpenSpec 最新格式
- templates/planning/: 对齐 GSD 最新模板
- templates/github-actions/: 补充 claude-code-action 模板
- catalog/: 索引更新

---

## 执行约束

- 只做必要变更，对比差异不重写
- 保留所有现有优点
- 每层独立 commit，可单独回滚
- 每次修改后 MANIFEST.yaml 验证归属
- 不突破规模上限

## 规模上限

| 类型 | 上限 | 目标 |
|------|------|------|
| skills | ≤28 | 27 |
| agents | ≤22 | 20 |
| rules | 10 | 10 |
| CLAUDE.md | ≤300行 | ~250 |
| hooks | 15 | 15 |
