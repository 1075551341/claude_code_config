# 精确难度判定与一次改完 — 设计决策

## 背景

v10.12.0 已具备：关联需改≤2、六维+⑥模型匹配、`verify_tier` 比例|全量、双端 gate、SSOT=`skills/task-triage`。缺口是：

1. 分类前无强制「已知条件」盘点 → 易低估范围、多轮返工
2. 持续处理（attempt≥2）仅升验证档，执行可仍走简单旁路 → 与「最多改一次 / 首轮失败升非简单」目标冲突
3. 模型档无具体映射表 → 易虚报更高档或预期过低

## 决策

采用 **Phase0 前置盘点 → 六维+模型映射精确分类 → 简单路径一次改完 → 持续处理默认执行升档非简单**，仍以 `skills/task-triage/SKILL.md` 为唯一 SSOT；他处短引用对齐。

### 升档语义（相对 v10.12）

| 触发 | verify_tier | 执行 |
|------|-------------|------|
| attempt≥2 / 用户反馈未解决 / 验失败后继续 / 首轮问题仍在 | 全量 | **执行升档非简单**（按使用类型） |
| 清单膨胀>2 / 黑名单新现 | 全量 | 执行升档非简单 |
| 同方案达 R5（≤2）仍失败 | 全量 | 停空转 / NEEDS_CONTEXT |

升档后路由细化：

- Bug/可复现修复 → `systematic-debugging` + 全量验证；成功标准仍歧义才 grill
- 功能/架构/配置/删除 → grill → brainstorming → …
- 调研 → deep-research

### 模型档映射

- `frontier`：Opus / o3 / high-thinking 重推理档
- `mid`：Sonnet / GPT-5 中档 / Composer 主会话默认档
- `light`：Haiku / Flash / mini / 子代理默认廉价档

所需档：①–⑤ 全低 → light；含中 → mid；含高或黑名单 → frontier。当前档 < 所需档 → ⑥=高 → 非简单。

### 不做

新 hook 强制 attempt 计数器（保持配置驱动 + 门控注入；attempt 由会话契约自报）。

## 理由

- 与外部实践同构：失败升档（Model Hierarchy）、triage handoff（OpenAI Agents）、歧义走人在环（Swarmia）
- 保留现有优点：P0=6、SSOT、双端 gate、R17/R18、强制验证、MANIFEST 同步
- 一次改完依赖「先盘点再改」+「清单膨胀立即升档」，而非事后多轮简单旁路

## 替代方案

| 方案 | 淘汰原因 |
|------|----------|
| 仅升 verify_tier（v10.12） | 不满足「升非简单处理流程」 |
| 新 hook 计数 attempt | 增复杂度，与 hook 极简优点冲突 |
| 另起第三套复杂度体系 | 破坏 SSOT 与双端短引用 |

## 后果

- 简单旁路仅限 **真正简单且 attempt=1**
- 首轮失败后成本上升（非简单链），换取更少空转与更高一次成功率
- 需同步：verification、gate_messages、CLAUDE/ROUTER/using-superpowers、SPEC、Cursor 插件 ROUTER 副本、RUNTIME_PLAYBOOK/README 短引用

## 证据

- 截至 2026-08-01：[Every Model Hierarchy](https://skills.every.to/skills/model-hierarchy)、[OpenAI Practical Guide](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)、[Swarmia 五级自治](https://www.swarmia.com/blog/five-levels-ai-agent-autonomy/)
