---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义
---

# CORE — 机器执行层骨架

> SSOT: 三横切、阈值、编码规范、铁律R12-R20、变更彻底性门控
> 引用: P0路由集/加载等级/五阶段流程 → `CLAUDE.md`（v11: ROUTER 已并入） | 治理详情(R14/R15/R16适用范围/注释模板/变更三阶段/最佳实践详参) → `rules/GOVERNANCE.md`

## 三横切基础设施

```
L1 治理 — ECC(MANIFEST防互博+hook分级+loop防护) + deer-flow 2.0(LangGraph编排,四模式)
L2 优化 — RTK(shell压缩,60-90%) + caveman(输出压缩,~75%) + 三级阈值(上下文治理)
L3 洞察 — codegraph(R17 常驻) + Firecrawl/Exa(外部搜索)  # UA removed v10.5；codebase-memory 已禁用（全盘索引爆 CPU/内存，见 R17）

所有阶段自动注入 L1/L2/L3。柱驱动阶段，横切保障执行。
```

## 上下文腐烂三级阈值

⛔ **铁律: 绝不允许上下文达到 100%。违者任务无效。**

| 使用率 | Cursor                                | Claude Code                     |
| ------ | ------------------------------------- | ------------------------------- |
| <70%   | 正常工作                              | 正常工作                        |
| 70%    | ⚠️ 择机 `/summarize` 或「压缩上下文」 | ⚠️ 择机 `/compact`              |
| 90%    | 🔴 强制 `/summarize` 或新子 Agent     | 🔴 强制 `/compact` 或新子 Agent |

⛔ 绝不允许达到 100%。子 Agent：无依赖并行 | 有依赖串行 | 同制品路径禁止并行写入。

**GSD 逻辑断点（70%）**：到达时完成当前原子任务、切换子 Agent 或写入制品；**非**强制压缩（压缩仍按上表 70%/90%）。

**每完成原子任务 → 评估上下文% → 达阈值按平台压缩**

## 五阶段状态机与门控

> 完整流程 + 状态机 + 门控全部 → `CLAUDE.md` 五阶段流程（SSOT）。

### 错误升级路径

Agent 异常 → 主 Agent 判断：**重试**（瞬态，≤R5 上限2次）→ **降级**（非核心能力不可用，标 DONE_WITH_CONCERNS 继续）→ **需确认**（权限/冲突/数据风险，暴露详情等决策）→ **硬阻断**（安全/不可逆，立即停止+报告）。

**原则**: 不静默吞错（R16），不无限重试（R5），不确定时升级而非猜测。

## 优先级

1. **简单至上** — 最小可行方案，拒绝过度设计
2. **精准响应** — 直击要点，无废话
3. **最佳实践** — 干净代码 + 语义化 + 安全规范
4. **主动确认** — 需求模糊时先问，不盲目执行
5. **第一性原理** — 优先解决本质问题；长期可维护 > 临时运行；代码服务业务目标而非展示技术

## 代码规范

- DRY + 单一职责；不可变优先（新对象/展开/map/filter，不原地修改）
- 未指定语言 → 沿用当前项目技术栈；未指定框架 → 最轻量够用方案
- 安全防御 → `rules/SECURITY.md`；错误处理：每层显式处理，禁止静默吞错，异步必 try/catch
- 输入验证：系统边界验证所有外部输入；内部信任类型系统
- 文件组织：多小文件优于少大文件（典型 200-400 行，上限 800），单一职责
- 性能：热路径测量→优化→验证；I/O 批量，避免 N+1
- 注释：独立组件/完整功能/复杂逻辑/对外 API 时写头部 docstring（模板 → `rules/GOVERNANCE.md`）
- 测试：新功能必覆盖；Bug 修复先写复现测试；命名 `should_x_when_y`；不跳过测试

## 工程原则

- KISS：优先简单直接实现，不为消除少量重复而做过度抽象
- SOLID 思想：职责清晰、降低模块耦合（不展开五原则全文）
- YAGNI：不为假设的未来需求提前设计；不做未经验证的架构设计；从最小可工作版本演进
- 删除过时代码优先于加兼容层/fallback/临时迁移逻辑
- 依赖克制：优先成熟稳定第三方库；用已有依赖前不随意新增；引入新方案前先查已有代码/依赖/文档/能力
- 简单方案已满足则不主动升级复杂方案；避免为“看起来更优雅”增加实际复杂度
- 详参 → `rules/GOVERNANCE.md` 最佳实践详参章

