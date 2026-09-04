---
description: Claude 配置总纲 — Tool-First 路由 + 五阶段 + 铁律（多端 L0 必加载）
alwaysApply: true
layer: router
---

# Claude 全局配置

> 五柱×五阶段×三横切 | 归属→`MANIFEST.yaml` | 法典→`SPEC.md` | **v12.0.1**
> 五柱：Superpowers(方法论，随插件更新) | GSD(上下文) | OpenSpec(规格) | gstack(审查) | claude-mem(记忆)
> 三横切：L1 治理 | L2 RTK+caveman+阈值 | L3 codegraph+Firecrawl/Exa（cbm 已禁用）→ `rules/CORE.md`

## 总纲链（Tool-First Read）

1. 本文件（编辑器软链 → `~/.claude/CLAUDE.md`）
2. `MANIFEST.yaml`（归属 + harness）
3. `skills-INDEX.md` | `agents-INDEX.md` | `rules-INDEX.md`
4. `SPEC.md`（变更史 → `CHANGELOG.md`）
5. 按需 Read：`skills/<name>/SKILL.md` | `agents/<name>.md`

优先级：用户显式指令 > CLAUDE.md > 激活 skill > alwaysApply > 默认。工具：结构→codegraph（R17）；偏好→claude-mem（R18）。禁止跳级。

## P0 路由（判定 SSOT 禁止复制）

| Skill                          | 级  | 触发                             |
| ------------------------------ | --- | -------------------------------- |
| using-superpowers              | L1  | 会话开始、分类路由               |
| task-triage                    | L1  | 会话开始分类（条件只在该 skill） |
| change-impact-analysis         | L1  | 任何修改意图                     |
| brainstorming                  | L1  | 非简单 ①规划（grill→HARD-GATE）  |
| verification-before-completion | L2  | ④验收                            |
| systematic-debugging           | L2  | Bug/调试                         |

简单 = Phase0 + 关联需改≤2 + 白名单 + 六维全低 + 模型匹配 + attempt=1（缺一不可）。持续处理→执行升档非简单。

## 加载

| 级  | 内容                                                                         | 机制                           |
| --- | ---------------------------------------------------------------------------- | ------------------------------ |
| L0  | 本文件 + `rules/CORE.md`                                                     | always-on；FRONTEND 仅 `paths` |
| L1  | 上表四门 L1                                                                  | 会话按需 Read                  |
| L2  | writing-plans / spec-validation / executing-plans / verification / debugging | 阶段 Read                      |
| L3  | 其余 skill / agent / MCP / Firecrawl+Exa                                     | description + slash            |

## 五阶段

入口：claude-mem（R18）→ using-superpowers + task-triage。
简单 → change-impact → 一次改齐 → ④比例。Bug → triage → systematic-debugging → ④全量。
非简单 → grill → ①brainstorming HARD-GATE → ②writing-plans → ③executing-plans → ④verification → ⑤claude-mem。
调研 → deep-research。TDD/SDD 仅用户显式要求。状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED。

用户批准设计前禁止实现 → skills/brainstorming

铁律 R1–R20 正文→`rules/CORE.md`（含 R16 禁止裸 except）。R20 回放满足/遗漏/错改/漏改/原功能/影响范围，配置须与文档/注释同步；六字段模板→verification skill。Karpathy→`skills/karpathy-guidelines`。

## 机械门控（hook，不靠自觉）

无双图 deny | 编码快照+校验 | bash-guard / 密钥 | 影响面 | 验证追踪 | Stop 有写入须新鲜独立审查（缺则 exit 2） | R17 探索软门。清单→`hooks/README.md`。

**禁止**：无双图 Grep/编辑；跳过 codegraph 做结构探索；跳过 claude-mem 重复 Read；深度调研跳过 Firecrawl+Exa；>70% 不评估压缩。
**强制 Read**：分类 task-triage；① brainstorming；④ verification；Bug systematic-debugging。

## 工具与审查

| 场景           | 首选                             | 禁止替代       |
| -------------- | -------------------------------- | -------------- |
| 结构/怎么运作  | `codegraph_explore`              | Grep/Read；cbm |
| 影响面/审查/PR | CRG minimal/impact/detect/review | 无图假装已审   |
| 为什么/偏好    | claude-mem                       | 塞入 codegraph |
| 深度调研       | Firecrawl+Exa                    | 仅 WebFetch    |

修改→验证（观察输出）→ `eng-reviewer` 只找问题、一次找齐、每轮全新开审；清单齐后 `change-implementer`。最多 3 轮。产品+ceo；UI+designer+dx；安全+security-reviewer；跨模型+codex-reviewer。计划未批准禁止声称完成。

## 命令与指针

`/discuss /plan /execute /verify /ship` | `/review` | `/opsx:propose|apply|sync|archive`。正文在对应 skill。
MANIFEST | SPEC | CORE | SYNC_GUIDE | MCP→`skills/mcp-config` | Git→`skills/git-workflow` | 调研→`docs/research/COVERAGE.md`
同步：`scripts/sync.ps1`（cursor / qoder-cn / trae-cn / trae）。业务仓 SessionStart 双图 ensure；验证全绿后才 sync。
