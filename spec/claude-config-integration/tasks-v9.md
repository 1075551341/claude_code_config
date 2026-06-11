# .claude 配置更新实施计划

> 基于: 01-ANALYSIS.md + 02-DESIGN.md | 版本 v9.0 | 优先级: P0>P1>P2>P3

---

## 概览

```
总任务数: 28
P0 关键(≤1h): 8个  — 直接修复缺口
P1 重要(≤2h): 8个  — 新功能添加
P2 优化(≤4h): 8个  — 质量提升
P3 长期(可选): 4个  — 探索性改进
```

---

## P0 — 关键任务（立即执行）

### T01: 更新 CLAUDE.md 工具路由策略 ⚡
**目标**: 将 codegraph 提升为代码探索首选，添加 claude-mem 记忆路由
**文件**: `CLAUDE.md`
**变更**:
```markdown
# 旧
搜索策略：技术文档→Context7 MCP；外部信息→Firecrawl/Exa；代码结构→codegraph；概念理解→Understand-Anything

# 新
搜索策略（四轨）:
- 代码结构探索 → codegraph_explore（首选）→ Grep fallback
- 项目全貌理解 → understand-anything /understand-chat
- 外部技术文档 → Context7 MCP
- 外部信息/调研 → Firecrawl(爬取) + Exa(语义)
- 历史记忆查询 → claude-mem search（先于重复文件读取）
```
**验证**: 下次会话执行代码探索时默认调用 codegraph_explore

---

### T02: 添加铁律 R17-R18 ⚡
**目标**: 正式化 codegraph 优先和 claude-mem 优先规则
**文件**: `CLAUDE.md` + `rules/CORE.md`
**内容**:
```markdown
R17 | 代码探索 | 探索代码先调用 codegraph_explore，次选 Grep
R18 | 记忆优先 | 历史上下文先查 claude-mem，避免重复分析文件
```
**验证**: grep "R17" CLAUDE.md rules/CORE.md 均有结果

---

### T03: 修复 context-monitor hook（升级为 GateGuard 模式）⚡
**目标**: 增加 tool loop 检测 + scope creep 警告 + 成本估算
**文件**: `hooks/context-monitor/` 或对应 hooks.json 条目
**变更**:
```json
{
  "checks": [
    "context_percent > 70% → 警告择机压缩",
    "context_percent > 90% → 强制 /compact",
    "same_tool_call_count > 3 → loop警告",
    "task_drift_detected → scope_creep警告",
    "estimated_cost > threshold → 成本警告（可ECC_CONTEXT_MONITOR_COST_WARNINGS=off关闭）"
  ]
}
```
**验证**: 模拟 tool loop 触发警告

---

### T04: 增强 pre-compact hook（ECC PreCompact模式）⚡
**目标**: 压缩前保存工作状态，防止 /compact 后丢失上下文
**文件**: `hooks/pre-compact/` 或对应条目
**保存内容**:
```json
{
  "current_task": "任务摘要",
  "in_progress_files": ["path1", "path2"],
  "pending_decisions": ["决策1"],
  "last_checkpoint": "最后验证点描述"
}
```
**保存路径**: `.claude/state.json`（跨会话持久化）
**验证**: 执行 /compact 后检查 .claude/state.json 是否生成

---

### T05: 添加 codegraph post-edit hook ⚡
**目标**: Write/Edit后触发增量 codegraph sync
**文件**: `hooks/post-tool-use/codegraph-sync.js`
**触发条件**: 变更文件数>3 OR 变更包含 .ts/.tsx/.js/.py
**命令**: `codegraph sync --incremental`
**验证**: 编辑文件后 .codegraph/ 时间戳更新

---

### T06: 更新 CLAUDE.md 版本为 v9.0 ⚡
**目标**: 版本号+日期+变更记录更新
**文件**: `CLAUDE.md`
**内容**:
```markdown
> 五柱 × 五阶段 × 三横切。路由 → SPEC.md | 归属 → MANIFEST.yaml | 版本：v9.0

五柱：Superpowers v5.1.0 | GSD v1.42.3 | OpenSpec v1.4.1 | gstack v0.19 | claude-mem v13.4.0
新增：codegraph优先路由(R17) + claude-mem记忆路由(R18) + GateGuard增强 + DX审查
```
**验证**: version字段为 v9.0

---

