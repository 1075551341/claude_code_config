# Agents 智能体库

> **全局 17 个**（7 核心 + 6 gstack 审查 + 3 补全 + 1 跨模型）+ **catalog/agents/** 领域库

完整索引 → [agents-INDEX.md](../agents-INDEX.md)

---

## 核心 7

planner | code-explorer | code-reviewer | build-error-resolver | architect | spec-reviewer | agentic-orchestrator

## gstack 审查 6（skeleton）

eng-reviewer | ceo-reviewer | designer | **dx-reviewer** | qa | security-reviewer（含原 cso 深度模式）

## 补全 3

sre | doc-writer | **change-implementer**

## 跨模型 1

codex-reviewer

> v11 去向：cso→security-reviewer 深度模式；release-engineer→skills/ship；product-manager→catalog office-hours；design-engineer→skills/design-pipeline；design-shotgun/pair-agent/ios-specialist/land-and-deploy/performance-engineer→`catalog/agents/`（按需复制）。

---

## Cursor Task 注册 vs 本地 agents

| 来源                    | 机制                                 | Token 影响                          |
| ----------------------- | ------------------------------------ | ----------------------------------- |
| `~/.claude/agents/*.md` | sync 联接；Task `subagent_type` 引用 | 每个定义计入 Subagent + Task schema |
| plugin subagents        | 已禁用 compound-engineering          | 勿重复启用                          |
| Cursor 内置             | explore, shell, generalPurpose 等    | 保留；按需委派                      |

**审查路由 SSOT**：仅 `~/.claude/agents/` gstack。MANIFEST `excludes: plugin/compound-engineering/*`。

### 推荐常驻（核心 7 + 审查 6）

| 类别   | Agents                                                                                                      |
| ------ | ----------------------------------------------------------------------------------------------------------- |
| 核心 7 | planner, code-explorer, code-reviewer, build-error-resolver, architect, spec-reviewer, agentic-orchestrator |
| 审查 6 | eng-reviewer, ceo-reviewer, designer, dx-reviewer, qa, security-reviewer                                    |
| 补全   | sre, doc-writer, change-implementer                                                                         |

> `context-manager` 已合并至 claude-mem（MANIFEST `memory_ssot`）；勿重复注册。

其余 gstack 补全 / catalog agents：**按需** Task 委派，避免全量注册膨胀。

### 委派原则

- 按 MANIFEST concern→owner 路由，非按名称堆叠
- 子 Agent fresh context（R12）；制品通信，禁止共享可变状态
- 简单任务（task-triage 判定=关联需改≤2）不启动多 persona 审查链

---

审查路由 → `rules/AGENTS.md` | 归属 → `MANIFEST.yaml`
