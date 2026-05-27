# Design v5.0 — 五柱×五阶段×三层 全量整合

> 日期: 2026-05-27 | 基于 9 Agent 并行审查 27 仓库 | 增量优化，骨架不动

## 架构公式

```
RUNTIME  = Superpowers(方法论) + GSD(上下文工程) + OpenSpec(规格) + gstack(审查) + claude-mem(记忆)
FORMAT   = ECC(路由) + anthropics/skills(格式) + best-practice(实证)
REVIEW   = gstack 5审查 + 7补全
OPTIMIZE = RTK(shell token) + caveman(输出token)
```

## 三层架构

```
骨架层 (methodology)  → P0 skills ×4 + CORE铁律 R1-R13 + 审查路由 + MCP basic
执行层 (capability)   → 阶段 skill + agent + domain rules（按需 reactive）
护栏层 (guardrails)   → 安全/治理/效率 hook（骨架级4 + 按需级4）
                        + 学习 loop（Stop/PreCompact 触发）
```

## 五阶段嵌入

```
①规划(discuss)  ②规格(plan)   ③执行(execute)  ④验证(verify)  ⑤学习(compact)
     │               │               │               │               │
  HARD-GATE     spec-validation  SDD/TDD组合     gstack审查      pattern提取
  Red Flags表    OpenSpec格式    原子任务(2-5min) quality-gate    claude-mem SSOT
  一次一问       三轨互斥        两阶段审查       反合理化        上下文压缩
```

## 五柱职责

| 柱 | 骨架层 | 执行层 | 护栏层 |
|----|--------|--------|--------|
| Superpowers | HARD-GATE + Red Flags + P0×4 | brainstorming→writing-plans(原子)→executing→TDD→verify | defense-in-depth + 反合理化 |
| GSD | 三级阈值 + 连续执行 + 制品优先 | subagent(两阶段审查) + context-engineering | read-before-edit + canonical-source + trust-but-verify |
| OpenSpec | 三轨互斥 + proposal→spec→tasks | spec-validation + /propose→/apply→/archive | spec-reviewer门控 + 结构校验 |
| gstack | 审查路由5+7 + autoplan/ship | eng/ceo/design/qa/security review | browser-qa + quality-gate |
| claude-mem | SSOT渐进式披露 + 6hook | mem-search/timeline/knowledge-agent | MEMORY.md↔claude-mem统一 + Chroma |

## 护栏层

```
骨架级 (always-on, 4个)
├─ pre-bash-guard          → 阻断危险命令
├─ pre-read-before-edit    → 编辑前已读（GSD硬纪律）
├─ pre-manifest-validator  → 归属冲突检测
└─ post-secret-detector    → 密钥泄露检测

按需级 (profile控制, 4个)
├─ pre-rtk-rewrite         → ENABLE_TOOL_SEARCH=true
├─ pre-context-injector    → 非简单任务（会话缓存一次）
├─ post-edit-format        → 编辑后格式化
└─ stop-quality-gate       → /verify或/ship阶段

学习loop (Stop/PreCompact)
├─ pre-compact-state       → 压缩前快照
├─ stop-session-summary    → 会话摘要
├─ stop-readme-updater     → README更新
└─ instinct-learning v2    → pattern提取（替代v1 stop-pattern-extraction）
```

## 执行层：SDD + TDD 组合

```
模式一 SDD: spec/design → writing-plans(原子) → subagent(两阶段审查) → verify
模式二 TDD: RED(失败测试) → GREEN(最小通过) → REFACTOR → verify
模式三 组合: writing-plans → 每个task: RED→GREEN→REFACTOR → subagent审查 → verify

规则:
- 原子任务 2-5分钟，含精确路径+代码+验证命令
- 两阶段审查：先spec合规→后代码质量，失败打回
- 连续执行不问"是否继续"，阻塞即停不猜测
- TDD铁律：无失败测试无生产代码
```

## 规模约束

