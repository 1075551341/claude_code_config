---
trigger: model_decision
description: 治理详情规则 — R14/R15/R16 适用范围、注释模板、变更彻底性三阶段、codegraph 工具集细节、最佳实践详参（提示词/API/日志/会话/编排，v11 并入原 BESTPRACTICE）。触发：改配置/改 hook/依赖升级/版本升级/写注释/审查治理/最佳实践。
---

# GOVERNANCE — 治理详情（骨架 → `rules/CORE.md`）

> 本文承接 CORE.md 迁出的详情内容。铁律一行表与门控在 CORE；此处为适用范围与操作细节。

## 门控强度（v10.15.0 — 配置驱动三门 + 完成验证硬阻断）

> 原则：不依赖模型自觉。三门文本 SSOT = `hooks/_lib/gate_messages.md`（改文本不改代码）；双端 hook 注入 `additionalContext`/`additional_context`。
> v10.14：完成验证门升级硬阻断（Claude Stop hook exit 2 回灌强制补验）；新增 PostToolUse 追踪器记录编辑/验证/审查状态；引入 code-review-graph 审查/验证专用层。

| 门         | Claude Code 触发                                                                                                      | Cursor Guard 触发                                                                                                       | 行为                                                                                                                                                                   | 豁免                                                                                                                |
| ---------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| P0 分类门  | SessionStart → `session-start-bootstrap.py`                                                                           | sessionStart → `session_bootstrap.py`                                                                                   | 每会话注入分类指令（简单/Bug/非简单路由）                                                                                                                              | 无；skill 已读且范围未变可不重复 Read                                                                               |
| 完成验证门 | UserPromptSubmit → `pre-userprompt-verify-gate.py`（软注入）+ Stop → `stop-verification-gate.py`（**硬阻断 exit 2**） | beforeSubmitPrompt → `verification_gate.py`（软注入，enforce_mode=soft）+ postToolUse → `verify_tracker.py`（状态追踪） | 软注入：命中关键词**或**状态显示未验证编辑 → 注入验证指令；硬阻断（Claude）：Stop 时强制核查变更范围轻量检查+测试证据+预期符合性+eng-reviewer 委派，未通过 exit 2 回灌 | 纯文档编辑降级；逃逸关键词（跳过验证）；max_blocks=3 上限后放行标 DONE_WITH_CONCERNS；Cursor 无 Stop 阻断能力仅注入 |
| 变更影响门 | PreToolUse Edit/Write/MultiEdit → `pre-edit-impact-nudge.py`                                                          | preToolUse Write/StrReplace → `impact_nudge.py`                                                                         | 本会话首次编辑注入「blast-radius + Grep 引用 + MANIFEST depends_on」                                                                                                   | **永不 deny**（用户决策）；二次编辑静默；状态 7 天自动清理                                                          |

- 状态文件：Claude `~/.claude/.state/impact-nudge.json` + `verification-gate.json`；Cursor Guard 同路径共用
- 配置 SSOT：`config/quality_gates.json` → `verification_gate` 节（max_blocks / auto_check_timeout_sec / skip_keywords / verify_command_patterns / require_reviewer_min_files）
- 强度调整：验证门硬阻断由 `verification_gate.enabled` 控制；影响门仅注入不阻断是**显式决策**，升级 deny 需用户确认
- Cursor 侧改动生效路径：改 `templates/cursor-guard/` → 跑 `scripts/deploy-cursor-guard.ps1` → 重启 Cursor

## R16 详细声明（错误暴漏）

- **Hook**：所有 `hooks/*.py` 禁止 `except:pass` 或 `except Exception:pass`，异常必须向上传播或 `sys.exit(1)` + 错误详情
- **Agent**：执行失败时报告错误详情 + 已尝试方案 + 建议下一步，不静默吞掉
- **子 Agent**：主 Agent 接收子 Agent 异常，决定重试/报告/中止，不丢弃
- **配置验证**：`validate_config.py` 失败时 `exit(1)` + 输出可操作修复建议
- **扫描**：`validate_config.py V17` 扫描 `hooks/` + `scripts/` 裸 except 数量，必须为 0
- **新增**：所有 Python 脚本裸 `except:` 或裸 `except Exception:` 必须为 0（除非有 `# noqa: R16` 豁免）

## R14 适用范围（版本克制）