### T07: 添加 dx-reviewer agent ⚡
**目标**: 补充开发体验审查视角（TTHW/摩擦点/魔法时刻）
**文件**: `agents/dx-reviewer.md`
**内容**:
```markdown
# DX Reviewer
角色: 开发体验工程师
视角: Time-To-Hello-World / 魔法时刻 / 摩擦点识别 / Persona tracing
触发: UI/UX变更 + 新功能 + API设计
职责:
  1. 测量 TTHW（首次运行时间）
  2. 识别摩擦点（≥3步骤才能完成的操作）
  3. 记录魔法时刻（"哇原来这么简单"的体验）
  4. Persona trace（从不同用户视角走一遍流程）
审查不修改代码，仅出具 DX report
```
**验证**: 在审查路由中 UI/UX 变更触发 dx-reviewer

---

### T08: 更新审查路由（增加 dx-reviewer）⚡
**目标**: CLAUDE.md 审查路由表添加 dx-reviewer 触发条件
**文件**: `CLAUDE.md`
**变更**:
```markdown
UI/UX 变更   → + designer + dx-reviewer    # 新增 dx-reviewer
DX体验变更   → + dx-reviewer               # 新增行
```
**验证**: grep "dx-reviewer" CLAUDE.md 有结果

---

## P1 — 重要任务（近期执行）

### T09: 创建 workstream-management skill
**目标**: 支持 GSD v1.42.3 风格的并行任务流
**文件**: `skills/workstream-management/SKILL.md`
**功能**:
```markdown
## 并行任务流管理
基于 git worktrees 的并行开发隔离

触发词: 并行任务、多任务同时、工作流/workstream
触发时机: 需要同时推进2+个独立任务

流程:
1. /workstream new <name>  → git worktree add + .planning/phases/<name>/
2. /workstream status      → 列出所有活跃流状态
3. /workstream merge <name> → PR + claude-mem 整合记忆
4. /workstream list        → 查看所有流（含已完成）

约束:
- 每个 workstream 独立 git branch
- workstream 内 claude-mem 自动隔离（platform_source）
- 合并时触发 verification-before-completion
```
**验证**: 创建 workstream → git worktree ls 可见

---

### T10: 创建 adr-management skill
**目标**: 架构决策记录，防止重复讨论已决定的技术选型
**文件**: `skills/adr-management/SKILL.md`
**功能**:
```markdown
## ADR（架构决策记录）管理
位置: docs/ADR/YYYY-MM-DD-<kebab-title>.md

触发词: 架构决策、技术选型、为什么用X不用Y、ADR
触发时机: 做出影响架构的决策时

ADR格式:
  # ADR-NNNN: <标题>
  状态: [提议/已采纳/已废弃]
  背景: 为什么需要做这个决策
  决策: 我们决定...
  后果: 正面/负面影响
  替代方案: 考虑过的其他选项

命令:
  /adr new <title>     → 创建新ADR
  /adr list            → 列出所有ADR
  /adr search <query>  → 搜索相关ADR（before重复讨论）
```
**验证**: 创建 ADR → docs/ADR/ 目录中有对应文件

---

### T11: 添加 sync.sh（Linux/macOS 同步脚本）
**目标**: 替代 Windows-only 的 sync.ps1，支持跨平台同步
**文件**: `scripts/sync.sh`
**功能**:
```bash
#!/bin/bash
# 用法: ./sync.sh [index|full] [cursor|windsurf|vscode|zed]
# 索引模式: 软链接（默认）
# 全量模式: 格式转换+软链接
```
**验证**: 在 macOS/Linux 上执行后 Cursor 能加载 CLAUDE.md

---

### T12: 更新 rules/OPENSPEC.md（新增）
**目标**: 补充 OpenSpec delta-spec 使用规范
**文件**: `rules/OPENSPEC.md`
**内容**:
```markdown
# OpenSpec 使用规范
## 核心概念
- delta specs: 只描述变化，不重写全量
- 四大制品: proposal.md / specs/ / design.md / tasks.md
- brownfield优先: 在现有代码基础上增量变更

## 命令用法
- /opsx:propose <idea>  → 创建 openspec/changes/<id>/
- /opsx:ff              → 快进创建所有制品
- /opsx:apply           → 按 tasks.md 实现
- /opsx:archive         → 归档到 archive/

## 触发条件
- 新功能 ≥ 3个文件变更 → 使用 OpenSpec
- 小修复 < 3个文件 → 使用轻量 spec/
- 多阶段大功能 → 使用 GSD + workstreams

## 禁止事项
- 禁止跳过 proposal.md 直接写 tasks.md
- 禁止 apply 前未经用户确认 design.md
```
**验证**: `rules/OPENSPEC.md` 存在，文件 > 20行

---

