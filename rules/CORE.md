---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义
---

## 三横切基础设施

```
L1 治理 — ECC(MANIFEST防互博+hook分级+loop防护) + deer-flow 2.0(LangGraph编排,flash/standard/pro/ultra四模式)
L2 优化 — RTK(shell压缩,60-90%) + caveman(输出压缩,~75%) + 三级阈值(上下文治理)
L3 洞察 — codegraph(静态索引,47%token减少) + Understand-Anything(交互知识图) + Firecrawl/Exa(外部搜索)
可选外部 — task-master MCP(任务管理,core/standard/all三级,~70%token减少,按需启用) + deer-flow bridge(claude-to-deerflow skill)

所有阶段自动注入 L1/L2/L3。柱驱动阶段，横切保障执行。
```

## 上下文腐烂三级阈值

⛔ **铁律: 绝不允许上下文达到 100%。违者任务无效。**

| 使用率 | Cursor | Claude Code |
|--------|--------|-------------|
| <70%   | 正常工作 | 正常工作 |
| 70%    | ⚠️ 择机 `/summarize` 或「压缩上下文」 | ⚠️ 择机 `/compact` |
| 90%    | 🔴 强制 `/summarize` 或新子 Agent | 🔴 强制 `/compact` 或新子 Agent |

⛔ 绝不允许达到 100%。子 Agent：无依赖并行 | 有依赖串行 | 同制品路径禁止并行写入。

**每完成原子任务 → 评估上下文% → 达阈值按平台压缩**

## 五阶段流程

```
① 规划(brainstorming) → ② 规格(writing-plans) → ③ 执行(executing-plans/SDD+TDD)
→ ④ 验证(verification-before-completion) → ⑤ 学习(pattern-extraction)

状态机: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
门控:
  ① 规划: HARD-GATE 用户批准设计 ✓
  ② 规格: spec-validation通过 + 任务有成功标准 + 无静默缩scope
  ③ 执行: 子任务完成 + 构建/类型/Lint通过 + 子Agent异常已处理(R16)
  ④ 验证: 质量门全通过 + 交叉验证通过
  ⑤ 学习: 模式提取完成
```

## vibe-coding-cn 道/法/术/器

```
道(原则): AI能做的不人工做 | 先结构后代码 | 上下文是第一性要素
法(策略): 接口先行实现后补 | 能抄不写不重复造轮子 | 文档即上下文
术(技巧): 明确能改什么不能改什么 | Debug给预期vs实际+最小复现
器(工具): Claude Code/Cursor/Codex CLI — 选最合适的

α-提示词(生成器): 唯一职责生成其他提示词或技能
Ω-提示词(优化器): 唯一职责优化其他提示词或技能 → skill/instinct-learning
```

## 优先级

1. **简单至上** — 最小可行方案，拒绝过度设计
2. **精准响应** — 直击要点，无废话
3. **最佳实践** — 干净代码 + 语义化 + 安全规范
4. **主动确认** — 需求模糊时先问，不盲目执行

## 快速指令前缀

| 前缀     | 行为             |
| -------- | ---------------- |
| `[方法]` | 生成具体功能代码 |
| `[方案]` | 输出技术实现规划 |
| `[解释]` | 逐步解析现有代码 |
| `[修改]` | 对项目增删改查   |
| `[审查]` | 代码质量评审     |

## 代码规范

- DRY + 单一职责
- 不可变优先：创建新对象，数组用展开/map/filter，不原地修改
- 未指定语言 → 沿用当前项目技术栈
- 未指定框架 → 选最轻量够用的方案
- 安全防御 → 详见 `rules/SECURITY.md`

## 文件组织

- 多小文件优于少大文件，典型 200-400 行，上限 800 行
- 每个文件单一职责，目录按功能域组织

## 错误处理

- 每层显式处理，永不静默吞错
- 错误信息包含上下文（操作名、输入摘要、原始错误）
- 自定义错误类携带机器可读 code
- 异步操作必须 try/catch，禁止裸 await
- 已知错误 → 业务码 + 友好提示；未知错误 → 完整日志 + 通用错误码

