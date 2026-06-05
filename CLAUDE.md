# Claude 全局配置

> 五柱 × 五阶段 × 三横切。路由入口 → `SPEC.md` | 归属 → `MANIFEST.yaml` | 设计 → `spec/claude-config-integration/design-v6.md`

**五柱（纵向阶段驱动）**：Superpowers（方法论）| GSD（上下文工程）| OpenSpec（规格格式）| gstack（角色审查）| claude-mem（跨会话记忆）

**三横切（基础设施，所有阶段常驻）**：
- L1 治理 — ECC(防互博+hook分级) + deer-flow 2.0(LangGraph编排)
- L2 优化 — RTK(shell,60-90%) + caveman(输出,~75%) + 三级阈值(<40/50/70%)
- L3 洞察 — codegraph(静态索引,47%token减少) + Understand-Anything(交互知识图) + Firecrawl/Exa(外部搜索)

---

## 优先级链

```
用户显式指令 > CLAUDE.md 指针 > 激活 skill > lazy规则 > alwaysApply规则 > 默认
```

---

## 五阶段处理流程

```
用户输入
├─ 简单（≤3文件、需求明确）→ 执行 → 验证
├─ Bug/Issue → skill/triage（P0-P3+状态机）→ 路由
└─ 非简单 → ①规划(brainstorming) → ②规格(writing-plans 原子)
           → ③执行(executing-plans / SDD+TDD) → ④验证(verification) → ⑤学习

每阶段: 骨架层(always-on) + 执行层(reactive) + 护栏层(guardrails)
```

<HARD-GATE>用户批准设计前禁止实现。详见 skill/brainstorming</HARD-GATE>

---

## 执行模式：SDD + TDD 组合

```
SDD: spec/design → writing-plans(原子任务 2-5min) → subagent(两阶段审查) → verify
TDD: RED(失败测试) → GREEN(最小通过) → REFACTOR → verify
组合: writing-plans → 每个task: RED→GREEN→REFACTOR → 两阶段审查 → verify
```

---

## 铁律 R1–R16

| #   | 约束          | 核心                                             |
| --- | ------------- | ------------------------------------------------ |
| R1  | 任务完成      | 验证通过才算完成                                 |
| R2  | 修改确认      | Read → Edit → Read                               |
| R3  | Bug 修复      | Grep 全项目 → 全修 → 确认                        |
| R4  | 配置变更      | 改接口/类型/路由 → Grep 引用 → 构建              |
| R5  | 重试上限      | 同一方案失败 ≤2 次                               |
| R6  | 非简单任务    | ①→②→③→④→⑤                                        |
| R7  | 交叉验证      | 完成前通过验证清单                               |
| R8  | 高危确认      | 删数据/强推 main 前确认                          |
| R9  | 命令安全      | 禁 `cd+重定向` / `powershell -Command`           |
| R10 | 简洁优先      | 最小代码(优先做到高内聚,低耦合)                        |
| R11 | 安全默认      | 不信任输入、无硬编码密钥                         |
| R12 | 子 Agent 隔离 | fresh context + 三态制品通信                     |
| R13 | 制品存活      | 跨会话持久化                                     |
| R14 | 版本克制      | 非必要不升 major；优先 patch/minor               |
| R15 | 包管理器      | pnpm 优先；npm 兜底                              |
| R16 | 错误暴漏      | 禁止裸 except:pass，异常必须传播或显式处理并报告 |

> 扩展 → `rules/CORE.md` | Karpathy 四原则 → skill/karpathy-guidelines

---

## P0 强制 Skill (4)

| Skill                          | 触发                 | 阶段   |
| ------------------------------ | -------------------- | ------ |
| using-superpowers              | 会话开始             | 骨架   |
| brainstorming                  | 方案/架构/非简单任务 | ① 规划 |
| verification-before-completion | 完成/验收            | ④ 验证 |
| systematic-debugging           | 调试/bug             | ③ 执行 |

---

## Tool-First 五级路由

```
MANIFEST.yaml 查 owner → P0 skill → catalog skill → agent 委派 → hook/MCP
```

**Token 三轨**：Shell(RTK) + 输出(caveman) + 探索(codegraph: 47% token减少, 58%调用减少)
**上下文阈值**：<40% 正常 / 50% compact / 70% 强制压缩（→ rules/CORE.md）
**加载策略**：骨架(CLAUDE.md+CORE.md always) + lazy(paths: glob) + 补充(按需)
**护栏层**：L1 治理(防互博+hook分级) + L2 优化(压缩+阈值) + L3 洞察(图谱+搜索)

---

## 规格三轨（互斥）

| 轨道            | 路径                     | 场景                                             |
| --------------- | ------------------------ | ------------------------------------------------ |
| OpenSpec /opsx: | `openspec/changes/<id>/` | 功能变更/brownfield；/opsx:propose→apply→archive |
| GSD Redux       | `.planning/phases/`      | 大功能多阶段                                     |
| 轻量            | `spec/<project>/`        | ≤3 文件小功能                                    |