### T13: 更新 skills-INDEX.md（添加新技能）
**目标**: 同步添加 workstream-management / adr-management / onboarding-guide
**文件**: `skills-INDEX.md`
**变更**: 在表格末尾添加3行新技能记录
**验证**: 技能总数从29→32

---

### T14: 更新 agents-INDEX.md（添加 dx-reviewer）
**目标**: 添加 dx-reviewer 到代理索引
**文件**: `agents-INDEX.md`
**变更**: 添加 dx-reviewer（审查类，🟡审查）
**验证**: 代理总数从24→25

---

### T15: 创建 ADR-001（本次配置集成决策）
**目标**: 记录本次 v8.1→v9.0 升级的关键架构决策
**文件**: `docs/ADR/2026-06-10-v9-config-integration.md`
**内容要点**:
```markdown
背景: 分析28个仓库，识别缺口与融合优化机会
决策:
  1. codegraph 提升为代码探索首选（R17）
  2. claude-mem 3层工作流正式化（R18）
  3. GateGuard 替代简单阈值检查
  4. 添加 dx-reviewer 角色
  5. workstreams 并行任务流
  6. ADR 机制建立
替代方案: 保持v8.1不变（拒绝：有明确缺口）
```
**验证**: docs/ADR/2026-06-10-*.md 存在

---

### T16: 验证并更新 rules/CORE.md（添加 R17-R18）
**目标**: 铁律扩展至18条，更新 CORE.md 中的规则表
**文件**: `rules/CORE.md`
**验证**: grep -c "^| R" rules/CORE.md 返回 18

---

## P2 — 优化任务（近期计划）

### T17: CLAUDE.md 精简（保持 ≤200行）
**目标**: 当前 CLAUDE.md 可能已超过200行，迁移详情到 SPEC.md
**策略**:
- Plugin表格 → SPEC.md 的插件部分（CLAUDE.md 只保留 @插件状态摘要）
- 详细命令说明 → SPEC.md
- CLAUDE.md 只保留: 优先级链 + 五阶段流程 + P0 skills + 路由摘要 + R1-R18
**验证**: wc -l CLAUDE.md ≤ 200

---

### T18: caveman-compress 运行一次（压缩 CLAUDE.md）
**目标**: 使用 caveman-compress skill 减少 CLAUDE.md 约46%
**前提**: T17完成后
**操作**: 激活 caveman-compress skill → 压缩 CLAUDE.md / rules/CORE.md
**验证**: 压缩后两文件总 token 减少 ≥ 30%（允许适当信息保留）

---

### T19: 更新 MANIFEST.yaml（添加新组件归属）
**目标**: 新增 workstream-management / adr-management / dx-reviewer / OPENSPEC.md 的归属
**文件**: `MANIFEST.yaml`
**格式**:
```yaml
workstream-management:
  type: skill
  owner: skills/workstream-management
  depends_on: [using-git-worktrees, claude-mem]
  
dx-reviewer:
  type: agent
  owner: agents/dx-reviewer.md
  triggered_by: [ui-changes, ux-changes, new-features]
```
**验证**: yaml 解析无错误

---

### T20: 添加 onboarding-guide skill（OpenSpec 风格）
**目标**: 新项目/新团队成员引导（对标 /opsx:onboard 11阶段）
**文件**: `skills/onboarding-guide/SKILL.md`
**流程**:
```
Phase 1: 项目概览（/understand-domain → 业务领域图）
Phase 2: 代码结构（/understand → 交互知识图）
Phase 3: 关键路径（codegraph_trace 主要函数）
Phase 4: 开发环境（验证本地运行）
Phase 5: 第一个任务（选最小有价值任务作为热身）
```
**验证**: 新项目运行 onboarding-guide → 5阶段均有输出

---

### T21: 验证 pre-bash tmux hook（ECC模式）
**目标**: 确认 pre-bash 中有 tmux 检查（参考 ECC pre:bash:tmux-reminder）
**检查点**: hooks/ 中是否有阻止 tmux 外运行的检查
**若缺失**: 添加 pre-bash tmux reminder hook
**验证**: 在非tmux环境运行 bash 命令时有警告

---

### T22: 安全规则校验（对齐 ECC AgentShield）
**目标**: 验证 security-guidance plugin + rules/SECURITY.md 覆盖 OWASP Top10
**检查**: 对比 ECC 102条安全规则与本地安全规则
**补充**: 未覆盖的关键规则添加到 rules/SECURITY.md
**验证**: security-reviewer agent 能识别 SQL注入/XSS/SSRF 三类基础漏洞

---

