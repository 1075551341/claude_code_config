# Claude 全局配置

> 五柱 × 五阶段 × 三层。路由入口 → `SPEC.md` | 归属 → `MANIFEST.yaml`
> 五柱：Superpowers（方法论）GSD（上下文）OpenSpec（规格）gstack（审查）claude-mem（记忆）

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

## 铁律 R1–R13

| # | 约束 | 核心 |
|---|------|------|
| R1 | 任务完成 | 验证通过才算完成 |
| R2 | 修改确认 | Read → Edit → Read |
| R3 | Bug修复 | Grep全项目 → 全修 → 确认 |
| R4 | 配置变更 | 改接口/类型/路由 → Grep引用 → 构建 |
| R5 | 重试上限 | 同一方案失败 ≤2次 |
| R6 | 非简单任务 | ①→②→③→④→⑤ |
| R7 | 交叉验证 | 完成前通过验证清单 |
| R8 | 高危确认 | 删数据/强推main前确认 |
| R9 | 命令安全 | 禁 `cd+重定向` / `powershell -Command` |
| R10 | 简洁优先 | 最小代码 |
| R11 | 安全默认 | 不信任输入、无硬编码密钥 |
| R12 | 子Agent隔离 | fresh context + 三态制品通信 |
| R13 | 制品存活 | 跨会话持久化 |

> 扩展 → `rules/CORE.md` | Karpathy 四原则 → skill/karpathy-guidelines

---

## P0 强制 Skill (4)

| Skill | 触发 | 阶段 |
|-------|------|------|
| using-superpowers | 会话开始 | 骨架 |
| brainstorming | 方案/架构/非简单任务 | ①规划 |
| verification-before-completion | 完成/验收 | ④验证 |
| systematic-debugging | 调试/bug | ③执行 |

---

## Tool-First 五级路由

```
MANIFEST.yaml 查 owner → P0 skill → catalog skill → agent 委派 → hook/MCP
```

**Token 双轨**：Shell → RTK hook | 回复 → caveman-compress skill
**上下文阈值**：<40% 正常 / 50% compact / 70% 强制压缩
**护栏层**：骨架4 + 按需4 + 学习4 → `SPEC.md`

---

## 规格三轨（互斥）

| 轨道 | 路径 | 场景 |
|------|------|------|
| OpenSpec | `openspec/changes/<id>/` | 功能变更/brownfield |
| GSD | `.planning/phases/` | 大功能多阶段 |
| 轻量 | `spec/<project>/` | ≤3文件小功能 |

---

## 审查路由

```
所有变更     → eng-reviewer (必须)
产品/新功能  → + ceo-reviewer
UI/UX 变更   → + designer
安全敏感     → + security-reviewer
infra/配置   → CEO可跳过
```

---

## 命令速查

| 命令 | 阶段 | 作用 |
|------|------|------|
| /discuss | ①规划 | 明确需求 |
| /plan | ②规格 | 设计方案(/propose → openspec) |
| /execute | ③执行 | 按原子任务计划实现 |
| /verify | ④验证 | 交叉验证 + gstack审查 |
| /ship | — | 合并部署 |
| /compact | ⑤学习 | 压缩上下文 + 模式提取 |

---

## Token 效率

- **输出压缩**：500字 / >50%上下文 → caveman-compress
- **Shell压缩**：Bash 命令 → pre-rtk-rewrite hook
- **上下文管理**：CONTEXT.md 三级阈值 + subagent 30%预算

---

## 回复语言

所有回复优先使用中文。代码块原文保留。

---

## 指针

| 内容 | 位置 |
|------|------|
| 配置法典 | SPEC.md (v5.0) |
| 组件归属 | MANIFEST.yaml |
| 铁律+编码 | rules/CORE.md |
| 上下文工程 | rules/CONTEXT.md |
| 最佳实践 | rules/BESTPRACTICE.md |
| 工作流 | rules/WORKFLOW.md |
| MCP 定义 | .mcp.json |
| 同步指南 | SYNC_GUIDE.md |

---

## 同步

Claude Code 主环境；Cursor/Windsurf/Trae 软链接同步：CLAUDE.md + skills/ + agents/ + rules/
hooks/commands/MCP/plugins 不同步。

@RTK.md
