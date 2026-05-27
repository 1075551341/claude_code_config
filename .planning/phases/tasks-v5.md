# Tasks v5.0 — 五柱整合实施

> 基于 design-v5.md | 按层分波，每波独立可验证

## DAG 依赖图

```
Wave1 (无依赖，并行)
├─ T1: GitHub MCP 迁移 [MCP]
├─ T2: ChromaDB 配置统一 [claude-mem]
├─ T3: 停用 stop-pattern-extraction v1 [hook]
├─ T4: 卸载 8 插件 + 禁用 3 插件 [plugins]
├─ T5: OpenSpec 路径修复 specs/→openspec/changes/ [commands]
└─ T6: CONTEXT.md 补全 canonical-source + trust-but-verify [rule]

Wave2 (依赖 Wave1 完成)
├─ T7: BESTPRACTICE.md 50→200行扩展 [rule]
├─ T8: karpathy-guidelines +实施规则 [skill]
├─ T9: triage +状态机模型 [skill]
├─ T10: qa.md +互斥声明 [agent]
└─ T11: improve-codebase-architecture 重写 [skill]

Wave3 (依赖 Wave2 完成)
├─ T12: brainstorming 重写 (一次一问+Red Flags) [skill]
├─ T13: writing-plans 重写 (原子任务) [skill]
└─ T14: subagent-driven-development 重写 (两阶段审查) [skill]

Wave4 (依赖 Wave3 完成)
├─ T15: ui-ux-pro-max 数据补全 [catalog]
├─ T16: SPEC.md + MANIFEST.yaml + catalog REGISTRY.csv 更新 [index]
└─ T17: CLAUDE.md 精简 ≤280行 [路由层]

Wave5 (收尾)
├─ T18: 删除 4 冗余文件
├─ T19: 全量验证 (MANIFEST一致性+sync+需求逐条)
└─ T20: 学习 loop 钩子确认
```

---

## Wave1: 基础设施修复 (并行)

### T1: GitHub MCP 迁移
- **文件**: `.mcp.json`
- **操作**: 替换 `gh` 条目，`@modelcontextprotocol/server-github` → `github/github-mcp-server`，添加 `--toolsets all`
- **验证**: `gh --version` 或检查 MCP 工具列表包含 80+ tools

### T2: ChromaDB 配置统一
- **文件**: `settings.json` env.CLAUDE_MEM_CHROMA_ENABLED
- **操作**: `false` → `true`，与 `~/.claude-mem/settings.json` 一致
- **验证**: claude-mem 重启后 Chroma 向量搜索可用

### T3: 停用 stop-pattern-extraction v1
- **文件**: `settings.json` hooks.Stop
- **操作**: 删除 stop-pattern-extraction 的 hook 注册条目
- **验证**: Stop hook 列表不再包含该条目

### T4: 插件精简
- **文件**: `settings.json` enabledPlugins + `plugins/installed_plugins.json`
- **操作**: 
  - `frontend-design`, `code-review`, `feature-dev` → false
  - 卸载 context7/github/chrome-devtools-mcp/playwright/security-guidance/firecrawl/ralph-loop/typescript-lsp
  - 更新 installed_plugins.json
- **验证**: `/plugin` 列表仅显示 6 个插件

### T5: OpenSpec 路径修复
- **文件**: `commands/propose.md`, `commands/apply.md`, `commands/archive.md`
- **操作**: 所有 `specs/` → `openspec/changes/`
- **验证**: grep 确认无残留 `specs/` 路径

### T6: CONTEXT.md 补全
- **文件**: `rules/CONTEXT.md`
- **操作**: 新增 Canonical Source Precedence 规范 + Trust-But-Verify 纪律段
- **验证**: 包含"规范文档 > ADR > CONTEXT.md > Agent记忆"链和"不信任Agent自述"规则

---

## Wave2: 规则与轻量补全 (并行)

### T7: BESTPRACTICE.md 扩展
- **文件**: `rules/BESTPRACTICE.md`
- **操作**: 从 ~50 行扩展到 ~200 行，15 类别：错误处理/提示词/代码精炼/API/日志/会话管理/上下文/Skills设计/Hooks/Git与PR/调试/编排/输出/安全/记忆
- **验证**: 15 类别标题完整，各节有实质性内容

### T8: karpathy-guidelines 补全
- **文件**: `skills/karpathy-guidelines/SKILL.md`
- **操作**: 四原则各自增加实施规则，补量化测试(200行→50行)、孤儿清理边界、弱命令转换表
- **验证**: SKILL.md 从 ~10 行扩展到 ~40 行，四个原则各有可执行规则