### T23: 更新 README.md（目录结构同步）
**目标**: README.md 中的目录结构反映 v9.0 变更
**变更**: 技能数29→32，代理数24→25，rules+OPENSPEC.md
**验证**: README.md 中技能数量与 skills/ 目录一致

---

### T24: 更新 SPEC.md（法典 v9.0）
**目标**: SPEC.md 同步 v9.0 架构变更（workstreams/ADR/DX review/R17-R18）
**验证**: SPEC.md 版本号更新为 v9.0

---

## P3 — 探索性改进（长期计划）

### T25: 品味记忆机制研究
**目标**: 参考 gstack 品味偏好记忆，通过 claude-mem 实现跨会话设计偏好
**方案**: claude-mem 存储设计决策记录（minimal/dark/dense style偏好）
**约束**: 不修改 claude-mem 插件本身，通过 observation 机制实现
**产出**: 品味记忆 skill 草案

---

### T26: deer-flow 接口标准化
**目标**: claude-to-deerflow skill 稳定化，明确触发条件
**场景**: 需要长时间（>30min）、多角度、深度调研任务
**接口**: /deer-flow --mode <flash|standard|pro|ultra> <task>
**验证**: 至少一次成功的 deer-flow 调研完整流程

---

### T27: codegraph + understand-anything 联动
**目标**: 明确两者互补而非重叠的使用场景
**设计**:
```
codegraph_explore  → 函数级查询（快速，低token）
/understand-chat   → 业务级问答（高层理解）
/understand-diff   → 结合 codegraph_impact 变更影响可视化
```
**产出**: 两工具协同使用指南（rules/CORE.md 或 README）

---

### T28: 评估 GSD workstreams 完整实现
**目标**: 对比 T09 的轻量 workstream-management skill 与 GSD v1.42.3 完整 workstreams
**决策**: 是否升级为完整 GSD workstreams（需评估 token 成本）
**约束**: 不引入外部依赖超过 pnpm/npm
**产出**: 评估报告 + ADR 记录决策

---

## 执行顺序建议

```
第一轮（今天，P0全部）:
  T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08
  预计: 3-4小时

第二轮（本周，P1全部）:
  T09 → T10 → T11 → T12 → T13 → T14 → T15 → T16
  预计: 6-8小时

第三轮（下周，P2全部）:
  T17 → T18 → T19 → T20 → T21 → T22 → T23 → T24
  预计: 8-10小时

第四轮（持续迭代，P3）:
  T25~T28 按需推进
```

---

## 验收标准

### 必须全部通过（P0）:
- [x] CLAUDE.md 版本 = v9.0
- [x] 铁律 R17-R18 存在于 CLAUDE.md + CORE.md
- [x] context-monitor hook 包含 tool loop 检测
- [x] pre-compact hook 生成 .claude/state.json
- [x] dx-reviewer agent 文件存在
- [x] 审查路由包含 dx-reviewer

### 必须通过（P1）:
- [x] workstream-management skill 存在
- [x] adr-management skill 存在
- [x] sync.sh 可执行
- [x] rules/OPENSPEC.md 存在
- [x] docs/ADR/2026-06-10-*.md 存在
- [x] CORE.md 铁律数 = 18

### 优化指标（P2）:
- [x] CLAUDE.md ≤ 200行
- [x] 压缩后 CLAUDE.md token 减少 ≥ 30%（234→~130行，插件表迁至SPEC）
- [x] MANIFEST.yaml 无 yaml 解析错误
- [x] README.md 技能数 = 34，代理数 = 25

### P3 探索（已完成）:
- [x] T25 taste-memory skill 草案
- [x] T26 claude-to-deerflow skill 标准化
- [x] T27 codegraph+UA 协同指南（rules/CORE.md R17-R18表）
- [x] T28 GSD workstreams 评估 → docs/ADR/2026-06-10-gsd-workstreams-evaluation.md
- [x] T21 pre-tmux-reminder 已注册 settings.json Bash matcher
- [x] T22 SECURITY.md ECC AgentShield §16 对齐

### 同步与验证（复查 2026-06-10）:
- [x] `sync.ps1 -Force` → Cursor rules 含 OPENSPEC.mdc + CORE R17-R18 + CLAUDE.mdc v9.0
- [x] `validate_config.py` v9 全 12 项 PASS（agents=25, skills=34, rules=10）
- [x] `agent.yaml` 升至 v9.0；`/workstream` `/adr` 命令已创建
- [x] Cursor 软链：CLAUDE.md / skills(34) / agents(含 dx-reviewer) 均 OK
