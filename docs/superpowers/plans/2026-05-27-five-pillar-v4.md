# 五柱架构 v4.0 配置整合实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) to implement this plan layer-by-layer. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 design-v4.md，对 .claude 配置进行七层增量优化，深度对比五柱核心仓库最新内容，选择性补全其余 21 仓库优点，确保骨架清晰、无互博。

**Architecture:** 配置整合项目，按骨架→规则→Agent→Hook→Skill→MCP→模板七层顺序执行。每层先研究(对比差异)→编辑(增量修改)→验证(一致性检查)→提交(独立commit)。每层完成后 MANIFEST.yaml 归属验证。

**Tech Stack:** YAML/Markdown/Python hooks/JSON config — 纯配置文件编辑

---

## 文件结构

```
C:\Users\DELL\.claude\
├── CLAUDE.md              # L1: 路由入口 (≤300行)
├── SPEC.md                # L1: 法典索引
├── MANIFEST.yaml          # L1: 防互博归属
├── agent.yaml             # L1: 组件清单
├── rules/
│   ├── CORE.md            # L2: 编码规范+铁律
│   ├── CONTEXT.md         # L2: 上下文工程 (重点)
│   ├── WORKFLOW.md        # L2: 工作流编排
│   ├── AGENTS.md          # L2: 多Agent协作
│   ├── SECURITY.md        # L2: 安全规则
│   ├── GIT.md             # L2: Git规范
│   ├── DESIGN.md          # L2: 设计Token
│   ├── MCP.md             # L2: MCP配置
│   ├── BESTPRACTICE.md    # L2: 最佳实践
│   └── README.md          # L2: 规则索引
├── agents/ (20个)         # L3: Agent定义
├── hooks/ (15个)          # L4: Hook脚本
├── settings.json          # L4: 主配置
├── plugins/               # L5: 插件市场
├── .mcp.json              # L6: MCP权威源
├── mcp/servers.json       # L6: MCP分组
└── templates/             # L7: 模板文件
```

---

## 阶段0: 并行研究 (一次性)

用6个并行子Agent分别研究各仓库最新内容，产出差异报告。

### Task 0.1: 研究 Superpowers (obra/superpowers)

**Files:** 无文件修改，研究用

- [ ] **Step 1: 获取最新内容**

```bash
git -C /tmp clone --depth 1 https://github.com/obra/superpowers 2>/dev/null || echo "already cloned"
ls /tmp/superpowers/skills/ 2>/dev/null || echo "check online"
```

- [ ] **Step 2: 对比本地 skills 目录**

对比 `/tmp/superpowers/skills/` 与 `C:\Users\DELL\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills/` 的差异：
- brainstorming 是否有新增门控或流程变化
- writing-plans 是否有格式更新
- verification-before-completion 是否有新检查项
- 是否有新增 skill 未在 agent.yaml 注册

- [ ] **Step 3: 输出差异清单**

输出格式: `{skill_name}: {变更类型} - {具体差异} - {是否需要落地}`
若有新增 P0 触发规则，标注 HIGH。

---

### Task 0.2: 研究 GSD (gsd-build/get-shit-done)

**Files:** 无文件修改，研究用

- [ ] **Step 1: 获取最新 GSD 仓库**

```bash
git -C /tmp clone --depth 1 https://github.com/gsd-build/get-shit-done 2>/dev/null || echo "already cloned"
```

- [ ] **Step 2: 对比上下文工程规则**

重点对比：
- `.claude/rules/CONTEXT.md` 的三级阈值 vs GSD 最新定义
- GSD 是否新增阶段或命令
- read-before-edit 规则是否更新
- 上下文腐烂治理策略是否有新机制

- [ ] **Step 3: 输出差异清单**

输出格式同上。标注哪些影响 CONTEXT.md 和 WORKFLOW.md。

---

### Task 0.3: 研究 OpenSpec (Fission-AI/OpenSpec)

**Files:** 无文件修改，研究用

- [ ] **Step 1: 获取最新 OpenSpec 仓库**

```bash
git -C /tmp clone --depth 1 https://github.com/Fission-AI/OpenSpec 2>/dev/null || echo "already cloned"
```

- [ ] **Step 2: 对比规格格式**

重点对比：
- proposal→spec→tasks 三文件的字段和格式
- brownfield 变更的 diff 格式
- archive 归档规则
- 与本地 `templates/openspec/` 的差异

