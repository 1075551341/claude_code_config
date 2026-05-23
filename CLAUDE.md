# Claude 全局配置

> 路由层入口。索引 → `SPEC.md` | 归属 → `MANIFEST.yaml` | 技能 → `skills/` | 智能体 → `agents/`

---

## 五柱架构

| 柱 | 来源 | 职责 |
|----|------|------|
| Superpowers | obra/superpowers | 方法论 + P0 skill（brainstorming/verification/debugging） |
| GSD | GSD-redux | 上下文工程（阈值 <40%/50%/70%）+ 连续执行 + read-before-edit |
| OpenSpec | Fission-AI/OpenSpec | 规格格式（proposal→spec→tasks）+ spec-validation |
| gstack | garrytan/gstack | 角色审查（eng/ceo/designer/qa/security） |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 SSOT + 模式提取 |

## 优先级链

```
用户显式指令 > CLAUDE.md 指针 > 激活 skill > lazy rules > alwaysApply rules > default prompt
```

---

## 铁律 R1–R11

| # | 约束 | 核心要求 |
|---|------|----------|
| R1 | 任务完成 | 验证通过才算完成 |
| R2 | 修改确认 | Read → Edit → Read 确认 |
| R3 | Bug 修复 | Grep 全项目 → 全修 → Grep 确认 |
| R4 | 配置变更 | 改接口/类型/路由 → Grep 引用 → 构建验证 |
| R5 | 重试上限 | 同一方案失败 ≤2 次 |
| R6 | 非简单任务 | 头脑风暴 → 计划 → 执行 → 验证 → 模式提取 |
| R7 | 交叉验证 | 声称完成前必须通过验证清单 |
| R8 | 高危确认 | 删生产数据/强推 main 前必须确认 |
| R9 | 命令安全 | 禁止 `cd + 重定向` / `powershell -Command` 包裹 |
| R10 | 简洁优先 | 最小代码解决问题 |
| R11 | 安全默认 | 输入不信任、无硬编码密钥 |

<HARD-GATE>用户批准设计前禁止实现。详见 skill/brainstorming。</HARD-GATE>

Karpathy 四原则 → `rules/CORE.md` + skill/karpathy-guidelines

---

## 任务决策树

```
收到任务
├─ 简单（≤3文件、需求明确、无方案选择）→ 执行 → 验证
└─ 非简单 → skill/brainstorming → skill/writing-plans → 执行 → skill/verification-before-completion
```

---

## P0 强制 Skill（4 个）

| Skill | 触发 |
|-------|------|
| using-superpowers | 会话开始 / 不确定用什么技能 |
| brainstorming | 头脑风暴、方案设计、架构决策 |
| verification-before-completion | 完成、验收、声称完成 |
| systematic-debugging | 调试、报错、bug |

---

## Tool-First

```
MANIFEST.yaml 查 owner → P0 skill → 全局/catalog skill → agent 委派 → hook → MCP（TOOL_MATCHING_GUIDE.md）
```

**Token 双轨**：Shell → RTK hook | 回复 → caveman-compress skill

---

## 持续学习

| 机制 | 路径 |
|------|------|
| claude-mem | 跨会话记忆 plugin |
| stop-pattern-extraction | → experiences/patterns/ |
| pre-compact-state | 压缩前快照 |
| catalog | 领域能力不丢失，按需复制 |

---

## 规格三轨（互斥，同功能只选一套）

| 轨道 | 路径 | 场景 |
|------|------|------|
| OpenSpec | `openspec/changes/<id>/` | 功能变更 / brownfield |
| GSD | `.planning/phases/` | 大功能多阶段 |
| 轻量 | `spec/<project>/` | ≤3 文件小功能 |

---

## 命令速查

| 命令 | 作用 |
|------|------|
| /discuss | 明确需求 |
| /plan | 设计方案（→ writing-plans） |
| /execute | 按计划实现 |
| /verify | 交叉验证 |
| /ship | 合并部署 |
| /propose (/spec) | 创建 OpenSpec 变更 |
| /review | gstack 多角色审查 |
| /compact | 战略压缩上下文 |
| /clear | 切换任务重置 |
| /status | 查看工作流阶段与进度 |

---

## 上下文阈值

| 使用率 | 行动 |
|--------|------|
| <40% | 正常工作（主会话编排 + 子agent实现） |
| 50% | 逻辑断点 `/compact` |
| 70% | 强制压缩或新子 Agent |

---

## 指针

| 内容 | 位置 |
|------|------|
| 完整索引 | SPEC.md |
| 组件归属 | MANIFEST.yaml |
| 规则铁律 | rules/CORE.md |
| 领域 skill 库 | catalog/skills/（按需复制到项目） |
| 领域 agent 库 | catalog/agents/ |
| 同步指南 | SYNC_GUIDE.md |

---

## 同步

Claude Code 主环境；Cursor/Windsurf/Trae 软链接同步：`CLAUDE.md` + `skills/` + `agents/` + `rules/`。hooks/commands/MCP 不同步。

@RTK.md