| 类型 | v5.0 | v4.0 | 变化 |
|------|------|------|------|
| CLAUDE.md | ≤280行 | ~260 | 精简 |
| rules | 10 | 10 | BESTPRACTICE大幅扩展 |
| skills | 26 | 27 | 重写2，其余补全，删1 |
| agents | 19 | 20 | 删context-manager(归claude-mem) |
| hooks | 12 | 15 | 删3 |
| plugins | 6 | 17 | 卸载8+禁用3 |
| MCP | 17 | 18 | gh迁移新版 |

## 插件精简

```
保留 6: superpowers, claude-mem, claude-md-management, skill-creator, commit-commands, claude-code-setup
禁用 3: frontend-design, code-review, feature-dev (设计覆盖)
卸载 8: context7, github, chrome-devtools-mcp, playwright, security-guidance, firecrawl, ralph-loop, typescript-lsp
```

## 变更清单

### 重写 (6)
1. `skills/writing-plans/SKILL.md` — 原子任务模式 (2-5min+精确路径+验证命令)
2. `skills/subagent-driven-development/SKILL.md` — 两阶段审查+连续执行
3. `skills/brainstorming/SKILL.md` — 一次一问+Red Flags+用户审核门
4. `rules/BESTPRACTICE.md` — 50→200行，15类别全覆盖
5. `skills/improve-codebase-architecture/SKILL.md` — 术语表+删除测试+HTML报告+Grilling Loop
6. `catalog/skills/ui-ux-pro-max/` — 补全67风格+161色板+99UX

### 补全 (4)
7. `rules/CONTEXT.md` — +Canonical Source Precedence + Trust-But-Verify
8. `skills/karpathy-guidelines/SKILL.md` — +实施规则+量化测试+孤儿清理边界
9. `skills/triage/SKILL.md` — 保留P0-P3+补状态机模型
10. `agents/qa.md` — +互斥声明(边界/回归 vs eng-reviewer覆盖率)

### Bug修复 (5)
11. `/propose`, `/apply`, `/archive` — 路径统一为 `openspec/changes/`
12. GitHub MCP — 迁移至 `github/github-mcp-server` + toolsets all
13. ChromaDB — 统一 settings.json 与 claude-mem 配置为 true
14. `stop-pattern-extraction.py` — 停用v1
15. SPEC.md — 仓库映射更新 + catalog REGISTRY.csv

### 删除 (5)
- `agents/context-manager.md` (归claude-mem)
- `hooks/stop-pattern-extraction.py` (v1与v2重复)
- `hooks/post-operation-log.py` (claude-mem覆盖)
- `hooks/pre-config-protection.py` (与manifest-validator重叠)
- `plugins/` 中 8 个已禁用插件目录

### 保留不动
- rules: GIT, MCP, DESIGN, SECURITY, WORKFLOW, AGENTS, README (7)
- agents: 18个 (除context-manager外的全部)
- skills: 20个 (除重写的6个外的全部)
- hooks: 10个 (除删除3个+停用1个外的全部)
- catalog: 除ui-ux-pro-max外的所有条目
- sync.ps1 + SYNC_GUIDE.md

## 需求逐条验证

| # | 要求 | 验收 |
|---|------|------|
| 1 | 五柱骨架清晰 | 五柱各司骨架/执行/护栏 |
| 2 | 协调自主运行 | SessionStart→P0→路由→五阶段→护栏→学习loop |
| 3 | 非简单任务有计划 | writing-plans原子任务+SDD/TDD组合 |
| 4 | 管理好上下文 | GSD三级阈值+三态制品+subagent 30% |
| 5 | 智能按需加载 | lazy rules+catalog按需+profile控制+MCP分组 |
| 6 | 最大程度调用工具 | MANIFEST concern→owner+tool-first五级查询 |
| 7 | 不左右手互博 | MANIFEST excludes+manifest-validator hook |
| 8 | 持续学习 | instinct-learning v2+claude-mem渐进式披露 |
| 9 | 言简意赅杜绝废话 | caveman-compress+RTK shell token |
| 10 | 同步编辑器正常 | sync.ps1软链接CLAUDE.md/skills/agents/不变 |
| 11 | 保留所有优点 | 不变清单确认，针对性增量 |
| 12 | 不过度优化 | 15项变更，其余不动 |
