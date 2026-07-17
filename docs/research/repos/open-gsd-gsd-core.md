# open-gsd/gsd-core v1.4.5 (本地锁定) --> v1.6.0 (上游)

> 层: 五柱(GSD) | 置信度: 高 | 刷新: 2026-06-26 | 来源: GitHub Releases + CHANGELOG + npm

## v10.5 delta (2026-07-17)

- **最新元数据**：6,729 stars；GitHub Release **v1.7.0**；`pushed_at` 2026-07-17T01:26:16Z。
- **自 2026-06-29 的变化**：从 v1.6.0 升至 v1.7.0，存在新的上游版本漂移；本卡现有材料未证明其已消除 capability registry / Research module 与本地 MANIFEST、调研链的互博风险。
- **本地吸收**：不变——继续 Stay 1.4.5，v1.7.0 仅跟踪，任何跨 minor 升级仍需独立 ADR 与用户确认。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 CHANGELOG 研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：6,735★；Release **v1.7.0**（2026-07-15）；`pushed_at` 2026-07-17T01:26:16Z。
- **漂移要点**：ADR-1239 Embeddable Orchestration System（多 runtime EoS）；Windows 可移植性 AST 规则；`/gsd:next`、brownfield onboarding、assumption-delta；CLI version-skew 警告。
- **本地吸收 / 缺口**：钉 **1.4.5** 概念（阈值/制品/子 Agent）；升 1.7 待评估。已有：三级阈值、CONTEXT 制品、workstream。
- **不吸收**：全量 EoS 多 runtime 安装面、GSD 专属 MCP companion、MemPalace 后端替换本地 claude-mem。
- **双源**：GitHub API + Firecrawl（v1.7.0 release）。
## 核心价值

GSD (Get-Shit-Done) Redux 是一套**上下文工程方法论**，核心理念：上下文腐烂是AI开发的第一大故障模式，必须通过工程纪律系统化治理。

### 五大上下文工程原则

| 原则 | 说明 |
|------|------|
| **Fresh-Context Subagents** | 每个子Agent独立200K token窗口，Controller仅编排 |
| **Artifact-First** | 制品（文件）优先于对话历史；新会话首先加载制品 |
| **Canonical Source Precedence** | CONTRIBUTING.md/CLAUDE.md/ADR逐字引用，不可凭记忆转述 |
| **Trust-But-Verify** | Agent自述不可信，必须通过API/命令直接验证 |
| **Meta-Prompting** | 指令优先于Agent自主判断 |

### 上下文腐烂三级阈值

| 使用率 | 状态 | 行动 |
|--------|------|------|
| <60% | 正常 | 继续工作 |
| 60% | WARNING | 通过 lifecycle hooks (PreCompact, Stop, SubagentStop) 触发提醒 |
| 70% | CRITICAL | 强制压缩或新子Agent；GSD 逻辑断点（任务边界） |

> 本地适配：70%/90% 双阈值（Cursor + Claude Code）+ GSD 70% 逻辑断点

## Phase Loop（五阶段工作流）

```
Discuss → Plan → Execute → Verify → Ship → (Learn)
   │         │         │         │        │
  需求对齐  任务分解   SDD+TDD  gstack审查  模式提取
```

状态追踪：`STATE.md` 记录当前阶段 + 阻塞条件 + 切换历史。

## 子Agent编排

### DAG 波浪调度（Wave Scheduling）

```
Wave 1: 无依赖任务 → 并行派发
Wave 2: 依赖 Wave 1 的任务 → 等待前置完成
Wave 3: 最终集成
```

33 agents 分属 12 类别，workstream 隔离环境。

### 状态机

```
DONE → 审查通过
DONE_WITH_CONCERNS → 有疑虑但可继续
NEEDS_CONTEXT → 缺少信息
BLOCKED → 依赖未满足
```

## 11 质量门

| 门 | 阻断条件 |
|----|----------|
| Plan Checker (12维度) | 计划不符合 Nyquist 验证标准 |
| Schema Drift | ORM 变更缺 migration |
| Security Anchor | 未绑定威胁模型 |
| Scope Reduction | Planner 静默丢弃需求 |
| Test Coverage | 低于阈值 |
| Lint/Type Check | 构建失败 |
| Canonical Source | 引用偏离原文 |
| Trust-But-Verify | 验证未通过 |
| Artifact Consistency | 制品冲突 |
| Context Health | 超阈值未处理 |
| Deployment Ready | 发布检查未通过 |

## MVP 策略

Walking Skeleton 模式（`--mvp` flag）：纵向切片，每个切片独立可部署。Phase 1: Minimum Viable → Phase 2: Core Experience → Phase 3: Edge Cases → Phase 4: Optimization。

## Forensics/Resume（未实现）

GSD 设计了但未提供稳定实现的命令：
- `/gsd-forensics` — 诊断上下文腐烂根因
- `/gsd-resume-work` — 从制品恢复中断的工作
- `/gsd-pause-work` — 保存当前进度到制品
- `/gsd-health` — 上下文健康检查
- `/gsd-undo` — 回退到上一个检查点

> 本地决策：不实现，用制品恢复 + 压缩 + claude-mem 替代

## v1.5.0 stable（已发布 2026-06-05，Phase E 评估中）