---

## 审查路由

```
所有变更     → eng-reviewer (必须)
产品/新功能  → + ceo-reviewer
UI/UX 变更   → + designer
安全敏感     → + security-reviewer (+ ML注入防御 gstack v0.19)
iOS 变更     → + ios-specialist (gstack v0.19)
infra/配置   → CEO可跳过
跨模型验证   → + codex-reviewer (gstack /codex)
```

---

## 命令速查

| 命令     | 阶段   | 作用                          |
| -------- | ------ | ----------------------------- |
| /discuss | ① 规划 | 明确需求                      |
| /plan    | ② 规格 | 设计方案(/propose → openspec) |
| /execute | ③ 执行 | 按原子任务计划实现            |
| /verify  | ④ 验证 | 交叉验证 + gstack 审查        |
| /ship    | —      | 合并部署                      |
| /compact | ⑤ 学习 | 压缩上下文 + 模式提取         |

---

## Token 效率

- **输出压缩**：500 字 / >50%上下文 → caveman-compress
- **Shell 压缩**：Bash 命令 → pre-rtk-rewrite hook
- **上下文管理**：CONTEXT.md 三级阈值 + subagent 30%预算

---

## 回复语言

所有回复优先使用中文。代码块原文保留。

---

## 指针

| 内容       | 位置                                              |
| ---------- | ------------------------------------------------- |
| 配置法典   | SPEC.md (v7.0)                                    |
| 组件归属   | MANIFEST.yaml                                     |
| 铁律+编码  | rules/CORE.md                                     |
| 上下文工程 | rules/CONTEXT.md                                  |
| 最佳实践   | rules/BESTPRACTICE.md                             |
| 工作流     | rules/WORKFLOW.md                                 |
| MCP 定义   | .mcp.json                                         |
| 代码图谱   | codegraph (MCP) — 预索引知识图谱，47% token减少 + 58%调用减少 + 16%成本降低 |
| 项目洞察   | Understand-Anything — 交互知识图 + 引导导览       |
| 同步指南   | SYNC_GUIDE.md                                     |
| 知识图谱   | skill/understand-anything (UA 插件)               |
| 跨会话记忆 | plugin/claude-mem                                 |
| 方法论     | plugin/superpowers                                |

---

## Plugins（已安装 18，启用 15，禁用 3）

| Plugin                    | 状态 | 提供                                       | 禁用原因             |
| ------------------------- | ---- | ------------------------------------------ | -------------------- |
| superpowers 5.1.0         | ✅   | SessionStart bootstrap + 14 技能           | —                    |
| claude-mem 13.4.0         | ✅   | 6 hooks + 15 技能                          | —                    |
| understand-anything 2.7.5 | ✅   | SessionStart + PostToolUse + 8 技能        | —                    |
| chrome-devtools-mcp 1.1.1 | ✅   | Chrome DevTools 调试                       | —                    |
| frontend-design           | ✅   | 前端设计技能                               | —                    |
| code-review               | ✅   | 代码审查技能（与 eng-reviewer agent 互补） | —                    |
| commit-commands           | ✅   | Git commit 快捷命令                        | —                    |
| context7                  | ✅   | Context7 技术文档查询                      | —                    |
| feature-dev               | ✅   | 功能开发工作流                             | —                    |
| firecrawl 1.0.9           | ✅   | 网页抓取/爬虫                              | —                    |
| github                    | ✅   | GitHub 集成                                | —                    |
| playwright                | ✅   | Playwright 浏览器自动化                    | —                    |
| security-guidance 2.0.3   | ✅   | 安全指导规则                               | —                    |
| skill-creator             | ✅   | 技能创建辅助                               | —                    |
| typescript-lsp 1.0.0      | ✅   | TypeScript LSP 支持                        | —                    |
| ralph-loop                | ❌   | 自动循环执行                               | 与五阶段受控流程冲突 |
| claude-code-setup         | ❌   | 首次安装向导                               | 已配置完成，无需     |
| claude-md-management      | ❌   | 自动修改 CLAUDE.md                         | 防止覆盖手工配置     |

> **归属原则**：SessionStart → 插件；安全守卫/质量门/审计 → 本地 hooks；审查 → 本地 agents（gstack）。**15 个启用插件中仅 2 个含 hooks（superpowers/claude-mem），其余 13 个为纯 skills/commands — 零冲突。**
>
> **同名 Skill 解析**：本地 skills/ 中 13 个与 superpowers 插件同名。Claude Code 按「后加载覆盖先加载」原则，**本地精简版覆盖插件完整版**（token 节省 45-74%，中文适配，五阶段集成）。模型视角每个 name 仅见一个 skill — 零混淆。非同名 skill（插件 24 + 本地 15）互补共存。

---

## 同步

Claude Code 主环境；Cursor/Windsurf/Trae 软链接同步：CLAUDE.md + skills/ + agents/ + rules/
hooks/commands/MCP/plugins 不同步。

@RTK.md