## 输入验证

- 系统边界验证所有外部输入（API、CLI、用户输入）
- 内部代码信任类型系统，不重复验证
- 验证失败返回具体错误，不泛化

## 性能意识

- 避免不必要的计算和内存分配
- 热路径优先优化（测量 → 优化 → 验证）
- I/O 操作批量处理，避免 N+1

## 注释规则

```
触发条件（满足任一）：
  ① 独立组件 / 模块
  ② 完整业务功能
  ③ 复杂逻辑（分支 > 3 层 或 非显而易见算法）
  ④ 对外暴露的 API / 函数签名

语言：优先中文
位置：函数/类头部（JSDoc / Python docstring）
```

**注释模板：**

```
/**
 * @描述 简述功能（一句话）
 * @参数 {类型} 名称 - 说明
 * @返回 {类型} 说明
 * @示例 简短用法（复杂场景必填）
 * @注意 副作用 / 依赖 / 边界限制
 */
```

## 测试要求

- 新功能必须有测试覆盖
- Bug 修复先写复现测试
- 测试命名描述行为：`should_x_when_y`
- 不跳过测试（无 .skip/.todo 除非附 Issue 链接）

## 禁用规则

### 禁止使用 `new Date()` / 原生时间 API 获取当前时间

业务逻辑禁止 `new Date()` / `Date.now()` / `datetime.now()` — 用时区库 + 依赖注入（Clock 接口）。CLI 一次性脚本、纯 UI 展示除外。

| 语言 | 推荐库 |
|------|--------|
| TS/JS | dayjs / date-fns |
| Python | pendulum |
| Go | `time` + Clock 接口 |
| Rust | chrono / time crate |
| C# | NodaTime |

Claude Code 可用 `time` MCP 获取当前时间。

## 铁律 R12–R16

> R1–R11 → `CLAUDE.md`

| #   | 约束          | 核心                                                           |
| --- | ------------- | -------------------------------------------------------------- |
| R12 | 子 Agent 隔离 | fresh context + 结构化制品通信，禁止共享可变状态               |
| R13 | 制品存活      | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化        |
| R14 | 版本克制      | 非必要不升 major；优先 patch/minor；major 需明确收益或用户确认 |
| R15 | 包管理器      | Node 生态默认 `pnpm`；不可用时或项目仅 npm 时用 `npm`          |
| R16 | 错误暴漏      | 禁止裸 `except:pass`，异常必须传播或显式处理并报告             |
| R17 | 代码探索优先  | 探索代码先 `codegraph_explore`，次选 Grep/Glob                 |
| R18 | 记忆优先      | 历史上下文先查 claude-mem，避免重复分析文件                    |

### R17-R18 工具路由与协同

| 需求 | 首选 | 次选 | 禁止 |
|------|------|------|------|
| 函数/类/调用链 | codegraph_explore/trace | Grep精确定位 | 全库Grep盲扫 |
| 变更影响 | codegraph_impact | change-impact-analysis | 手动猜 |
| 项目全貌/领域 | /understand-chat | /understand-domain | 逐文件Read |
| 变更可视化 | /understand-diff + codegraph_impact | Grep | 忽略影响面 |
| 跨会话历史 | claude-mem search→get_observations | — | 重复分析已读文件 |

**claude-mem 三层**：search索引 → 识别关键IDs → fetch详情（token高效）

**codegraph vs UA**：codegraph=符号级低token快查 | UA=拓扑/业务流/交互图 | 互补不互博

### R16 详细声明

- **Hook**：所有 `hooks/*.py` 禁止 `except:pass` 或 `except Exception:pass`，异常必须向上传播或 `sys.exit(1)` + 错误详情
- **Agent**：执行失败时报告错误详情 + 已尝试方案 + 建议下一步，不静默吞掉
- **子 Agent**：主 Agent 接收子 Agent 异常，决定重试/报告/中止，不丢弃
- **配置验证**：`validate_config.py` 失败时 `exit(1)` + 输出可操作修复建议
- **扫描**：`validate_config.py V10` 扫描 `hooks/` 裸 except 数量，必须为 0