> 双源核验（2026-06-19）：v1.5.0 **stable 已发布**（非 rc），本地仍锁 1.4.5，走 [`docs/ADR/2026-06-19-gsd-1.5.0-evaluation.md`](../../ADR/2026-06-19-gsd-1.5.0-evaluation.md) 评估。

| 1.5.0 新能力 | 说明 | 与本地冲突风险 |
|--------------|------|----------------|
| Capability Registry | ADR-857 namespace meta-skill + 生成器 + UI pilot | 与 MANIFEST concerns 模型重叠 |
| async resume/pause | external_job_waiting 半状态 + resume/pause 契约 | hooks/pre-compact-state 重叠（forensics 此前 P2 不实现） |
| Research module | 内容寻址缓存 + provider seam + `RESEARCH.md` | 与 deep-research(Firecrawl+Exa) 互博 |
| 联邦配置合并 | config-loader federated merge | 评估 |
| Loop Host Contract | 从 workflow markers 生成 | 评估 |

**ADR 签署前 `MANIFEST.gsd.version` 保持 1.4.5。**

## 本地映射

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| workstreams | `skills/workstream-management/` | ✅ |
| adr | `skills/adr-management/` | ✅ |
| context_rot | `rules/CORE.md` + `rules/CONTEXT.md` | ✅ |
| gsd_context | `rules/WORKFLOW.md` | ✅ |
| context_engineering | `rules/CONTEXT.md` + `skills/context-engineering/` | ✅ |
| GSD 70% 逻辑断点 | `rules/CORE.md` | ✅ |
| 三态制品 | `rules/CONTEXT.md` | ✅ |
| 缺口文档 | `docs/research/gsd-gaps-v10.md` | ✅ |

## 吸收决策

| 决策 | 内容 |
|------|------|
| **采纳** | 五阶段流程、三态制品、三级阈值、Trust-But-Verify、Canonical Source、DAG编排 |
| **适配** | 阈值从 60/70 调整为 70/90（匹配 Cursor/Claude Code 实际阈值） |
| **不实现** | forensics/resume/pause/health/undo（用制品恢复+压缩替代） |
| **仅跟踪** | v1.5.0-rc（不部署） |

## 互博检查

- vs OpenSpec `.planning`：三轨互斥（`change_spec` vs `phase_planning`）
- vs deer-flow：MANIFEST excludes `[deer_flow, workstream_management]`
- vs Superpowers：GSD 不原生集成 Superpowers — 原则吸收，非代码集成

## 版本演进

```
get-shit-done (v1.0-v1.42.x, gsd-build 组织)
  → get-shit-done-redux (过渡)
  → @opengsd/gsd-core (v1.0.0 → v1.4.5, open-gsd 组织)
  → v1.5.0 stable (2026-06-05，Phase E 评估，本地暂锁 1.4.5)
```

## v10.2 增量（vs v10.1）

- 五大上下文工程原则文档化
- 11 质量门完整列表（原仅 3 门）
- DAG 波浪调度机制明确
- 版本演进链路完整记录

## v10.2.1 增量（双源刷新 2026-06-19）

- **v1.5.0 stable 已发布**（修正「仅 rc」认知）：Capability Registry / async resume-pause / Research module
- 走独立 ADR 评估，三选一：Stay 1.4.5（推荐）/ Cherry-pick Research / Upgrade
- Research module 与本地 deep-research 双源调研存在互博风险，评估重点

## v10.3.1 增量（双源刷新 2026-06-26）

**v1.5.0 → v1.6.0**（GitHub Releases 交叉验证，2026-06-24 发布）：
- **ADR-1244 完整落地**（5 phase 全部完成）：
  - Phase 1 (#1430): 版本化 capability manifest + native stamping
  - Phase 2 (#1431): runtime capability registry overlay
  - Phase 3 (#1432): capability source resolver + ledger
  - Phase 4 (#1433): capability trust gate + upgrade/compat 检查
  - Phase 5 (#1434): registry-driven dispatch for 第三方 capabilities
- **新增 CLI**：`gsd capability install/update/remove/list/disable/enable`（#1457）
- **新增配置**：`workflow.context_guard_mode`（execute-phase 主动上下文耗尽守卫，#1505）
- **新增配置**：`workflow.mvp_mode`（VALID_CONFIG_KEYS，#1494）
- **安全增强**：WebFetch/WebSearch injection isolation + opt-in blocking（#1585）
- **修复**：prototype pollution (CodeQL #40, #1407)、purity gate #1777、auto-backmerge PR 门

**本地影响与决策**：
- v1.5.0 评估结论（Stay 1.4.5）需重新评估 — v1.6.0 capability registry 可能影响 MANIFEST concern 层级
- `context_guard_mode` 与本地三级阈值（70%/90%）协同，可能替代部分 GSD 逻辑断点
- Research module 互博风险维持（v1.6.0 未解决）
- 走独立 ADR 评估，三选一：Stay 1.4.5（推荐）/ Cherry-pick context_guard_mode / Upgrade to 1.6.0
- 升级阻塞：v1.5.0 → v1.6.0 跨 minor，需 changelog 评估 + 用户确认（R14）

## v10.4 增量（2026-06-29）

- **维持 Stay 1.4.5**（访谈锁定）；v1.6.0 仅文档跟踪
- 上游无新 release；GSD forensics/resume 仍在 P2 刻意不实现