- [ ] **Step 3: 输出差异清单**

---

### Task 0.4: 研究 gstack (garrytan/gstack)

**Files:** 无文件修改，研究用

- [ ] **Step 1: 获取最新 gstack 仓库**

```bash
git -C /tmp clone --depth 1 https://github.com/garrytan/gstack 2>/dev/null || echo "already cloned"
```

- [ ] **Step 2: 对比审查 Agent 定义**

重点对比：
- 5 核心审查角色的 prompt 定义是否更新
- 7 补全角色是否有新增或合并
- 浏览器QA agent 是否有新能力
- 审查路由规则是否变化

- [ ] **Step 3: 输出差异清单**

---

### Task 0.5: 研究 claude-mem (thedotmack/claude-mem)

**Files:** 无文件修改，研究用

- [ ] **Step 1: 检查本地 claude-mem 插件版本**

```bash
cat C:/Users/DELL/.claude/plugins/marketplaces/claude-plugins-official/.claude-plugin/marketplace.json 2>/dev/null | head -5
# 检查 claude-mem 是否在此注册
ls C:/Users/DELL/.claude/plugins/marketplaces/thedotmack/ 2>/dev/null
```

- [ ] **Step 2: 获取最新 claude-mem 仓库**

```bash
git -C /tmp clone --depth 1 https://github.com/thedotmack/claude-mem 2>/dev/null || echo "already cloned"
```

- [ ] **Step 3: 对比记忆系统**

重点对比：
- MEMORY.md 格式是否更新
- 渐进式披露机制是否有变化
- 向量搜索是否有新能力
- hook 设计是否有变化
- 与 memory MCP 的协作方式

- [ ] **Step 4: 输出差异清单**

---

### Task 0.6: 研究其余 21 仓库（分类并行）

**Files:** 无文件修改，研究用

- [ ] **Step 1: 结构格式组 (6仓库) 批量获取**

```bash
for repo in affaan-m/ECC shanraisshan/claude-code-best-practice \
  forrestchang/andrej-karpathy-skills mattpocock/skills \
  VoltAgent/awesome-design-md anthropics/skills; do
  git -C /tmp clone --depth 1 "https://github.com/$repo" 2>/dev/null || true
done
```

- [ ] **Step 2: 优化工具组 (4仓库) 批量获取**

```bash
for repo in rtk-ai/rtk JuliusBrussee/caveman \
  github/github-mcp-server anthropics/claude-code-action; do
  git -C /tmp clone --depth 1 "https://github.com/$repo" 2>/dev/null || true
done
```

- [ ] **Step 3: 编排增强组 (4仓库) 批量获取**

```bash
for repo in eyaltoledano/claude-task-master \
  nextlevelbuilder/ui-ux-pro-max-skill zilliztech/claude-context \
  bytedance/deer-flow; do
  git -C /tmp clone --depth 1 "https://github.com/$repo" 2>/dev/null || true
done
```

- [ ] **Step 4: 参考索引组 (5仓库) 批量获取**

```bash
for repo in ComposioHQ/awesome-claude-skills \
  hesreallyhim/awesome-claude-code \
  x1xhlol/system-prompts-and-models-of-ai-tools \
  Chalarangelo/30-seconds-of-code ruvnet/ruflo; do
  git -C /tmp clone --depth 1 "https://github.com/$repo" 2>/dev/null || true
done
```

- [ ] **Step 5: 输出亮点清单**

按优先级标注: HIGH(必须落地) / MEDIUM(选择性) / LOW(仅索引)

---

## 阶段1: Layer 1 — 骨架层

### Task 1.1: 更新 CLAUDE.md

**Files:**
- Modify: `C:\Users\DELL\.claude\CLAUDE.md`

基于 Task 0.1-0.6 的研究差异，增量更新。

- [ ] **Step 1: 读取当前 CLAUDE.md 和差异报告**

读取当前 CLAUDE.md，对照研究差异清单。

- [ ] **Step 2: 更新优先级链**

将 `用户显式指令 > CLAUDE.md 指针 > 激活 skill > lazy rules > alwaysApply rules > default prompt`
更新为包含 plugin 层:
```
用户显式指令 > CLAUDE.md 指针 > 激活 plugin > 激活 skill > lazy rules > alwaysApply rules > default prompt
```

