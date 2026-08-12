---
trigger: model_decision
description: 治理详情规则 — R14/R15/R16 适用范围、注释模板、变更彻底性三阶段、codegraph 工具集细节。触发：改配置/改 hook/依赖升级/版本升级/写注释/审查治理。
---

# GOVERNANCE — 治理详情（骨架 → `rules/CORE.md`）

> 本文承接 CORE.md 迁出的详情内容。铁律一行表与门控在 CORE；此处为适用范围与操作细节。

## 门控强度（v10.15.0 — 配置驱动三门 + 完成验证硬阻断）

> 原则：不依赖模型自觉。三门文本 SSOT = `hooks/_lib/gate_messages.md`（改文本不改代码）；双端 hook 注入 `additionalContext`/`additional_context`。
> v10.14：完成验证门升级硬阻断（Claude Stop hook exit 2 回灌强制补验）；新增 PostToolUse 追踪器记录编辑/验证/审查状态；引入 code-review-graph 审查/验证专用层。

| 门         | Claude Code 触发                                             | Cursor Guard 触发                               | 行为                                                                                          | 豁免                                                              |
| ---------- | ------------------------------------------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| P0 分类门  | SessionStart → `session-start-bootstrap.py`                  | sessionStart → `session_bootstrap.py`           | 每会话注入分类指令（简单/Bug/非简单路由）                                                     | 无；skill 已读且范围未变可不重复 Read                             |
| 完成验证门 | UserPromptSubmit → `pre-userprompt-verify-gate.py`（软注入）+ Stop → `stop-verification-gate.py`（**硬阻断 exit 2**） | beforeSubmitPrompt → `verification_gate.py`（软注入，enforce_mode=soft）+ postToolUse → `verify_tracker.py`（状态追踪） | 软注入：命中关键词**或**状态显示未验证编辑 → 注入验证指令；硬阻断（Claude）：Stop 时强制核查变更范围轻量检查+测试证据+预期符合性+eng-reviewer 委派，未通过 exit 2 回灌 | 纯文档编辑降级；逃逸关键词（跳过验证）；max_blocks=3 上限后放行标 DONE_WITH_CONCERNS；Cursor 无 Stop 阻断能力仅注入 |
| 变更影响门 | PreToolUse Edit/Write/MultiEdit → `pre-edit-impact-nudge.py` | preToolUse Write/StrReplace → `impact_nudge.py` | 本会话首次编辑注入「blast-radius + Grep 引用 + MANIFEST depends_on」                          | **永不 deny**（用户决策）；二次编辑静默；状态 7 天自动清理        |

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
- design-shotgun 品味数据 → taste_memory concern → claude-mem
- bug 修复模式 → experiences/patterns/ + claude-mem observation
- /learn 提取项目模式 → 触发 claude-mem observation 写入

## vibe-coding-cn 道/法/术/器

```
道(原则): AI能做的不人工做 | 先结构后代码 | 上下文是第一性要素
法(策略): 接口先行实现后补 | 能抄不写不重复造轮子 | 文档即上下文
术(技巧): 明确能改什么不能改什么 | Debug给预期vs实际+最小复现
器(工具): Claude Code/Cursor/Codex CLI — 选最合适的

α-提示词(生成器): 唯一职责生成其他提示词或技能
Ω-提示词(优化器): 唯一职责优化其他提示词或技能 → skill/instinct-learning
```

## 快速指令前缀

| 前缀     | 行为             |
| -------- | ---------------- |
| `[方法]` | 生成具体功能代码 |
| `[方案]` | 输出技术实现规划 |
| `[解释]` | 逐步解析现有代码 |
| `[修改]` | 对项目增删改查   |
| `[审查]` | 代码质量评审     |
