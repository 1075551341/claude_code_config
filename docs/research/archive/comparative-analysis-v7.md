# 仓库对比分析 & 集成建议 v7.0

> 日期: 2026-06-07

---

## 1. 五柱核心仓库 (P0 — 必须深度集成)

| 仓库 | 角色 | 版本 | 集成级别 | 关键动作 |
|------|------|------|----------|----------|
| obra/superpowers | 方法论 | 5.1.0 | ✅ 已集成 | 维持本地精简版覆盖 |
| open-gsd/gsd-core | 上下文工程 | latest | ⚠️ 概念吸收 | 跟踪新仓库更新 |
| Fission-AI/OpenSpec | 规格格式 | 1.4.1 | ⚠️ 部分集成 | 安装 CLI, 集成 opsx |
| garrytan/gstack | 角色 Agent | 0.19 | ⚠️ 部分集成 | 补充缺失角色 agent |
| thedotmack/claude-mem | 跨会话记忆 | 6.5.0/13.4.0 | ✅ 已集成 | 启用 Chroma + Endless Mode |

---

## 2. 治理 & 编排 (P1 — 核心基础设施)

| 仓库 | 关键价值 | 集成状态 | 建议动作 |
|------|----------|----------|----------|
| affaan-m/ECC | MANIFEST 防互博 + hook 分级 + 选择性安装 | ✅ MANIFEST.yaml 已落地 | 跟踪 ECC 2.0 Rust 控制平面 |
| bytedance/deer-flow | LangGraph 编排 + 四执行模式 + Docker 沙箱 | ⚠️ 概念吸收到 WORKFLOW.md | 考虑作为外部编排引擎 |

---

## 3. 优化工具 (P1 — 日常使用)

| 仓库 | 节省效果 | 集成状态 | 建议动作 |
|------|----------|----------|----------|
| rtk-ai/rtk | 60-90% shell token | ✅ pre-rtk-rewrite hook | 更新到最新版 |
| JuliusBrussee/caveman | ~75% 输出 token | ✅ caveman-compress skill | 考虑 ultra/wenyan 模式 |
| colbymchenry/codegraph | 47% token, 58% 调用减少 | ✅ MCP 已配置 | 确保所有项目 codegraph init |
| Lum1104/Understand-Anything | 概念级知识图 | ✅ MCP 已配置 | 定期 /understand --review |

---

## 4. 技能 & 最佳实践 (P1 — 内容增强)

| 仓库 | 核心贡献 | 吸收方式 |
|------|----------|----------|
| anthropics/skills | SKILL.md 格式标准 + 官方示例 | 格式已采用，可参考示例 |
| shanraisshan/claude-code-best-practice | lazy-load 规则 + `<important if>` 触发 | 规则系统已借鉴 |
| mattpocock/skills | grill 反推 + 共享语言 + triage 分诊 | 已集成 triage/grill 概念 |
| forrestchang/andrej-karpathy-skills | 四原则 + LLM 失效模式 | 已集成到 CORE.md |
| 2025Emma/vibe-coding-cn | 道法术器 + α/Ω 元技能 | 已集成到 CORE.md |

---

## 5. 设计 & 参考 (P2 — 按需使用)

| 仓库 | 核心贡献 | 建议 |
|------|----------|------|
| eyaltoledano/claude-task-master | MCP 任务管理 | 按需参考 |
| VoltAgent/awesome-design-md | DESIGN.md 标准 | 有 DESIGN.md 时参考 |
| nextlevelbuilder/ui-ux-pro-max-skill | 设计系统生成器 | 作为 catalog skill |
| ComposioHQ/awesome-claude-skills | 1000+ skills 索引 | 作为发现目录 |
| hesreallyhim/awesome-claude-code | 45.7k stars 资源索引 | 作为外部参考 |
| Chalarangelo/30-seconds-of-code | 代码片段参考 | 作为 catalog 参考 |
| x1xhlol/system-prompts | 提示词设计实证 | 已吸收到 BESTPRACTICE |
| ruvnet/ruflo | 蜂群拓扑概念 | 仅概念参考 |

---

## 6. CI/CD & 外部集成 (P2)

| 仓库 | 用途 | 建议 |
|------|------|------|
| github/github-mcp-server | GitHub API 集成 | ✅ 已配置 |
| anthropics/claude-code-action | CI/CD 自动化 | 按需使用 |
| zilliztech/claude-context | 向量上下文增强 | 按需启用 (需 Milvus) |

---

## 7. 去重分析

### 功能重叠 & 处理

| 重叠领域 | 涉及仓库 | 决策 |
|----------|----------|------|
| 任务规划 | superpowers/writing-plans vs task-master | 优先 superpowers (更成熟) |
| 代码审查 | gstack/review vs ECC eng-reviewer | gstack 集成 ECC agent 定义 |
| UI 设计 | gstack/design-review vs ui-ux-pro-max | gstack 管流程, uupm 管设计库 |
| Agent 编排 | superpowers/subagent vs deer-flow vs ruflo | deer-flow 做外部编排, superpowers 做内部编排 |
| 记忆 | claude-mem vs GSD context vs claude-context | claude-mem 做主记忆, GSD 管上下文策略 |
| Shell 压缩 | RTK vs caveman | RTK 压缩输入 (shell), caveman 压缩输出 |
| 代码探索 | codegraph vs Understand-Anything | codegraph 查结构, UA 查概念 |

### 防互博规则 (基于 ECC MANIFEST)

```
同一任务禁止: planner + agentic-orchestrator 同时编排
同一制品禁止: 两个 agent 并行写入同一路径
技能触发禁止: 多个 skill 声称同一触发条件
```

---

## 8. 优先级排序 (实施建议)

### 立即 (本轮 /plan)
1. 安装 OpenSpec CLI (`@fission-ai/openspec`)
2. 补充 gstack 缺失角色 agent (design-shotgun, pair-agent, land-and-deploy)
3. 更新 CLAUDE.md 集成 gstack 完整角色引用
4. 优化 rules/ 触发条件匹配度

### 短期 (本周)
1. 启用 claude-mem Chroma 向量搜索
2. 确保所有项目 codegraph init
3. 测试 deer-flow 作为可选编排引擎
4. 更新 sync.ps1 覆盖新 agent

### 中期 (本月)
1. 跟踪 ECC 2.0 Rust 控制平面
2. 评估 caveman ultra 模式
3. 集成 gstack 品味记忆机制
4. opsx archive 集成到 workflow

### 长期 (持续)
1. 跟踪 open-gsd/gsd-core 更新
2. 社区贡献反哺
3. 模式提取 & 持续学习