- [ ] **Step 3: 新增 R12 铁律**

在铁律表中增加:
```
| R12 | 子Agent隔离 | 同一上下文仅一个执行者，禁止共享可变状态 |
```
(仅当 deer-flow 研究确认有此需求时)

- [ ] **Step 4: 新增 R13 铁律**

```
| R13 | 制品存活 | 结构化制品跨会话持久化，不依赖对话历史 |
```
(仅当 ruflo 研究确认有此需求时)

- [ ] **Step 5: 命令速查去重**

检查 GSD 已有命令与 CLAUDE.md 命令速查表是否重复，去重。

- [ ] **Step 6: 验证行数 ≤300**

```bash
wc -l C:/Users/DELL/.claude/CLAUDE.md
```

- [ ] **Step 7: 提交**

```bash
git add CLAUDE.md
git commit -m "chore(skeleton): update CLAUDE.md to v4.0 - priority chain, R12/R13, command dedup

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1.2: 更新 SPEC.md

**Files:**
- Modify: `C:\Users\DELL\.claude\SPEC.md`

- [ ] **Step 1: 读取当前 SPEC.md**

- [ ] **Step 2: 更新版本号和日期**

版本 3.0 → 4.0，日期更新为 2026-05-27。

- [ ] **Step 3: 更新 26 仓库完整映射**

基于研究差异，补充/修正每个仓库的"吸收"和"落地"列。
特别关注: claude-code-action 的 CI 模板路径、github-mcp-server 的工具数量。

- [ ] **Step 4: 刷新规模约束表**

用实际数字更新:
```
| 全局 skills | ≤28 | 实际计数 |
| 全局 agents | ≤22 | 实际计数 |
| 全局 rules | 10 | 10 |
| CLAUDE.md | ≤300 | 实际行数 |
| 全局 hooks | 15 | 15 |
```

- [ ] **Step 5: 扩展防互博速查**

新增行:
```
| 插件注册 | plugin marketplace | skill 同名注册 |
| 工作流编排 | WORKFLOW.md | pre-task-planner |
| CI 模板 | claude-code-action templates | release-engineer 内嵌 |
```

- [ ] **Step 6: 验证一致性**

确认 SPEC.md 中的文件路径均为实际存在的路径。

- [ ] **Step 7: 提交**

```bash
git add SPEC.md
git commit -m "chore(skeleton): update SPEC.md to v4.0 - 26 repo mapping, scale refresh

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1.3: 更新 MANIFEST.yaml

**Files:**
- Modify: `C:\Users\DELL\.claude\MANIFEST.yaml`

- [ ] **Step 1: 版本号 3.0 → 4.0**

```yaml
version: "4.0"
updated: "2026-05-27"
```

- [ ] **Step 2: 新增 concerns**

基于研究差异，添加:
```yaml
  plugin_registry:
    owner: settings.json enabledPlugins
    source: ECC
    excludes: [skill同名注册]

  deer_flow:
    owner: skill/subagent-driven-development
    source: bytedance/deer-flow
    stage: execute
    excludes: [pre-task-planner]

  ci_template:
    owner: templates/github-actions/
    source: anthropics/claude-code-action
    stage: ship

  claude_context:
    owner: .mcp.json (optional)
    source: zilliztech/claude-context
    note: 按需启用，不常驻
```

- [ ] **Step 3: 更新互斥声明**

确保所有 excludes 字段准确反映当前实际情况。

- [ ] **Step 4: 提交**

```bash
git add MANIFEST.yaml
git commit -m "chore(skeleton): update MANIFEST.yaml to v4.0 - new concerns, deer-flow, ci

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 1.4: 更新 agent.yaml

**Files:**
- Modify: `C:\Users\DELL\.claude\agent.yaml`

- [ ] **Step 1: 版本号 3.0 → 4.0**

- [ ] **Step 2: 对齐 anthropics/skills 格式**

基于 Task 0.6 研究，检查 agent.yaml 中 skills 分类是否需要调整以匹配官方格式。

- [ ] **Step 3: 更新 catalog 注释**

标注实际 catalog 数量。

- [ ] **Step 4: 提交**

```bash
git add agent.yaml
git commit -m "chore(skeleton): update agent.yaml to v4.0

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 阶段2: Layer 2 — 规则层

