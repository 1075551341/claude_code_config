# Fission-AI/OpenSpec v1.4.1

> 层: 五柱(OpenSpec) | 置信度: 高 | 刷新: 2026-06-17 | 来源: GitHub + DeepWiki + npm + 官方文档

## v10.5 delta (2026-07-17)

- **最新元数据**：61,239 stars；GitHub Release **v1.6.0**；`pushed_at` 2026-07-16T22:25:56Z。
- **自 2026-06-29 的变化**：v1.6.0 新增更安全的原地计划修订，扩展工具支持，并强化 validation、archive 与 store setup。
- **本地吸收**：不变——Core profile、Delta Specs 与三轨互斥继续采纳；默认生成的 Cursor skills 仍由本地精简版覆盖。
- **双源**：GitHub API（stars/release/push）+ Firecrawl（官方 Releases 页面）。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：61,246★；Release **v1.6.0**（2026-07-10）；`pushed_at` 2026-07-16T22:25:56Z。
- **漂移要点**：`/opsx:update` 原地改计划；Oh My Pi / TRAE 适配；校验读 fenced examples；archive 失败非零退出；fresh stores 可用性。
- **本地吸收 / 缺口**：钉 **1.4.1** profile core；升 1.6 待评估。已有：OPSX 全链 + rules/OPENSPEC。
- **不吸收**：Oh My Pi / TRAE 生成器（非本机主路径）。
- **双源**：GitHub API + Firecrawl（v1.6.0 release）。
## 核心价值

OpenSpec 是**规格驱动开发（SDD）**的 CLI 工具链。核心创新：**Delta Specs** — 只描述变更（ADDED/MODIFIED/REMOVED/RENAMED），不重写全量 spec，天然适合 brownfield 项目。

### OPSX 流体工作流

```
propose → continue|ff → apply → verify → sync → archive
```

| 命令 | profile | 作用 |
|------|---------|------|
| `propose` | core | 创建 `openspec/changes/<id>/` 含 proposal.md |
| `explore` | core | 交互式探索已有 specs |
| `apply` | core | 按 tasks.md 逐步实现 |
| `sync` | core | Delta specs → 主 spec 语义合并（v1.4.0 起默认含于 core） |
| `archive` | core | 归档已完成的 change |
| `verify` | expanded | 验收实现与制品一致性 |
| `bulk-archive` | expanded | 批量归档 + 冲突检测 |
| `onboard` | expanded | 11 阶段 CLI 引导 |
| `continue` | expanded | 单步创建下一制品 |
| `ff` | expanded | 快进创建全部制品 |
| `status/list/show` | expanded | 查看 changes 状态 |

### Delta Spec 标记

```markdown
## ADDED Requirements
### Requirement: Two-Factor Authentication
...

## MODIFIED Requirements
### Requirement: User Login
...

## REMOVED Requirements
### Requirement: SMS Verification
...
```

Delta Application Algorithm（`src/core/archive.ts`）：语义级合并（非行级 diff），按 requirement 粒度检测冲突。

## 四大制品

| 制品 | 职责 | 依赖 |
|------|------|------|
| `proposal.md` | 为什么做、做什么 | — |
| `specs/` | Delta spec（ADDED/MODIFIED/REMOVED/RENAMED） | proposal.md |
| `design.md` | 技术方案、架构决策 | specs/ |
| `tasks.md` | 实施 checklist、原子任务 | design.md |

Schema-driven dependency graph（DAG）：done/ready/blocked 状态机。

## 三维验证（v1.4.0+）

| 维度 | 检查内容 |
|------|----------|
| **Completeness** | 所有 spec requirements 都有对应实现 |
| **Correctness** | 实现行为与 spec 描述一致 |
| **Coherence** | 无内部矛盾（如两处 spec 对同一行为描述冲突） |

## CLI 工具链

### 安装与初始化

```bash
npm install -g @fission-ai/openspec@latest  # Node >=20.19
openspec init --tools cursor --force         # 生成 .cursor/skills + openspec/
openspec update                              # 刷新 agent skills
```

### 三种交付模式

1. **file-based** — 无插件，直接读写文件（30 tools 支持）
2. **adapter** — 格式转换（MD ↔ TOML ↔ .prompt），语法变体（colon vs hyphen vs skill prefix）
3. **skill-based** — 4 skills（Cursor/Codex/Claude Code 等不支持 command adapter 的平台）

### 其他命令

- `openspec status` — 查看 changes 状态
- `openspec list` — 列出所有 changes
- `openspec show <id>` — 查看 change 详情
- `openspec validate` — 校验 spec schema
- `openspec view` — 可视化 spec 依赖图
- `openspec schemas` — 查看可用 schemas
- `openspec schema init/fork` — 创建/派生自定义 schema

## Progressive Rigor

| 模式 | 制品要求 | 适用场景 |
|------|----------|----------|
| **lite** | proposal.md + tasks.md | 小变更（<3 文件） |
| **full** | proposal.md + specs/ + design.md + tasks.md | 标准变更 |

## 30 Tools 集成

26 tools 通过 command adapters 集成（file-based，无插件依赖），4 tools 仅通过 skills。自动检测环境，update 时检测 profile/delivery drift。

## 三轨互斥模型

| 轨道 | 路径 | 场景 |
|------|------|------|
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更 / brownfield |
| GSD .planning | `.planning/phases/` | 大功能多阶段 |
| 轻量 spec | `spec/<project>/` | ≤3 文件小功能 |

同功能不可跨轨双写。

## 本地映射

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| change_spec | `commands/propose.md` | ✅ |
| openspec_rules | `rules/OPENSPEC.md` | ✅ |
| onboarding | `skills/onboarding-guide/` | ✅ |
| spec_review | `skills/spec-validation/` | ✅ |
| OPSX 全链 | `commands/{propose,apply,verify,sync,archive}.md` | ✅ |

## 吸收决策

| 决策 | 内容 |
|------|------|
| **采纳** | Core profile (propose + explore + apply + sync + archive)；Delta spec 格式；三轨互斥 |
| **适配** | Expanded commands 通过本地 scripts 实现；verify/bulk-archive 用本地替代 |
| **不采用** | CLI `openspec init --tools cursor` 的默认 skills（用本地精简版覆盖） |

## 互博检查

- vs GSD `.planning`：三轨互斥（`change_spec` vs `phase_planning`）
- vs Superpowers brainstorming：OpenSpec proposal 与 brainstorming 设计文档互补
- vs writing-plans：OpenSpec tasks.md 与 writing-plans 原子任务互补

## v10.2 增量（vs v10.1）

- 11 命令完整清单（core 5 + expanded 6）
- DAG 制品依赖图 + done/ready/blocked 状态机
- Delta Application Algorithm 语义合并说明
- 三维验证（Completeness/Correctness/Coherence）
- Progressive Rigor（lite/full 模式）
- 30 tools 集成全景