## 禁用规则

业务逻辑禁止 `new Date()` / `Date.now()` / `datetime.now()` — 用时区库 + Clock 接口依赖注入（TS/JS: dayjs；Python: pendulum；Go/Rust/C# 同理）。CLI 一次性脚本、纯 UI 展示除外。推荐库表 → `rules/GOVERNANCE.md`。

## 铁律 R12–R20

> R1–R11 → `CLAUDE.md` | 适用范围详情（R14/R15/R16） → `rules/GOVERNANCE.md`

| #   | 约束          | 核心                                                                                                       |
| --- | ------------- | ---------------------------------------------------------------------------------------------------------- |
| R12 | 子 Agent 隔离 | fresh context + 结构化制品通信，禁止共享可变状态                                                           |
| R13 | 制品存活      | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化                                                    |
| R14 | 版本克制      | 非必要不升 major；优先 patch/minor；major 需明确收益或用户确认                                             |
| R15 | 包管理器      | Node 生态默认 `pnpm`；不可用时或项目仅 npm 时用 `npm`                                                      |
| R16 | 错误暴漏      | 禁止裸 `except:pass`，异常必须传播或显式处理并报告                                                         |
| R17 | 代码探索优先  | 严格：codegraph → claude-mem；codebase-memory **已禁用**；禁止跳级                                         |
| R18 | 记忆优先      | 「为什么/约定/偏好」查 claude-mem；禁止塞入 codegraph/cbm                                                  |
| R19 | Git 禁令      | 禁止自动 `git stash`/`git commit`（仅用户显式指令+Guard 确认）；禁止 force push main/master                |
| R20 | 会话终验      | 改前优先成熟方案或全局通用处理；完成后按原始要求逐条回放（满足/遗漏/错改/漏改/原功能），禁止把实现重做一遍；非功能变更必须保持原功能并给出证据；验证命令不能代替需求对照；未输出不得声称完成 |

### R20 会话终验

**改前**：优先成熟方案或已有全局通用处理；禁止为单编辑器/单场景发明特例（现有全局方案不够时才开特例，并在终验「错改」里说明）。详参 → `rules/GOVERNANCE.md` 工程决策原则。

**完成后**：按用户原始要求逐条回放核对（禁止把实现重做一遍）。验证命令不能代替需求对照。必须输出满足 / 遗漏 / 错改 / 漏改（影响面内该改的都改了） / 原功能。非功能变更（重构/格式/配置/重命名/文档）「原功能」必须写「保持」并指向测试或冒烟证据；禁止「应该没影响」。模板 SSOT → `skills/verification-before-completion/SKILL.md`。未输出不得声称完成。

### R17-R18 代码理解工具优先级（严格递进，禁止跳级）

```
1. 结构/局部（调用链、依赖、影响面、「怎么运作」）
   → 仅 codegraph_explore；禁止直接 Grep/Read
2. codebase-memory：**已禁用**（全盘索引爆内存）— 勿调用；原升级场景（语义/跨服务/ADR）一律用 codegraph
3. 「为什么这么做」「约定是什么」「用户偏好」（代码推不出）
   → 查 claude-mem；决策原因存 memory
```

| 需求                       | 首选                               | 次选                    | 禁止                                 |
| -------------------------- | ---------------------------------- | ----------------------- | ------------------------------------ |
| 函数/类/调用链/符号影响面  | codegraph_explore（blast-radius）  | —（无索引才 Grep 定点） | 跳过 codegraph 直接 Grep/Read        |
| 语义模糊 / 跨服务 / ADR    | codegraph_explore                  | docs/ADR/ 手写          | 启用/调用 codebase-memory（已禁用）  |
| 为什么/约定/偏好/决策原因  | claude-mem search→get_observations | —                       | 往 codegraph 塞偏好；重复 Read       |
| 变更后 test-gap / 风险评分 | code-review-graph detect_changes   | —                       | 用 codegraph 做 test-gap（无此能力） |