### Task 2.1: 更新 CORE.md

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\CORE.md`

- [ ] **Step 1: 读取当前 CORE.md**

- [ ] **Step 2: Karpathy 四原则改为引用指针**

将现有的详细四原则内容替换为简洁引用:
```
## Karpathy 四原则

详细内容 → skill/karpathy-guidelines

1. Think Before Coding — 先陈述假设
2. Simplicity First — 能50行不写200行
3. Surgical Changes — 只改必须改的
4. Goal-Driven — 弱命令转强声明式
```

(仅当研究确认 karpathy-skills 仓库有更完整版本时执行)

- [ ] **Step 3: 新增 R12、R13 铁律**

与 CLAUDE.md 保持一致:
```
| R12 | 子Agent隔离 | 同一上下文单执行者，禁止共享可变状态 |
| R13 | 制品存活 | 结构化制品跨会话持久化 |
```

- [ ] **Step 4: 精简注释规则**

移除冗余模板(已在 BESTPRACTICE.md 覆盖)，保留核心触发条件。

- [ ] **Step 5: 提交**

```bash
git add rules/CORE.md
git commit -m "chore(rules): update CORE.md - R12/R13, karpathy ref, simplify comments

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.2: 更新 CONTEXT.md (重点)

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\CONTEXT.md`

- [ ] **Step 1: 读取当前 CONTEXT.md**

- [ ] **Step 2: 三级阈值精确化**

基于 GSD 最新研究，确认并更新:
```markdown
## 上下文腐烂三级阈值

| 使用率 | 行动 |
|--------|------|
| <40% | 正常工作（主会话编排 + 子agent实现） |
| 50% | 逻辑断点 `/compact`，释放已完成上下文 |
| 70% | 强制压缩或启动新子Agent，保留决策丢弃细节 |
```

- [ ] **Step 3: 新增 DAG 依赖图调度规则**

基于 deer-flow 研究:
```markdown
## 子Agent DAG 调度

- 无依赖子目标 → 并行派发
- 有依赖子目标 → 等待前置完成后派发
- 每个子Agent: fresh context + 精确注入必要状态
- 同一模块内禁止多agent并行执行
```

- [ ] **Step 4: 新增三态制品管理**

```markdown
## 制品三态

