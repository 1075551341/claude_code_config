---
trigger: model_decision
description: 综合最佳实践 — 详细参考（骨架内容已迁至 CORE.md）
---

> **status: supplement_only** — v10.2: CORE.md = SSOT（编码规范、铁律、错误处理、变更彻底性）。
> 本文保留：提示词设计、代码精炼、API 设计、日志规范、会话管理等详细策略。

# 综合最佳实践

> 来源：shanraisshan/claude-code-best-practice + x1xhlol/system-prompts + Chalarangelo/30-seconds-of-code + garrytan/gstack v0.19
> **骨架内容已迁至 `rules/CORE.md`**：错误处理规范、铁律 R14–R16。

## 提示词设计

- 明确角色定位和职责边界
- 结构化输出格式（JSON Schema / Markdown Template）
- Few-shot 示例优于长描述
- 约束条件用否定式（禁止X 优于 建议不X）
- 分步推理优于一次性输出

**gstack v0.19 实证**：
- **810× 生产力提升**：Garry Tan 实测 2026 vs 2013 逻辑代码行（非原始 LOC），11,417 vs 14 行/天
- **ML 注入防御三层**：22MB 本地 ML 分类器 + Canary Tokens + Haiku 转录检查 — 零信任外部内容
- **品味记忆跨会话**：`/design-shotgun` 学习用户 UI 偏好，每次迭代更贴近用户审美
- **多 Agent 浏览器共享**：`/pair-agent` — 每个 AI Agent 独立 tab，ngrok tunnel，作用域隔离

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

## API 设计

- RESTful 资源命名用名词复数
- 版本化：`/v1/resources`
- 幂等设计：PUT/DELETE 天然幂等，POST 需显式保证
- 分页、过滤、排序参数统一格式
- 响应包含自我描述（_links / _meta）

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

## 依赖与版本（铁律 R14 + R15）

**版本（R14）**

- 默认：同 major 内 patch/minor（安全修复、bugfix）
- major 升级：用户明确要求，或 CVE 无同 major 修补，或阻塞缺陷且已读 changelog
- 禁止：无差别 `ncu -u` / `@latest` 批量 major、无验证清单的依赖大扫除
- 插件/MCP/全局工具链：非用户指令不主动 bump major

**包管理器（R15，Node 生态）**

- 默认命令：`pnpm install` / `pnpm add` / `pnpm run` / `pnpm exec` / `pnpm dlx`
- 项目已有 `pnpm-lock.yaml` 或 `packageManager` 指定 pnpm → 禁止改用 npm install
- npm 兜底：无 pnpm、仅 `package-lock.json`、或 pnpm 不可用且用户未指定工具链
- 新建 monorepo/前端项目：优先 `pnpm init` + `packageManager` 字段

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

- 失败模式写入 `experiences/rejected/`，成功模式写入 `experiences/patterns/`
- claude-mem 为跨会话 SSOT，MEMORY.md 为项目级静态索引
- 会话结束自动提取模式，30 天置信度衰减
- 优先从制品恢复上下文，而非依赖对话历史
