# Claude 全局配置

> 五柱 × 五阶段 × 三层。路由入口 → `SPEC.md` | 归属 → `MANIFEST.yaml`
> 五柱：Superpowers（方法论）GSD（上下文）OpenSpec（规格）gstack（审查）claude-mem（记忆）

---

## 优先级链

```
用户显式指令 > CLAUDE.md 指针 > 激活 skill > lazy rules > alwaysApply rules > default prompt
```

---

## 五阶段处理流程

```
用户输入
├─ 简单（≤3文件、需求明确）→ 执行 → 验证
├─ Bug/Issue → skill/triage → 路由
└─ 非简单 → ①规划(brainstorming) → ②规格(writing-plans) 
           → ③执行(executing-plans) → ④验证(verification) → ⑤学习

每阶段: 骨架层(always-on) + 执行层(reactive) + 横切层(cross-cutting)
```

<HARD-GATE>用户批准设计前禁止实现。详见 skill/brainstorming</HARD-GATE>

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
| R12 | 子Agent隔离 | fresh context + 三态制品通信，禁止共享可变状态 |
| R13 | 制品存活 | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化 |

> 扩展说明 → `rules/CORE.md` |

Karpathy 四原则 → `rules/CORE.md` + skill/karpathy-guidelines

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
| /plan | ②规格 | 设计方案 |
| /execute | ③执行 | 按计划实现 |
| /verify | ④验证 | 交叉验证 |
| /ship | — | 合并部署 |
| /review | ④验证 | gstack审查 |
| /compact | ⑤学习 | 压缩上下文 |
| /status | — | 查看进度 |

---

## caveman-compress

触发：输出>500字 / 上下文>50% / 用户要求
规则：去冗余→去解释→保留关键信息→保留代码

---

## 指针

| 内容 | 位置 |
|------|------|
| 完整索引 | SPEC.md |
| 组件归属 | MANIFEST.yaml |
| 规则铁律 | rules/CORE.md |
| 上下文工程 | rules/CONTEXT.md |
| MCP 定义 | .mcp.json |
| 审查 agent | agents/ |
| 领域库 | catalog/ |
| 命令定义 | commands/ |
| 模板 | templates/ |
| 同步指南 | SYNC_GUIDE.md |

---

## 同步

Claude Code 主环境；Cursor/Windsurf/Trae 软链接同步：CLAUDE.md + skills/ + agents/ + rules/
hooks/commands/MCP 不同步。

@RTK.md