- **依赖**：npm/pip/cargo 等默认锁定当前 major；安全补丁用同 major 最新版
- **插件/MCP/工具链**：`plugins/`、`.mcp.json`、`installed_plugins.json` 等不做「追 latest major」
- **允许 major**：用户明确要求；CVE 无同 major 修复；阻塞缺陷且 changelog 已评估
- **禁止**：`npm-check-updates -u` 无差别 major、无 changelog/无验证的批量升级

## R15 适用范围（Node / JS 包管理器）

- **默认**：`pnpm install` / `pnpm add` / `pnpm run` / `pnpm exec` / `pnpm dlx`
- **尊重项目**：已有 `pnpm-lock.yaml` 或 `packageManager` 含 `pnpm` → 必须用 pnpm；仅 `package-lock.json` 且无 pnpm 配置 → 用 npm
- **npm 兜底**：本机无 pnpm、pnpm 执行失败且用户未要求换工具链、或脚本/文档明确写 `npm` 时
- **禁止**：在 pnpm 项目中混用 `npm install` 生成/改写 lock（避免双 lock 漂移）

## 注释规则与模板

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

## 时间 API 替代库表

业务逻辑禁止原生时间 API（CORE 禁用规则）。推荐库：

| 语言   | 推荐库              |
| ------ | ------------------- |
| TS/JS  | dayjs / date-fns    |
| Python | pendulum            |
| Go     | `time` + Clock 接口 |
| Rust   | chrono / time crate |
| C#     | NodaTime            |

获取当前时间用 Shell（`date` / `Get-Date`）；`time` MCP 已不在常驻集（v10.17 常驻 9 项，见 `rules/MCP.md`）。

## 变更彻底性三阶段流程（R3/R4 详情）

**阶段 1: 变更前 — 影响分析（阻断式）**

```
① codegraph_explore(target_symbol) blast-radius — 代码级影响范围（默认工具；含调用者/被调用者）
   └ 需精确 impact 时 `CODEGRAPH_MCP_TOOLS=...,impact` 启用 codegraph_impact 或 CLI `codegraph impact`（F1）
② Grep 全项目(reference_pattern)   — 引用级影响（文件名/函数名/类型名/配置key）
③ MANIFEST.yaml concern→depends_on — 配置级关联（改此文件必须同步更新哪些文件）

输出: 受影响文件完整清单
门控: 清单为空？→ 拒绝执行，先明确范围
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

## codegraph F1 默认工具集（v10.3 纠偏）

codegraph MCP 默认仅 4 工具（`codegraph_explore`/`codegraph_node`/`codegraph_search`/`codegraph_callers`）。`codegraph_impact`/`codegraph_callees`/`codegraph_files`/`codegraph_status` **默认不暴露**，影响面信息已内联到 `codegraph_explore` 的 **blast-radius** 段与 `codegraph_node` 的 dependents 注记。

**当前 `.mcp.json` 未配置 `CODEGRAPH_MCP_TOOLS`**（v10.17 核对纠正：此前文档误称已启用）。R3/R4 的变更前影响分析以 `codegraph_explore` 的 blast-radius 段为准，已满足要求。确需独立 `codegraph_impact` 时二选一：给 `.mcp.json` 的 codegraph 条目加 `"env": {"CODEGRAPH_MCP_TOOLS": "explore,node,search,callers,impact"}` 后重启，或直接用 CLI `codegraph impact`。

## /learn ↔ claude-mem 管道（v10.2）

- brainstorming 决策 → 自动写入 claude-mem observation（跨会话复用）
- 设计品味数据（catalog/design-shotgun 或 design-pipeline）→ taste_memory concern → claude-mem
- bug 修复模式 → claude-mem observation（原 experiences/ 文件体系已归档）
- /learn 提取项目模式 → 触发 claude-mem observation 写入

## vibe-coding-cn 道/法/术/器

```
道(原则): AI能做的不人工做 | 先结构后代码 | 上下文是第一性要素
法(策略): 接口先行实现后补 | 能抄不写不重复造轮子 | 文档即上下文
术(技巧): 明确能改什么不能改什么 | Debug给预期vs实际+最小复现
器(工具): Claude Code/Cursor/Codex CLI — 选最合适的