| 制品路径 | 类型 | 生命周期 |
|----------|------|----------|
| openspec/changes/ | 功能变更规格 | 合并后归档 |
| .planning/phases/ | 大功能阶段 | 完成后清理 |
| memory/ (claude-mem) | 跨会话知识 | 持续更新 |
```

- [ ] **Step 5: 更新 claude-context 启用条件**

确认版本要求是否变化。

- [ ] **Step 6: 长任务治理细化**

```markdown
- 超过30分钟 → 拆分为独立子Agent
- 每个子目标完成 → 输出状态摘要
- 检查点: 每完成3个Task验证一次一致性
```

- [ ] **Step 7: 提交**

```bash
git add rules/CONTEXT.md
git commit -m "chore(rules): update CONTEXT.md - DAG scheduling, three artifacts, governance

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.3: 更新 WORKFLOW.md

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\WORKFLOW.md`

- [ ] **Step 1: 读取当前 WORKFLOW.md**

- [ ] **Step 2: DAG 编排四阶段确认完整**

检查拆解→调度→整合→验证是否已完整，仅在缺失时补充。

- [ ] **Step 3: 质量门增加**

确认已有: Schema Drift / Security Anchor / Scope Reduction
仅在缺失时补充。

- [ ] **Step 4: 状态机补充 DONE_WITH_CONCERNS**

基于 ruflo 研究:
```markdown
DONE              → 继续 spec 合规性审查
DONE_WITH_CONCERNS → 阅读担忧后决定是否通过
NEEDS_CONTEXT     → 提供缺失上下文并重新派遣
BLOCKED           → 评估阻止因素并重新派遣
```

- [ ] **Step 5: 编排互斥精确化**

```markdown
planner (writing-plans) vs agentic-orchestrator (subagent-driven-development):
- planner: 规划阶段，只产出计划，不执行
- agentic-orchestrator: 执行阶段，按计划派发子agent
- 两者不同时参与同一任务
```

- [ ] **Step 6: 提交**

```bash
git add rules/WORKFLOW.md
git commit -m "chore(rules): update WORKFLOW.md - state machine, quality gates, mutual exclusion

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.4: 更新 AGENTS.md

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\AGENTS.md`

- [ ] **Step 1: 读取当前 AGENTS.md**

- [ ] **Step 2: 审查路由表对齐 gstack 最新**

确认 5+7 角色的触发条件精确。仅在研究发现差异时修改。

- [ ] **Step 3: 委派条件精确化**

基于 ECC 研究:
```markdown
| 条件 | Agent | 精确触发 |
|------|-------|---------|
| 只读探索 | code-explorer | grep/glob 无法定位时 |
| 写计划 | planner | 非简单任务，>3文件变更 |
| 多模块并行 | agentic-orchestrator | 无依赖的独立子任务 |
```

- [ ] **Step 4: 禁止项扩展**

```markdown
- agent 间共享可变状态（包括通过临时文件）
- planner 与 agentic-orchestrator 同时编排同一任务
- context-manager 重复 claude-mem 存储逻辑
- 同一模块内多agent并行写入
```

- [ ] **Step 5: 提交**

```bash
git add rules/AGENTS.md
git commit -m "chore(rules): update AGENTS.md - routing precision, delegation, prohibitions

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.5: 更新 SECURITY.md

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\SECURITY.md`

- [ ] **Step 1: 读取当前 SECURITY.md**

- [ ] **Step 2: STRIDE 对齐 OWASP Agentic 2026**

仅在研究发现新威胁模型时更新。

- [ ] **Step 3: 渐进硬化 Checklist 统一**

将 §11、§12、§13、§14 整合为单一硬化清单:
```markdown
## 硬化 Checklist
□ permissions.deny 阻断凭证路径
□ pre-bash-guard 阻断危险命令
□ /sandbox OS 隔离
□ post-secret-detector 密钥扫描
□ .mcp.json 纳入 git 审查
□ 技能来源审查 (untrusted SKILL.md)
```

- [ ] **Step 4: 提交**

```bash
git add rules/SECURITY.md
git commit -m "chore(rules): update SECURITY.md - unify hardening checklist

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2.6: 更新其余规则文件 (GIT/DESIGN/MCP/BESTPRACTICE/README)

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\GIT.md`, `DESIGN.md`, `MCP.md`, `BESTPRACTICE.md`, `README.md`

- [ ] **Step 1: GIT.md — 确认完整性**

读取并确认内容完整，仅在发现缺失时补充。

- [ ] **Step 2: DESIGN.md — 补充 token 优先验证规则**

基于 awesome-design-md 研究:
```markdown
## Token 验证规则
- 组件引用 token，不硬编码色值
- CI 可运行 token-usage 检查：grep -r "#[0-9a-fA-F]{6}" components/
```

- [ ] **Step 3: MCP.md — 分组视图更新**

增加 claude-context 到 optional 分组:
```json
"optional": ["postgres", "puppeteer", "glif", "claude-context"]
```

- [ ] **Step 4: BESTPRACTICE.md — 注入防护更新**

基于 system-prompts 研究，确认注入防护内容是否最新。

- [ ] **Step 5: README.md — 索引更新**

更新文件数量和描述，确保与实际一致。

- [ ] **Step 6: 提交**

```bash
git add rules/GIT.md rules/DESIGN.md rules/MCP.md rules/BESTPRACTICE.md rules/README.md
git commit -m "chore(rules): update minor rules - DESIGN/MCP/BESTPRACTICE/README sync

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 阶段3: Layer 3 — Agent 层

### Task 3.1: 更新核心 Agent (agentic-orchestrator, context-manager, security-reviewer, release-engineer)

**Files:**
- Modify: `C:\Users\DELL\.claude\agents\agentic-orchestrator.md`
- Modify: `C:\Users\DELL\.claude\agents\context-manager.md`
- Modify: `C:\Users\DELL\.claude\agents\security-reviewer.md`
- Modify: `C:\Users\DELL\.claude\agents\release-engineer.md`

- [ ] **Step 1: agentic-orchestrator — DAG 依赖调度**

研究 deer-flow 后，更新 agent 定义中的调度规则:
```
## 调度规则
- 无依赖子目标 → 并行派发所有子Agent
- 有依赖子目标 → 等待前置完成，验证输出后派发
- 每子Agent独立上下文，通过结构化制品通信
- 禁止: 同一模块内多agent同时写入
```

