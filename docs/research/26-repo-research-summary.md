# 26+ 仓库调研整合报告

> 日期: 2026-05-27 | 版本: 4.0 | 关联设计: spec/claude-config-integration/design-v4.md

---

## 调研方法

29 并行 Agent 分析 26+ 仓库 + 本地配置审计，产出 42 项发现（5 P0 + 25 P1 + 12 P2），驱动 7 层增量实施。

---

## 五柱骨架（5）

| # | 仓库 | 版本 | 核心吸收 | 落地 |
|---|------|------|----------|------|
| 1 | **obra/superpowers** | 5.1.0 | 13 skill 链 + HARD-GATE + 双阶段审查 + SessionStart bootstrap | skills/×13, hooks/, P0 4 skill |
| 2 | **gsd-build/get-shit-done** | latest | 上下文工程 + 三级阈值 + read-before-edit + phase 工作流 | rules/CONTEXT.md, templates/planning/ |
| 3 | **Fission-AI/OpenSpec** | latest | proposal→spec→tasks delta 格式 + brownfield + archive | templates/openspec/, spec-validation skill |
| 4 | **garrytan/gstack** | latest | 5 角色审查 + 7 角色补全 + 浏览器 QA + autoplan/ship | agents/×12, skills/autoplan,ship |
| 5 | **thedotmack/claude-mem** | latest | 渐进式披露 + 向量搜索 + 6 hook SSOT + SEMANTIC_INJECT | plugins/marketplaces/thedotmack/ |

---

## 结构格式（6）

| # | 仓库 | 核心吸收 | 落地 |
|---|------|----------|------|
| 6 | **affaan-m/ECC** | MANIFEST concern→owner→excludes 防互博 + instinct-learning + hook profile | MANIFEST.yaml, agent.yaml, catalog/ |
| 7 | **anthropics/skills** | SKILL.md 格式标准 + 跨平台 + 渐进披露 | writing-skills skill，所有 SKILL.md frontmatter |
| 8 | **shanraisshan/best-practice** | 80+ 提示词 + 10+ 方法论 + 编排模式 + lazy-load | rules/BESTPRACTICE.md |
| 9 | **forrestchang/karpathy** | 四原则 + LLM 失效模式对策 | karpathy-guidelines skill, rules/CORE.md |
| 10 | **mattpocock/skills** | triage 分诊 + grill 反推 + improve-codebase-architecture | skills/triage, improve-codebase-architecture |
| 11 | **VoltAgent/awesome-design-md** | 9 节结构 + 73 品牌 + 零依赖 + YAML token | rules/DESIGN.md, templates/DESIGN.md |

---

## 优化工具（4）

| # | 仓库 | 核心吸收 | 落地 |
|---|------|----------|------|
| 12 | **rtk-ai/rtk** | Rust CLI 60-90% token 压缩 + 100+ 命令预置 | hooks/pre-rtk-rewrite.py |
| 13 | **JuliusBrussee/caveman** | 四级压缩(L1-L4) + 仅压输出 + 学术佐证 | skill/caveman-compress |
| 14 | **github/github-mcp-server** | 20+ tool + Enterprise + 精细权限 | .mcp.json (gh) |
| 15 | **anthropics/claude-code-action** | 4 后端 CI + 结构化 JSON 输出 | templates/github-actions/ |

---

## 编排增强（4）

| # | 仓库 | 核心吸收 | 落地 |
|---|------|----------|------|
| 16 | **eyaltoledano/task-master** | PRD→结构化任务 + 3 级工具裁剪 | templates/taskmaster/ |
| 17 | **nextlevelbuilder/ui-ux-pro-max** | 67 风格 + 161 色板 + 99 UX 指南 | catalog/skills/ui-ux-pro-max |
| 18 | **zilliztech/claude-context** | Milvus + BM25 + 40% token 节省 | .mcp.json optional 分组 |
| 19 | **bytedance/deer-flow** | 渐进式加载 + Docker 沙箱 + DAG 四阶段 + middleware chain | rules/WORKFLOW.md |

---

## 参考索引（5）