**codegraph vs code-review-graph 分工（v10.14，防互博）**：

- **codegraph = R17 探索主位**（符号/调用链/blast-radius/变更前影响面）
- **code-review-graph = 审查/验证专用**（变更后 test-gap、detect_changes 风险评分、review-delta、pre_merge_check）
- 禁止用 CRG 替代 R17 日常探索；禁止用 codegraph 做 test-gap（无此能力）。CRG 需项目内 `code-review-graph build` 建图，未建图自动降级跳过。

**索引刷新**：codegraph v1.5 起由 MCP server **自动同步**（原生文件监听 + 连接时追赶，无需 hook/脚本触发；v11 已退役双侧 sync hook）。claude-mem / codebase-memory 不在自动刷新范围。

### R17 反模式检测

| 行为                                             | 判定         | 后果                              |
| ------------------------------------------------ | ------------ | --------------------------------- |
| 改文件前未查 blast-radius（`codegraph_explore`） | 违反 R17     | 变更范围不可信                    |
| 跳过 codegraph 直接 Grep 搜函数                  | 违反 R17     | ~47% token / ~58% 工具调用浪费    |
| 结构问题未用 codegraph 就上 cbm                  | 违反 R17     | cbm 已禁用；标 DONE_WITH_CONCERNS |
| 启用/调用 codebase-memory                        | 禁止         | 全盘索引爆内存；用 codegraph      |
| codegraph 已返回结果仍 Read 同文件               | 违反 R17     | 重复 token 消耗                   |
| 探索前未确认 codegraph init                      | 违反 mandate | 索引缺失，回退全量 Grep           |

**codegraph_explore 返回的源码视为已读取，禁止重复 Read/Grep。**（F1 默认工具集与 impact env 启用细节 → `rules/GOVERNANCE.md`）

## 变更彻底性保障（R3/R4 强制执行）

**⛔ 改任何文件前必须先查 blast-radius（`codegraph_explore`）+ Grep 全项目引用 — 违反者变更视为不可信。**

> 改任何文件/函数/类型/配置 → 先分析影响范围 → 全关联文件修改 → 残留引用检测（三阶段详情 → `rules/GOVERNANCE.md`）

### 强制触发条件

| 变更类型                 | 必须执行                                                   |
| ------------------------ | ---------------------------------------------------------- |
| 改函数签名/接口/类型定义 | `codegraph_explore` blast-radius + Grep 全项目引用         |
| 改配置文件/规则/Skill    | MANIFEST `depends_on` 遍历                                 |
| 重命名/删除/移动文件     | Grep 全项目残留引用                                        |
| 改 agent/hook/MCP 定义   | 同步更新 INDEX.md + MANIFEST.yaml                          |
| 调研/分析任务            | 先 `codegraph_explore` blast-radius 确定范围，再逐文件深读 |
| 变更后验证 test-gap      | `code-review-graph` detect_changes（有图项目）+ 测试运行   |

### 反模式（禁止）

| 禁止                     | 原因                        |
| ------------------------ | --------------------------- |
| 只改指定文件不改关联文件 | 造成不一致/死代码           |
| "看起来差不多" 跳过 Grep | 遗漏隐藏引用                |
| 手动估计影响范围         | codegraph 比人准            |
| 残留引用 > 0 声称完成    | 违反 R1（验证通过才算完成） |

## 工作原则与项目约定

> Tool-First 路由、五柱边界、失败报告 → `CLAUDE.md`

- 自动维护 `README.md`；最小改动集；环境配置走 `.env`，禁止硬编码
- 沟通语言：中文；代码仅在明确要求或上下文需要时输出完整代码块
- Windows 终端：优先 `pwsh`（PowerShell 7+ 稳定版，避免 PS5.1 异常）；脚本注释示例统一 pwsh 化（编辑器 MCP 启动包装 `python-mcp.ps1` 等用 powershell.exe，详见 GOVERNANCE）
- Git 规范 → `rules/GIT.md`；提交/PR → `skills/git-workflow`、`skills/pr-workflow`
- Karpathy 四原则 → `skills/karpathy-guidelines/SKILL.md`（L3 按需）