- [ ] **Step 2: context-manager — 三态制品感知**

```
## 制品感知
启动时检查:
1. openspec/changes/ — 进行中的功能变更
2. .planning/phases/ — 进行中的阶段规划
3. memory/ (via claude-mem plugin) — 跨会话知识
按优先级注入上下文，避免重复加载。
```

- [ ] **Step 3: security-reviewer — STRIDE 2026**

仅在研究发现新威胁类别时更新 threat model 部分。

- [ ] **Step 4: release-engineer — CI 模板引用**

```
## CI 集成
发布时检查: templates/github-actions/ 中的工作流模板
支持: PR Check / Deploy Preview / Production Deploy / Rollback
```

- [ ] **Step 5: 提交**

```bash
git add agents/agentic-orchestrator.md agents/context-manager.md agents/security-reviewer.md agents/release-engineer.md
git commit -m "chore(agents): update core agents - DAG, artifacts, CI integration

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3.2: 确认其余 16 个 Agent 格式

**Files:**
- Read: `C:\Users\DELL\.claude\agents\` (all .md files)

- [ ] **Step 1: 批量读取所有 agent 文件**

检查格式一致性: 每个 agent 是否有 description / tools / 触发条件。

- [ ] **Step 2: 标记格式异常**

输出需要修复的 agent 列表。仅修复格式问题，不改行为逻辑。

- [ ] **Step 3: 批量修复格式（如有需要）**

- [ ] **Step 4: 提交（如有修改）**

```bash
git add agents/
git commit -m "chore(agents): format consistency check for 16 agents

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 阶段4: Layer 4 — Hook 层

### Task 4.1: 更新 pre-manifest-validator.py

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\pre-manifest-validator.py`

- [ ] **Step 1: 读取当前脚本**

- [ ] **Step 2: 增加 plugin vs skill 互斥检查**

在现有 MANIFEST 归属校验基础上，新增检查逻辑:
```python
# 检查: 同一能力是否同时注册为 plugin 和 skill
# 若是，输出 WARNING: "X is both plugin and skill — disable one"
```

具体实现依赖当前脚本结构，读取后确定插入位置。

- [ ] **Step 3: 测试验证**

```bash
python C:/Users/DELL/.claude/hooks/pre-manifest-validator.py --dry-run 2>&1
```

- [ ] **Step 4: 提交**

```bash
git add hooks/pre-manifest-validator.py
git commit -m "chore(hooks): add plugin-vs-skill mutual exclusion check

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4.2: 更新 pre-context-injector.py

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\pre-context-injector.py`

- [ ] **Step 1: 读取当前脚本**

- [ ] **Step 2: 增加三态制品加载**

在现有项目 CLAUDE.md 注入基础上，新增:
```python
# 加载顺序:
# 1. 项目 CLAUDE.md (现有逻辑)
# 2. openspec/changes/ (当前活跃的变更规格)
# 3. .planning/phases/ (当前阶段规划)
# 4. memory/ 摘要 (通过 claude-mem plugin)
# 每项最多加载500字符摘要，避免上下文过载
```

- [ ] **Step 3: 测试验证**

- [ ] **Step 4: 提交**

```bash
git add hooks/pre-context-injector.py
git commit -m "chore(hooks): add three-artifact loading to context injector

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4.3: 更新 stop-pattern-extraction.py 和 pre-compact-state.py

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\stop-pattern-extraction.py`
- Modify: `C:\Users\DELL\.claude\hooks\pre-compact-state.py`

- [ ] **Step 1: stop-pattern-extraction — 增加 DAG 执行模式**

读取当前脚本，确认是否已提取子Agent执行模式。若未覆盖，增加:
```python
# 提取: 子Agent DAG 执行路径
# - 并行成功的子任务组合
# - 失败依赖链
# - 最佳并行度
```

- [ ] **Step 2: pre-compact-state — 增加 openspec 状态**

读取当前脚本，确认压缩快照是否包含 openspec/ 状态。若未覆盖，增加。

- [ ] **Step 3: 测试验证**

- [ ] **Step 4: 提交**

```bash
git add hooks/stop-pattern-extraction.py hooks/pre-compact-state.py
git commit -m "chore(hooks): add DAG pattern extraction and openspec state snapshot

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4.4: 确认其余 11 个 Hook 完整性