| # | 仓库 | 核心吸收 | 落地 |
|---|------|----------|------|
| 20 | **ComposioHQ/awesome-claude-skills** | 1000+ 技能索引 + 渐进式加载模式 | catalog/ 索引 |
| 21 | **hesreallyhim/awesome-claude-code** | 配置范式 + 工具发现 | 外链索引 |
| 22 | **x1xhlol/system-prompts** | 30+ 提示词比较 + 注入防护 | BESTPRACTICE 原则 |
| 23 | **Chalarangelo/30-seconds-of-code** | 多语言代码片段 | catalog 参考 |
| 24 | **ruvnet/ruflo** | 蜂群拓扑 + HNSW 加速 + 3-Tier Model Routing | 概念吸收→WORKFLOW.md |

---

## 安全补强（4）

| # | 仓库 | 核心吸收 | 落地 |
|---|------|----------|------|
| 25 | **trailofbits/claude-code-config** | /sandbox + deny + 三层防御 | SECURITY.md §11 |
| 26 | **dwarvesf/claude-guardrails** | 密钥扫描 hook | hooks/_optional/ |
| 27 | **lasso-security/claude-hooks** | 注入扫描 hook | hooks/_optional/ |
| 28 | **marc-shade/claude-code-security** | 渐进硬化 checklist | SECURITY.md §14 |

---

## 关键发现（42项）

### P0 (5) — 已全部修复
1. ~~settings.json API token 硬编码~~ → 跳过（用户 cc-switch 管理）
2. claude-mem 模型对齐（MEM_MODEL/MODE/CHROMA 等 8 环境变量）→ 已添加
3. CLAUDE_MCP_PROFILE 缺失 → 已添加 "dev"
4. stop-quality-gate.py L22 裸 except:pass → 已修复
5. .mcp.json @github/mcp-server 包不存在 → 已修复为 @modelcontextprotocol/server-github

### P1 (25) — 核心已落地
- SPEC.md 仓库计数修正（25→28）
- R1-R11 循环引用修复（CLAUDE.md ← → CORE.md）
- CLAUDE.md 命令表去重（8→8 保留，无重复）
- MANIFEST 命名统一（version 3.0→4.0, source 字段更新）
- CONTEXT.md 三级阈值精确化（<40%/50%/70%）
- WORKFLOW.md DAG 编排四阶段确认完整
- AGENTS.md 禁止项扩展到 7 条
- SECURITY.md 孤立的 ``` 修复
- pre-manifest-validator plugin vs skill 互斥检测
- pre-context-injector 三态制品加载
- stop-pattern-extraction DAG 模式提取
- pre-compact-state openspec 快照

### P2 (12) — 记录待后续
- Agent tools 字段审查
- catalog/ 规模更新（skills ~120）
- _optional hooks 治理
- gotchas.md 实例化
- gstack 角色间 overlap 审查

---

## 架构公式（v4.0 确认）

```
RUNTIME = superpowers(methodology) + GSD(context) + OpenSpec(spec) + gstack(review) + claude-mem(memory)
STRUCTURE = ECC(manifest) + anthropics/skills(format) + best-practice(entry)
OPTIMIZATION = RTK(shell) + caveman(output)
REVIEW = gstack 5角色 + gstack 7补全
```

## 规模约束（v4.0 实际）

| 类型 | 上限 | 实际 | 状态 |
|------|------|------|------|
| skills | ≤28 | 27 | ✅ |
| agents | ≤22 | 20 | ✅ |
| rules | 10 | 10 | ✅ |
| CLAUDE.md | ≤300行 | ~260 | ✅ |
| hooks | 15 | 15 | ✅ |
| 仓库覆盖 | 26+ | 28 | ✅ |

## 关联文档

- 设计: `spec/claude-config-integration/design-v4.md`
- 实施计划: `docs/superpowers/plans/2026-05-27-five-pillar-v4.md`
- 需求规格: `spec/claude-config-integration/spec.md`
- 合规检验: `spec/claude-config-integration/compliance.md`
- 会话记录: `projects/C--Users-DELL--claude/`
