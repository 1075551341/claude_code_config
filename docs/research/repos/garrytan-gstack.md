# garrytan/gstack（包 1.58.x / CLI 0.19）

> 层: 五柱(审查) | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub CHANGELOG + PR + repo 双源交叉
>
> **版本说明**：CLI 自述 `v0.19`（binary 标识），npm/package 实际为 **1.58.1.0**（2026-06-14）。两套编号并存，本地以 CLI 行为为准。

## 核心价值

- **40+ 角色矩阵**（非 23）：Think/Plan(10) → Build/Review(10) → Test/QA(7) → Ship/Deploy(5) → Document/Reflect(5) → iOS(5) → Tools(5) → Auxiliary(3)
- **审查智能路由**：8 核心（eng/ceo/design/dx/qa/security/ios/codex）+ 7 补充，按 diff 内容自动路由
- **6 层 ML 注入防御**（非 3 层）：datamarking → 隐藏元素 stripping → ARIA/URL blocklist → BERT-small ONNX(22MB,本地) → Haiku 转录 → Canary token → Ensemble 裁决
- **Taste-Memory 跨会话学习**：`~/.gstack/projects/$SLUG/learnings.jsonl`，置信度评分 + 来源归属 + 5%/周衰退
- **Design-Shotgun**：4-6 AI mockup 变体 + 浏览器比较板 + GPT-4o vision 质量门控 + 多轮精炼
- **Land-and-Deploy**：`/setup-deploy → /ship → /land-and-deploy → /canary` 完整闭环
- **Pair-Agent**：双监听器（local + ngrok tunnel），三层 token 权限，26 命令 allowlist，tab 隔离

## 三大设计哲学（ETHOS.md）

1. **Boil the Ocean**：AI 时代的最后 10% 边际成本是秒级，永远选完整版而非 90% 方案
2. **Search Before Building**：三层知识（久经考验/新流行/第一性原理）；zig while others zag
3. **User Sovereignty**："AI 推荐，用户决定"；generation-verification loop

## 810× 方法论实证

- 2026 年：11,417 逻辑 SLOC/天（108 天项目）
- 2013 年：14 LOC/天
- 2.0% revert rate；AI-verbose 压缩后等效 408×

## 审查路由规则

```
所有变更 → eng-reviewer (硬关卡)
后端变更 → 跳过 design-review
UI 变更 → +designer + dx-reviewer
安全敏感 → +security-reviewer + cso(OWASP+STRIDE)
iOS → +ios-specialist (QA/fix/design-review/clean/sync)
跨模型 → +codex-reviewer (独立模型盲点检测)
新功能/产品 → +ceo-reviewer
/autoplan → CEO→Design→Eng→DX 自动串联
```

## ML 注入防御（6 层，非 3 层）

| 层 | 机制 | 详情 |
|----|------|------|
| L1 | 内容安全 | datamarking + 隐藏元素 stripping |
| L2 | ARIA/URL blocklist | 已知恶意模式过滤 |
| L3 | 结构性过滤 | DOM 树异常检测 |
| L4 | TestSavantAI BERT-small ONNX | 22MB，本地运行，零网络调用 |
| L4b | Claude Haiku 转录检查 | 低成本快速扫描，异常即熔断 |
| L5 | Canary token | 注入诱饵 token，触发即确定性阻断 |
| L6 | Ensemble 裁决 | L4 AND L4b 都 >= 0.75 才 BLOCK |
| 可选 L4c | DeBERTa-v3 | 721MB，`GSTACK_SECURITY_ENSEMBLE=deberta` 启用 |

## Taste-Memory 机制

```
~/.gstack/projects/$SLUG/learnings.jsonl
  ├── 置信度评分 (0.0-1.0)
  ├── 来源归属 (哪个审查/讨论)
  ├── 引用文件路径
  ├── 5%/周自然衰退
  └── gstack-taste-update CLI 写入品味 profile
```

其他 skill 推荐前自动搜索先前学习。跨机器通过 gbrain 同步。

## 本地映射

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| gstack_review | `rules/AGENTS.md`, `agents/` (25 agents) | ✅ 已落地 |
| gstack_dx | `agents/dx-reviewer.md` | ✅ |
| gstack_eng/ceo/designer/qa/security | `agents/*.md` | ✅ |
| gstack_codex | `agents/codex-reviewer.md` | ✅ |
| gstack_ios | `agents/ios-specialist.md` | ✅ |
| gstack_cso | `agents/cso.md` | ✅ |
| 审查路由 | `CLAUDE.md` + `rules/AGENTS.md` | ✅ |
| taste-memory | claude-mem observation + `skills/taste-memory/` | ✅ 指针 |
| design-shotgun | `agents/design-shotgun.md` | ✅ agent |
| land-and-deploy | `agents/land-and-deploy.md` | ✅ agent |
| pair-agent | `agents/pair-agent.md` | ✅ agent |
| autoplan | `skills/autoplan/` | ✅ |
| ship | `skills/ship/` | ✅ |
| ML defense | `rules/SECURITY.md` §15 | 🟡 仅文档了 3 层，需更新到 6 层 |
| gstack_learn | `rules/WORKFLOW.md` §Learn | ✅ |
| office-hours | `skills/office-hours/` | ✅ |

## 吸收优先级

| 优先级 | 内容 | 理由 |
|--------|------|------|
| P0 | 审查智能路由（已落地） | MANIFEST concern 路由规则 |
| P0 | ML 注入防御（6 层文档补全） | 当前 SECURITY.md 仅 3 层 |
| P1 | Taste Memory 运营化 | 依赖业务触发，当前 P2 跟踪 |
| P2 | Continuous Checkpoint | workflow 已有 checkpoints |
| P2 | Document Release | doc-writer agent 等效 |
| 不吸收 | Browser daemon | chrome-devtools MCP 等效 |
| 不吸收 | gbrain 同步 | claude-mem 等效 |
| 不吸收 | Conductor | agentic-orchestrator 等效 |

## 互博检查

- vs compound-engineering：`[plugin/compound-engineering, gstack_review]` — 已禁用 compound-engineering
- vs ui-ux-pro-max：gstack 流程管线；uupm 设计库 catalog 补充
- vs agentic-orchestrator：gstack Conductor 不吸收，本地 agentic-orchestrator 等效

## v10.2 增量（vs v10.1）

- 40+ 角色矩阵补充文档（原标注 23）
- ML 注入防御 6 层全量文档化（原 3 层）
- Taste-Memory 衰退机制明确化（5%/周）
- 810× 方法论实证数据补充

## v10.2.1 增量（双源刷新 2026-06-19）

- **版本号体系修正**：CLI `v0.19` 与 package `1.58.1.0` 并存（本地以 CLI 行为为准）
- **Codex 审查默认开启**（1.57.10.0）：`codex_reviews` 主开关，覆盖 `/review` `/ship` 四个 plan-review + `/document-release` + `/autoplan`；缺失/未登录时降级 Claude subagent（一行原因，不静默跳过）→ 对齐本地 `codex-reviewer` 路由「默认参与」
- **重技能懒加载**（1.56.0.0）：5 个最重 skill（plan-ceo/eng/design/devex-review + office-hours）改为「常驻骨架 + 按需 sections/ STOP-Read」→ 本地重 skill 可借鉴此模式
- **plain-text 兜底**：问题选择器中断时降级纯文本提问（与本地 brainstorming #1773 守卫策略一致：交互工具非强制）