**Files:**
- Read: `C:\Users\DELL\.claude\hooks\` (all .py files except already modified)

- [ ] **Step 1: 批量检查 hook 逻辑**

确认每个 hook:
- 超时设置合理 (≤30000ms)
- 错误处理不静默吞错
- 输出格式一致

- [ ] **Step 2: 标记并修复问题**

- [ ] **Step 3: 提交（如有修改）**

---

## 阶段5: Layer 5 — Skill 层

### Task 5.1: 更新 brainstorming skill

**Files:**
- Modify: `C:\Users\DELL\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills\brainstorming\SKILL.md`

- [ ] **Step 1: 对比最新 superpowers 版本**

基于 Task 0.1 研究差异。

- [ ] **Step 2: 更新视觉伴侣路径**

确认 visual-companion.md 引用路径正确。

- [ ] **Step 3: 更新（仅当有新版本时）**

注意: 这是插件缓存目录，通常由插件系统管理。仅在确认官方更新后修改或等待插件自动更新。

- [ ] **Step 4: 提交**

```bash
git add plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/brainstorming/SKILL.md
git commit -m "chore(skills): update brainstorming skill from superpowers upstream

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5.2: 更新 writing-plans, subagent-driven-development, context-engineering, caveman-compress

**Files:**
- Modify: `C:\Users\DELL\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills\writing-plans\SKILL.md`
- Modify: `C:\Users\DELL\.claude\plugins\cache\claude-plugins-official\superpowers\5.1.0\skills\subagent-driven-development\SKILL.md`
- Modify: `C:\Users\DELL\.claude\skills\context-engineering\` (if exists as standalone)
- Modify: `C:\Users\DELL\.claude\skills\caveman-compress\` (if exists as standalone)

- [ ] **Step 1: writing-plans — 三轨选择逻辑**

确认当前 SKILL.md 中是否已包含三轨选择 (openspec/GSD/lite)。若未包含，在 scope check 部分增加。

- [ ] **Step 2: subagent-driven-development — DAG 调度**

确认是否已有依赖图调度逻辑。若未包含，在 dispatching 部分增加 DAG 规则。

- [ ] **Step 3: context-engineering — 三态制品**

确认是否覆盖三种制品类型的管理策略。

- [ ] **Step 4: caveman-compress — 四级压缩**

确认压缩级别是否完整 (l1-verbose / l2-normal / l3-compact / l4-caveman)。

- [ ] **Step 5: 提交（分批）**

---

### Task 5.3: 其他 skill 格式对齐 anthropics/skills 标准

**Files:**
- Read: 所有 skill SKILL.md 文件

- [ ] **Step 1: 对齐检查**

基于 anthropics/skills 研究，检查每个 SKILL.md:
- 是否有 `name` 和 `description` frontmatter
- 工具引用格式是否一致
- 触发条件是否清晰

- [ ] **Step 2: 修复格式问题**

- [ ] **Step 3: 提交**

---

## 阶段6: Layer 6 — MCP 层

### Task 6.1: 更新 .mcp.json

**Files:**
- Modify: `C:\Users\DELL\.claude\.mcp.json`

- [ ] **Step 1: 读取当前 .mcp.json**

- [ ] **Step 2: 增加 claude-context 配置（可选）**

基于 claude-context 研究，仅在满足启用条件时添加:
```json
"claude-context": {
  "type": "stdio",
  "command": "claude-context",
  "args": ["serve"],
  "env": {
    "MILVUS_HOST": "${MILVUS_HOST}",
    "MILVUS_PORT": "${MILVUS_PORT}"
  }
}
```

- [ ] **Step 3: 标记为 optional 分组**

- [ ] **Step 4: 提交**

```bash
git add .mcp.json
git commit -m "chore(mcp): add claude-context as optional MCP server

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6.2: 更新 mcp/servers.json

**Files:**
- Modify: `C:\Users\DELL\.claude\mcp\servers.json`

- [ ] **Step 1: 分组增加 claude-context**

```json
"optional": ["postgres", "puppeteer", "glif", "claude-context"]
```

- [ ] **Step 2: 验证一致性**

确认 servers.json 中所有服务器名在 .mcp.json 中存在。

- [ ] **Step 3: 提交**