### T9: triage 补全
- **文件**: `skills/triage/SKILL.md`
- **操作**: 保留 P0-P3 分级，补充状态机模型(needs-triage/needs-info/ready-for-agent/ready-for-human/wontfix)
- **验证**: 包含状态迁移流描述

### T10: qa agent 互斥声明
- **文件**: `agents/qa.md`
- **操作**: 新增互斥声明段："不负责覆盖率评估（→ eng-reviewer），只负责边界用例与回归风险"
- **验证**: 声明存在且明确

### T11: improve-codebase-architecture 重写
- **文件**: `skills/improve-codebase-architecture/SKILL.md`
- **操作**: 补全 8 术语表(Module/Interface/Implementation/Depth/Seam/Adapter/Leverage/Locality)、删除测试原则、HTML报告生成、Grilling Loop
- **验证**: 术语表完整，流程含 Explore→Report→Grill→Update

---

## Wave3: Superpowers 三大件重写 (并行)

### T12: brainstorming 重写
- **文件**: `skills/brainstorming/SKILL.md`
- **操作**: 
  - 保留 HARD-GATE + 三方案对比
  - 补回：一次一问纪律、Red Flags 表（10条反借口）、用户审核门、visual companion 提示
  - 硬流转：终态必须 writing-plans
- **验证**: Red Flags 表 ≥8 条，流转逻辑完整

### T13: writing-plans 重写
- **文件**: `skills/writing-plans/SKILL.md`
- **操作**:
  - 原子任务模式：2-5分钟可完成、精确文件路径+完整代码+验证命令
  - 计划自审清单（覆盖/占位/类型一致性）
  - 执行握手（子代理驱动 vs 内联执行选择）
  - 三轨选择逻辑保留（openspec / phases / spec）
- **验证**: 任务模板含路径/代码/验证三个必填字段

### T14: subagent-driven-development 重写
- **文件**: `skills/subagent-driven-development/SKILL.md`
- **操作**:
  - 两阶段审查：先 spec 合规 → 后代码质量
  - 连续执行协议：不问"是否继续"
  - 状态机：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
  - DAG 依赖图规则保留
  - 与 writing-plans 原子任务对接
- **验证**: 审查流程含两个阶段，状态机四种状态

---

## Wave4: 索引与路由更新 (并行)

### T15: ui-ux-pro-max 数据补全
- **文件**: `catalog/skills/ui-ux-pro-max/`
- **操作**: 从源仓库拉取 data/*.csv (67风格+161色板+99UX) + scripts/search.py
- **验证**: 目录含数据文件，search.py 可执行

### T16: SPEC.md + MANIFEST.yaml + REGISTRY.csv 更新
- **文件**: `SPEC.md`, `MANIFEST.yaml`, `catalog/REGISTRY.csv`
- **操作**:
  - SPEC.md: 规模约束表刷新、仓库映射更新(v4.0→v5.0)，补新增的审查仓库
  - MANIFEST.yaml: version 5.0，新增 concerns (canonical_source/trust_but_verify/triage_state/qa_boundary)，补全 excludes
  - REGISTRY.csv: 生成 catalog 全量索引（技能名/分类/来源/版本/采纳日期）
- **验证**: SPEC 规模数字与实际一致，MANIFEST concerns 数 ≥ 组件数

### T17: CLAUDE.md 精简
- **文件**: `CLAUDE.md`
- **操作**:
  - 更新版本号 v4.0→v5.0
  - 三层架构(骨架/执行/护栏)替换原二层
  - SDD+TDD 组合执行段
  - 命令速查去重
  - 确保 ≤280 行
- **验证**: wc -l ≤280，架构描述与 design-v5.md 一致

---

## Wave5: 清理与最终验证 (顺序)

### T18: 删除冗余文件
- **删除**: `agents/context-manager.md`, `hooks/stop-pattern-extraction.py`, `hooks/post-operation-log.py`, `hooks/pre-config-protection.py`
- **验证**: ls 确认文件已删除

### T19: 全量验证
- MANIFEST.yaml concerns 与实际组件一一对应（无孤立/无重复）
- 防互博速查表覆盖新增内容
- sync.ps1 确认同步项不变
- 需求逐条对照 design-v5.md 验证清单

### T20: 学习 loop 钩子确认
- PreCompact hook 正确触发 pre-compact-state
- Stop hooks: quality-gate + session-summary + readme-updater + instinct-learning v2
- instinct-learning 的 experiences/patterns/ 目录可写入