α-提示词(生成器): 唯一职责生成其他提示词或技能
Ω-提示词(优化器): 唯一职责优化其他提示词或技能 → catalog/skills/instinct-learning（v11 降级 catalog）
```

## 快速指令前缀

| 前缀     | 行为             |
| -------- | ---------------- |
| `[方法]` | 生成具体功能代码 |
| `[方案]` | 输出技术实现规划 |
| `[解释]` | 逐步解析现有代码 |
| `[修改]` | 对项目增删改查   |
| `[审查]` | 代码质量评审     |

---

# 最佳实践详参（v11 并入原 rules/BESTPRACTICE.md）

> 来源：shanraisshan/claude-code-best-practice + x1xhlol/system-prompts + Chalarangelo/30-seconds-of-code + garrytan/gstack v0.19
> 骨架（编码规范、铁律、错误处理、变更彻底性）在 `rules/CORE.md`；本章为详细策略。

## 提示词设计

- 明确角色定位和职责边界
- 结构化输出格式（JSON Schema / Markdown Template）
- Few-shot 示例优于长描述
- 约束条件用否定式（禁止X 优于 建议不X）
- 分步推理优于一次性输出

**gstack v0.19 实证**：

- **810× 生产力提升**：Garry Tan 实测 2026 vs 2013 逻辑代码行（非原始 LOC），11,417 vs 14 行/天
- **ML 注入防御三层**：22MB 本地 ML 分类器 + Canary Tokens + Haiku 转录检查 — 零信任外部内容
- **品味记忆跨会话**：design-pipeline / catalog 的 design-shotgun 学习用户 UI 偏好，每次迭代更贴近用户审美（品味数据走 claude-mem）
- **多 Agent 浏览器共享**：`catalog/agents/pair-agent`（v11 按需变体）— 每个 AI Agent 独立 tab，ngrok tunnel，作用域隔离

**系统提示词实证**（来源：x1xhlol/system-prompts 横向对比）：

- 工具描述密度宜低不宜高 — Cursor/Devin 的对比表明简洁工具描述比详尽描述减少 30% 误用
- 安全护栏放入系统提示词而非工具描述 — 各家均采用这种分层，工具描述聚焦语义
- 角色定义粒度适度 — 过细的角色定义会导致 agent 在非角色场景拒绝处理

## 代码精炼

- 优先使用语言内置方法而非手写算法
- 函数名即文档，减少注释依赖
- 数据结构选择决定代码复杂度
- 不可变数据流优于可变状态
- 组合优于继承，函数优于类

## 工程决策原则（v11.2.0 并入 AGENTS.md 详参）

> 骨架（优先级 5 + 工程原则节）在 `rules/CORE.md`；本小节为操作化详参。

**第一性原理思考**：

- 遇到问题先追问本质：真正要解决的问题是什么？拆解到不可再分的原子需求
- 区分「事实」与「假设」：基于事实决策，对假设显式标注并验证
- 不被既有方案束缚：先想「从零开始会怎么做」，再看现有约束哪些是真约束

**KISS / SOLID 思想**：

- KISS：优先简单直接实现；DRY 不要为消除少量重复而引入过度抽象
- SOLID 思想（操作化）：单一职责、降低模块耦合；不要求机械套用五原则全文

**YAGNI 判定标准**：

- 无当前需求 = 不实现；「将来可能用到」不构成实现理由
- 不做未经验证的架构设计：架构从最小可工作版本演进，不预先设计完整抽象
- 不用未来复杂性牺牲当前可用性；预留扩展点 ≠ 提前实现扩展

**删除过时代码执行流程**：

- 确认无引用（codegraph blast-radius + Grep 全项目）→ 直接删除 → 不留兼容层/fallback/临时迁移逻辑
- 不为向后兼容长期保留废弃方案；迁移成本由调用方一次性承担，而非永久背负兼容包袱
- 例外：对外公开 API 的破坏性变更需显式 deprecation 周期（由变更彻底性门控约束）

**依赖评估清单**（引入新依赖前逐项确认）：

- 成熟度：发布历史、API 稳定性、生产验证规模
- 维护活跃度：最近提交/issue 响应/安全更新频率
- 与现有依赖重叠度：已有依赖能否覆盖？引入前必须先查已有代码/依赖/文档/能力
- 避免为「看起来更优雅」增加实际复杂度；简单方案已满足则不主动升级复杂方案

**终端环境规范（Windows）**：

- 优先 `pwsh`（PowerShell 7+ 稳定版）：PS5.1 在编码（默认 GBK/UTF-16LE）、管道行为、异常处理、跨平台路径上与 PS7 有实质差异，易引发脚本异常
- 脚本注释/文档示例统一 `pwsh -ExecutionPolicy Bypass -File <脚本>`；PS5.1 环境回退用 `powershell`
- **Qoder / 编辑器 MCP 特例**：`scripts/chrome-devtools-mcp.ps1`、`playwright-mcp.ps1`、`context7-mcp.ps1`、`python-mcp.ps1` 用 `powershell.exe` 间接启动（编辑器 MCP spawn / Qoder Go 客户端兼容），不受 pwsh 优先规则约束

## API 设计

- RESTful 资源命名用名词复数
- 版本化：`/v1/resources`
- 幂等设计：PUT/DELETE 天然幂等，POST 需显式保证
- 分页、过滤、排序参数统一格式
- 响应包含自我描述（\_links / \_meta）

## 日志规范

- 结构化日志（JSON 格式），禁止纯文本拼接
- 级别语义：DEBUG < INFO < WARN < ERROR < FATAL
- 敏感字段脱敏：password/token/secret/card_number
- 请求链路追踪：request_id 贯穿全链路

## 会话管理

- 新任务 = 新会话，不累积跨任务上下文
- 对话偏离时 rewind 优于 correct — 回退到分叉点比重定向更省 token
- 上下文 >70% 择机 compact，>90% 强制新子Agent
- 长任务（>30分钟）拆分为独立子Agent，每个有明确完成标准

**会话终验（R20）**：本会话全部任务完成后，必须对照用户**原始请求**输出清单（不是把任务重做一遍；验证命令不能代替需求对照）：

```
## 会话终验（R20）
原始要求：<一句复述>
- 满足：...
- 遗漏：无 | ...
- 错改：无 | ...
结论：DONE | DONE_WITH_CONCERNS
```

未输出该清单不得声称完成。Claude Code Stop 硬门检测标记（`会话终验` 或 `R20`，且含 `遗漏` 与 `错改`）；Cursor 经完成验证门软注入。纯文档编辑同样适用。

## 上下文管理

- 主窗口保持 30-40% 使用率，重活放子Agent fresh context
- 子Agent 间通过结构化制品通信，禁通过对话历史传递状态
- 制品优先加载：openspec/ > .planning/ > memory/
- 300-400K token 附近出现腐化阈值，接近时强制压缩

## Skills 设计

- `description` 是触发器非摘要 — 描述何时触发，非做什么
- 技能定义触发条件（菜单），不使用泛化触发词
- 高频 skill 用文件夹格式（progressive disclosure），低频用单文件
- `context: fork` 用于需要隔离的技能，`context: inherit` 用于编排技能
- 技能内禁止内联 MCP 服务器定义，统一走 .mcp.json

## Hooks 最佳实践

- Stop hook 验证而非修改 — 在停止前确保质量门，不追加额外操作
- PostToolUse 用于自动格式化，不做内容审查（留给 PreToolUse 和 human review）
- PreToolUse 匹配器尽量精确 — 空 matcher 会触发所有工具调用，浪费 token
- hook 超时设置保守（≤30s），长任务放 background agent

## Git 与 PR 管理

- Squash merge 优先，保持主分支线性历史
- 小 PR 优于大 PR — 单 PR 关注单一问题（One Concern Per PR）
- PR 描述用模板（What/Why/Test Plan），禁止自由格式
- 提交信息格式：`type(scope): subject`（≤50字符）
- 禁止 force push 到 main/master

## 调试策略

- 先在当前代码库中搜索相似模式，再查外部文档
- 错误信息逐层解读，从最底层开始
- 二分法定位：先确定哪一半代码引入问题
- 修复后写回归测试，确保同一 bug 不再出现
- 失败 2 次同一方案 → 换方案（铁律 R5）

## 编排模式

- Research → Plan → Execute → Review → Ship 元模式
- 无依赖子目标并行派发，有依赖等待前置完成
- 子Agent 状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
- 禁止 planner 与 agentic-orchestrator 同时编排同一任务

## 输出规范

- 默认简洁：回答即止，不追加总结
- 代码块仅在明确需要时输出
- 注释精简：只说 WHY，不说 WHAT
- 触发 caveman-compress：输出>500字 / 上下文>50%

## 安全基础

- 永不硬编码密钥/Token，统一走环境变量
- 系统边界验证所有外部输入，内部信任类型系统
- 文件上传检查类型/大小/内容
- 操作前确认权限，禁止默认提升

## 记忆与学习

- 失败/成功模式经 claude-mem observation 记录（原 `experiences/` 文件体系已归档至 `docs/archive/experiences/`）
- claude-mem 为跨会话 SSOT，MEMORY.md 为项目级静态索引
- 会话结束自动提取模式，30 天置信度衰减
- 优先从制品恢复上下文，而非依赖对话历史