```bash
git add mcp/servers.json
git commit -m "chore(mcp): add claude-context to optional group

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 阶段7: Layer 7 — 模板/目录层

### Task 7.1: 更新 templates/openspec/

**Files:**
- Modify: `C:\Users\DELL\.claude\templates\openspec\` (if exists, else create)

- [ ] **Step 1: 对比 OpenSpec 最新模板格式**

基于 Task 0.3 研究。

- [ ] **Step 2: 更新 proposal.md 模板**

对齐 proposal 字段: title / motivation / spec-delta / risk-assessment

- [ ] **Step 3: 更新 spec.md 模板**

对齐 spec 字段: requirements / design / api-contracts / data-model

- [ ] **Step 4: 更新 tasks.md 模板**

对齐 tasks 字段: phase / dependencies / verification

- [ ] **Step 5: 提交**

```bash
git add templates/openspec/
git commit -m "chore(templates): update openspec templates to latest format

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7.2: 更新 templates/planning/ 和 templates/github-actions/

**Files:**
- Modify: `C:\Users\DELL\.claude\templates\planning\` (if exists)
- Create: `C:\Users\DELL\.claude\templates\github-actions\` (if not exists)

- [ ] **Step 1: planning 模板对齐 GSD 最新**

基于 GSD 研究，检查阶段模板格式。

- [ ] **Step 2: 创建 github-actions 模板**

基于 claude-code-action 研究，创建:
- `pr-check.yml` — PR 检查工作流
- `deploy-preview.yml` — 预览部署
- `production-deploy.yml` — 生产部署
- `rollback.yml` — 回滚

- [ ] **Step 3: 提交**

```bash
git add templates/planning/ templates/github-actions/
git commit -m "chore(templates): update planning, add github-actions CI templates

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7.3: 更新 catalog/ 索引

**Files:**
- Modify: `C:\Users\DELL\.claude\catalog\` 索引文件

- [ ] **Step 1: 同步 awesome-claude-skills 索引**

基于研究，更新 catalog/skills/ 索引。

- [ ] **Step 2: 更新 catalog/agents/ 索引**

确认 43 个 agent 与实际一致。

- [ ] **Step 3: 提交**

---

## 阶段8: 全局验证

### Task 8.1: 交叉验证

- [ ] **Step 1: 防互博检查**

运行 MANIFEST.yaml 归属验证:
```bash
python C:/Users/DELL/.claude/hooks/pre-manifest-validator.py --check-all
```

- [ ] **Step 2: 规模约束检查**

检查所有计数是否在上限内:
```bash
# Count skills, agents, rules, hooks
echo "Skills: $(ls C:/Users/DELL/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/ | wc -l)"
echo "Agents: $(ls C:/Users/DELL/.claude/agents/*.md | wc -l)"
echo "Rules: $(ls C:/Users/DELL/.claude/rules/*.md | wc -l)"
echo "Hooks: $(ls C:/Users/DELL/.claude/hooks/*.py | wc -l)"
echo "CLAUDE.md lines: $(wc -l < C:/Users/DELL/.claude/CLAUDE.md)"
```

- [ ] **Step 3: 引用完整性检查**

确认 SPEC.md 中所有文件路径实际存在:
```bash
grep -oP '[\w/]+\.[\w]+' SPEC.md | while read f; do test -f "$f" || echo "MISSING: $f"; done
```

- [ ] **Step 4: MCP 一致性验证**

确认 mcp/servers.json 中服务器在 .mcp.json 中存在。

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "chore(verify): cross-validation - anti-conflict, scale, integrity checks pass

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## 快速参考: 预期 Commit 序列

```
Phase0: 6 parallel research agents (no commits)
Phase1: 4 commits (CLAUDE.md, SPEC.md, MANIFEST.yaml, agent.yaml)
Phase2: 6 commits (CORE, CONTEXT, WORKFLOW, AGENTS, SECURITY, others)
Phase3: 2 commits (core agents, format check)
Phase4: 4 commits (manifest-validator, context-injector, pattern-extraction, others check)
Phase5: 3 commits (brainstorming, workflow skills, format alignment)
Phase6: 2 commits (.mcp.json, servers.json)
Phase7: 3 commits (openspec, planning+ci, catalog)
Phase8: 1 commit (verification)
---
Total: ~25 commits, each independently reviewable and rollback-able
```
