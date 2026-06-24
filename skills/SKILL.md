# Skills 索引 — 名称 → 触发条件 → 路径 → 阶段

> 使用本索引按需加载 skill，避免全量暴露。骨架层(P0) 5个始终自动触发。

## P0 骨架 (5)

| Skill | 触发条件 | 阶段 | 路径 |
|-------|---------|------|------|
| using-superpowers | 会话开始 | L1 | skills/using-superpowers |
| change-impact-analysis | 任何修改/变更前 | L1 | skills/change-impact-analysis |
| brainstorming | 方案设计/架构决策/非简单任务 | L1 ① | skills/brainstorming |
| verification-before-completion | 完成/验收/声称完成 | L2 ④ | skills/verification-before-completion |
| systematic-debugging | 调试/报错/bug | L2 ③ | skills/systematic-debugging |

## Workflow (9)

| Skill | 触发条件 | 阶段 |
|-------|---------|------|
| writing-plans | 设计方案后/需任务分解 | ②规格 |
| executing-plans | 计划批准后 | ③执行 |
| test-driven-development | 新功能/实现 | ③执行 |
| subagent-driven-development | 复杂任务需并行（含 dispatching-parallel-agents） | ③执行 |
| using-git-worktrees | 多分支并行开发 | ③执行 |
| receiving-code-review | 收到 PR 审查 | ④验证 |
| requesting-code-review | 提交 PR 审查请求 | ④验证 |
| finishing-a-development-branch | 分支完成/合并 | ④验证 |
| writing-skills | 创建新 skill | ⑤学习 |

## 扩展 (8)

| Skill | 触发条件 | 阶段 |
|-------|---------|------|
| autoplan | 自动审查管线 CEO→Design→Eng | ④验证 |
| browser-qa | 浏览器 QA 测试 | ④验证 |
| design-pipeline | 设计管线探索→生产 | ②规格 |
| ship | 合并部署 | ④验证 |
| office-hours | 产品问题六问框架 | ①规划 |
| context-engineering | 上下文管理策略 | 横切 |
| structured-artifacts | 输出结构化制品 | ②规格 |
| instinct-learning | 置信度学习系统 | ⑤学习 |

## Meta (5)

| Skill | 触发条件 | 阶段 |
|-------|---------|------|
| memory-compression | 上下文压缩/记忆管理 | ⑤学习 |
| spec-validation | spec 审查/格式校验 | ②规格 |
| karpathy-guidelines | Karpathy 四原则行为约束 | 横切 |
| caveman-compress | 输出>500字/上下文>50% | 横切 |
| change-impact-analysis | 任何修改/变更前影响分析 | ③执行（P0） |

## Mattpocock (2)

| Skill | 触发条件 | 阶段 |
|-------|---------|------|
| triage | Bug报告/Issue分类 | ①规划 |
| improve-codebase-architecture | 架构改进/跨文件重构 | ③执行 |

## 项目洞察 (1)

| Skill | 触发条件 | 阶段 |
|-------|---------|------|
| understand-anything | 项目架构理解/知识图谱/新人导览 | ①规划 |

---

## v9 新增 (5)

workstream-management | adr-management | onboarding-guide | claude-to-deerflow | taste-memory

---

**总计 38 skills** — 详见 [skills-INDEX.md](../skills-INDEX.md)

**加载策略**：L1 常驻(3) → L2 阶段门控 Read(6) → L3 信号触发 Read(29) → catalog 按需复制
**显式调用**：`Read skills/<name>/SKILL.md`（首选）；slash/关键词为路由信号，非替代 Read
**互斥声明**：见 MANIFEST.yaml excludes
**外部桥接**：claude-to-deerflow(/deer-flow) | task-master(MCP)