### R14 适用范围

- **依赖**：npm/pip/cargo 等默认锁定当前 major；安全补丁用同 major 最新版
- **插件/MCP/工具链**：`plugins/`、`.mcp.json`、`installed_plugins.json` 等不做「追 latest major」
- **允许 major**：用户明确要求；CVE 无同 major 修复；阻塞缺陷且 changelog 已评估
- **禁止**：`npm-check-updates -u` 无差别 major、无 changelog/无验证的批量升级

### R15 适用范围（Node / JS）

- **默认**：`pnpm install` / `pnpm add` / `pnpm run` / `pnpm exec` / `pnpm dlx`
- **尊重项目**：已有 `pnpm-lock.yaml` 或 `packageManager` 含 `pnpm` → 必须用 pnpm；仅 `package-lock.json` 且无 pnpm 配置 → 用 npm
- **npm 兜底**：本机无 pnpm、pnpm 执行失败且用户未要求换工具链、或脚本/文档明确写 `npm` 时
- **禁止**：在 pnpm 项目中混用 `npm install` 生成/改写 lock（避免双 lock 漂移）

## 变更彻底性保障（R3/R4 强制执行）

> 改任何文件/函数/类型/配置 → 必须先分析影响范围 → 全关联文件修改 → 残留引用检测

### 三阶段流程

**阶段 1: 变更前 — 影响分析（阻断式）**
```
① codegraph_impact(target_symbol)  — 代码级影响范围（哪些调用者/被调用者受影响）
② Grep 全项目(reference_pattern)   — 引用级影响（文件名/函数名/类型名/配置key）
③ MANIFEST.yaml concern→depends_on — 配置级关联（改此文件必须同步更新哪些文件）

输出: 受影响文件完整清单
门控: 清单为空？→ 拒绝执行，先明确范围（不可在范围不明时盲目修改）
```

**阶段 2: 变更中 — 逐文件修改**
```
按依赖拓扑序修改 → 每文件 Read→Edit→Read
清单逐项勾销，中途发现新关联 → 追加到清单
```

**阶段 3: 变更后 — 完整性验证**
```
① Grep 残留引用(old_pattern)  — 不应有未更新引用 → 残留 > 0 则回到阶段 2
② 构建/类型/Lint 通过          — 编译级验证
③ MANIFEST concern 一致性       — 归属级验证
```

### 强制触发条件

| 变更类型 | 必须执行 |
|----------|----------|
| 改函数签名/接口/类型定义 | `codegraph_impact` + Grep 全项目引用 |
| 改配置文件/规则/Skill | MANIFEST `depends_on` 遍历 |
| 重命名/删除/移动文件 | Grep 全项目残留引用 |
| 改 agent/hook/MCP 定义 | 同步更新 INDEX.md + MANIFEST.yaml |
| 调研/分析任务 | 先 `codegraph_impact` 确定范围，再逐文件深读 |

### 反模式（禁止）

| 禁止 | 原因 |
|------|------|
| 只改指定文件不改关联文件 | 造成不一致/死代码 |
| "看起来差不多" 跳过 Grep | 遗漏隐藏引用 |
| 手动估计影响范围 | codegraph 比人准 |
| 残留引用 > 0 声称完成 | 违反 R1（验证通过才算完成） |

## 工作原则

> Tool-First 路由、五柱边界、失败报告 → `CLAUDE.md`；R12–R18 详情见上。

## 项目约定

- 自动维护 `README.md`（架构概览 + 模块说明）
- 每次修改：最小改动集，不破坏现有功能
- 环境配置统一走 `.env`，禁止硬编码

## 输出格式

- 沟通语言：中文
- 代码：仅在明确要求或上下文需要时输出完整代码块

## Git 规范

> 详见 `rules/GIT.md`；提交/PR 流程 → `skills/git-workflow`、`skills/pr-workflow`（L3 slash）

## Karpathy 四原则

> 详见 `skills/karpathy-guidelines/SKILL.md`（按需 L3 Read）
