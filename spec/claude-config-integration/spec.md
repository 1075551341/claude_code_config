# Spec — .claude 配置整合需求规格

> **设计源**：24 个 GitHub 仓库 PRIMARY + P3 安全补强 | 本地 `~/.claude` 仅迁移对照  
> **版本**：2.4 | **关联**：[design.md](./design.md) | [tasks.md](./tasks.md) | [design-round3.md](./design-round3.md)

---

## 1. 概述

### 1.1 背景

将 22 个社区 AI Agent 配置仓库整合为统一 `~/.claude` 全局配置，以 **五柱架构** 为骨架：

| 柱 | 仓库 | 职责 |
|----|------|------|
| Superpowers | obra/superpowers | 方法论 + workflow |
| GSD | GSD-redux | 上下文工程 |
| OpenSpec | Fission-AI/OpenSpec | 变更规格 |
| gstack | garrytan/gstack | 角色审查与补全 |
| claude-mem | thedotmack/claude-mem | 跨会话记忆 |

满足：Claude Code 完整运行时、多编辑器软链接同步、非简单任务有计划、持续学习、Token 可控、无互博。

### 1.2 范围

| 在范围内 | 不在范围内 |
|----------|------------|
| ~/.claude 全局骨架重构 | deer-flow 独立 super-agent 部署 |
| 项目级 openspec/.planning 模板 | x1xhlol prompt 直接 copy |
| sync.ps1 多编辑器同步 | ECC 232 skills 整包导入 |
| 本地 legacy 审计迁移 | GSD 原仓库 clone |

### 1.3 利益相关方

- **主用户**：Claude Code CLI 日常开发者
- **次用户**：Cursor/Windsurf/Trae 同配置使用者
- **维护者**：未来配置迭代者（通过 MANIFEST + experiences 学习）

---

## 2. 功能需求

### FR-01 PRIMARY 骨架（五柱 + 结构层）

**来源**：五柱 + ECC + anthropics/skills + best-practice

| ID | 要求 | 验收 |
|----|------|------|
| FR-01.1 | 全局 skills ≤28：superpowers 13 + 扩展 8 + meta 4 + mattpocock 2 | validate_config V2 |
| FR-01.2 | 全局 agents ≤22：core 8 + gstack 12 | agents/README |
| FR-01.3 | rules ≤10 alwaysApply/lazy 文件 | 9 文件当前 |
| FR-01.4 | MANIFEST.yaml 覆盖 55+ concerns | --check-manifest |
| FR-01.5 | agent.yaml harness 可解析 | YAML lint |
| FR-01.6 | 每组件标注 source_repo | SPEC.md 溯源 |
| FR-01.7 | 五柱在 CLAUDE.md 表可见 | 五柱架构节 |
| FR-01.8 | catalog/skills ≥90 保留领域能力 | migrate-from-legacy |

### FR-02 工作流链（superpowers PRIMARY）

**来源**：obra/superpowers

| ID | 要求 | 验收 |
|----|------|------|
| FR-02.1 | 13 core skills 完整导入 | 13 个 SKILL.md 存在且 frontmatter 合法 |
| FR-02.2 | SessionStart 唯一 bootstrap → using-superpowers | hooks.json 仅一条 SessionStart |
| FR-02.3 | 非简单任务强制 brainstorming → writing-plans | HARD-GATE 在 brainstorming skill 中 |
| FR-02.4 | 执行走 executing-plans + subagent-driven-development | commands/execute 引用正确 |
| FR-02.5 | 完成前 verification-before-completion | /verify 命令可用 |
| FR-02.6 | Bug/feature 均走 test-driven-development | TDD skill 触发词有效 |
| FR-02.7 | commands 链：discuss/plan/execute/verify/ship | 5 命令存在且互不重复 |
| FR-02.8 | P0 强制 skill 仅 4 个：using-superpowers, brainstorming, verification-before-completion, systematic-debugging | CLAUDE.md 表；其余按需 |

**13 workflow skills 清单**（superpowers）：

1. using-superpowers
2. brainstorming
3. writing-plans
4. executing-plans
5. verification-before-completion
6. systematic-debugging
7. test-driven-development
8. subagent-driven-development
9. using-git-worktrees
10. receiving-code-review
11. requesting-code-review
12. finishing-a-development-branch
13. writing-skills

**扩展 8 skills**（gstack/GSD/ECC，非 P0）：

autoplan | browser-qa | design-pipeline | ship | office-hours | context-engineering | structured-artifacts | instinct-learning

**Meta 4**：memory-compression | karpathy-guidelines | caveman-compress | spec-validation

**Mattpocock 全局 2**：triage | improve-codebase-architecture

### FR-02.9 gstack 审查路由

| ID | 要求 | 验收 |
|----|------|------|
| FR-02.9.1 | eng-reviewer 所有变更必须 | CLAUDE.md 审查路由 |
| FR-02.9.2 | ceo/designer/qa/security 条件触发 | MANIFEST gstack_* |
| FR-02.9.3 | /review 命令 pointer autoplan 或各 reviewer | commands/review.md |

### FR-03 规格三轨混合

**来源**：OpenSpec, GSD-redux, 本地 spec/

| ID | 要求 | 验收 |
|----|------|------|
| FR-03.1 | OpenSpec：`openspec/changes/<id>/` 四件套 | templates/openspec/ 可 copy |
| FR-03.2 | GSD-redux：`.planning/phases/XX-{SPEC,CONTEXT,PLAN}.md` | templates/planning/ 可 copy |
| FR-03.3 | 轻量：`spec/<project>/{spec,design,tasks}.md` | templates/spec/ 可 copy |
| FR-03.4 | 同功能不可三轨并行 | MANIFEST 互斥规则 + spec/README 说明 |
| FR-03.5 | commands：/propose /apply /archive 对齐 OpenSpec | 路径指向 openspec/changes/ |
| FR-03.6 | brainstorming 产出 → docs/superpowers/specs/ | writing-plans 引用路径 |
| FR-03.7 | task-master 轻量模板 optional | templates/taskmaster/README.md + example_prd.md 可 copy；不全局 skill |

**三轨选型决策树**：

```
功能变更？
├─ 是，影响多模块/brownfield → OpenSpec (openspec/changes/)
├─ 是，大功能多阶段里程碑 → GSD-redux (.planning/)
└─ 否，≤3文件小功能 → spec/<project>/
```

### FR-04 Token 优化双轨

**来源**：rtk-ai/rtk, JuliusBrussee/caveman

| ID | 要求 | 验收 |
|----|------|------|
| FR-04.1 | RTK PreToolUse 重写 bash 命令 | git status 输出压缩 |
| FR-04.2 | RTK 未安装时 hook passthrough | 无 rtk 时不报错 |
| FR-04.3 | caveman-compress skill 压缩 agent 长输出 | 触发词有效 |
| FR-04.4 | SessionStart 激活 caveman lite 模式 | session-start-bootstrap 配置 |
| FR-04.5 | RTK 与 caveman 职责不重叠 | MANIFEST 归属分离 |

### FR-05 记忆与持续学习

**来源**：claude-mem, ECC instincts

| ID | 要求 | 验收 |
|----|------|------|
| FR-05.1 | claude-mem plugin 安装并启用 6 lifecycle hooks | mem-search 可检索 |
| FR-05.2 | memory-compression skill 与 plugin 互补 | 不重复存储逻辑 |
| FR-05.3 | stop-pattern-extraction → experiences/patterns/ | Stop 后文件写入 |
| FR-05.4 | confidence ≥0.9 → experiences/instincts/ | README 说明固化流程 |
| FR-05.5 | confidence <0.5 → experiences/rejected/ | 审计可追踪 |
| FR-05.6 | memory MCP 与 claude-mem 职责分离 | TOOL_MATCHING_GUIDE 说明 |

### FR-06 设计层

**来源**：awesome-design-md, ui-ux-pro-max-skill

| ID | 要求 | 验收 |
|----|------|------|
| FR-06.1 | templates/DESIGN.md YAML 格式（colors/typography/spacing/components） | 模板可 copy 到项目 |
| FR-06.2 | rules/DESIGN.md 规范用法，不含 token 正文 | 与 FRONTEND 分离 |
| FR-06.3 | ui-ux-pro-max 在 catalog/skills/ 按需启用 | migrate --skill ui-ux-pro-max |
| FR-06.4 | frontend 任务引用 DESIGN.md；ux-design-expert 为**项目级** agent | templates 说明 |

### FR-07 编码哲学

**来源**：forrestchang/andrej-karpathy-skills

| ID | 要求 | 验收 |
|----|------|------|
| FR-07.1 | karpathy-guidelines skill 四原则 | Think/Simplify/Surgical/Goal-Driven |
| FR-07.2 | 四原则写入 rules/CORE.md 交叉引用 | 不三处重复全文 |

### FR-08 Skill 格式权威

**来源**：anthropics/skills

| ID | 要求 | 验收 |
|----|------|------|
| FR-08.1 | 所有 skill 遵循 agent-skills-spec frontmatter | validate_config skill lint |
| FR-08.2 | writing-skills 含 skill-creator eval 流程 | 可按 template 创建新 skill |
| FR-08.3 | 渐进披露：metadata → SKILL.md → references/ | skills/README 说明 |
| FR-08.4 | 30 秒可读约束 | 每个 core skill ≤150 行 |

| FR-08.5 | anthropics document skills（docx/pdf/pptx/xlsx）入 SPEC catalog，按需项目安装 | 不全局堆叠 |

### FR-09 ECC 精选结构

**来源**：affaan-m/ECC（cherry-pick only）

| ID | 要求 | 验收 |
|----|------|------|
| FR-09.1 | agent.yaml manifest | 列出 enabled agents/skills/hooks |
| FR-09.2 | mcp-configs/ 按域分组 | core/dev/ops 与 .mcp.json 一致 |
| FR-09.3 | SKILL-PLACEMENT-POLICY：workflow 全局 / domain 项目 | SPEC.md 文档化 |
| FR-09.4 | ECC_HOOK_PROFILE=minimal/standard/strict | hooks/README 说明 |
| FR-09.5 | AgentShield 安全基线 | rules/SECURITY.md 引用 |

### FR-10 配置规范

**来源**：shanraisshan/claude-code-best-practice

| ID | 要求 | 验收 |
|----|------|------|
| FR-10.1 | settings.json 六级层级 documented | SPEC.md |
| FR-10.2 | 项目 rules 支持 paths: frontmatter lazy-load | templates 含示例 |
| FR-10.3 | Command → Agent → Skill 编排模式 | commands/ 不 duplicate agent body |
| FR-10.4 | subagent 不可用 bash 调 subagent | rules/AGENTS.md |

### FR-11 MCP 集成

**来源**：github-mcp-server, zilliztech/claude-context

| ID | 要求 | 验收 |
|----|------|------|
| FR-11.1 | gh MCP 已配置且 toolset 可裁剪 | mcp-configs/dev.json |
| FR-11.2 | claude-context 可选 MCP 在 mcp-configs/dev.json `optional` 块 + rules/CONTEXT.md 启用指南 | 大 monorepo 文档可查 |
| FR-11.3 | RULES_MCP.md 单一权威源原则 | 无多处 MCP 定义 |
| FR-11.4 | sync 不同步 .mcp.json | SYNC_GUIDE 明确 |

### FR-12 多编辑器同步

**来源**：caveman 单源模式, 本地 sync.ps1

| ID | 要求 | 验收 |
|----|------|------|
| FR-12.1 | sync.ps1 v11 软链接 CLAUDE.md | DryRun 通过 |
| FR-12.2 | AGENTS.md 镜像生成（Cursor autodiscovery） | Cursor 可加载 |
| FR-12.3 | skills/ agents/ 目录联接 | Junction 正确 |
| FR-12.4 | rules/ 格式转换复制 | .mdc/.md 各编辑器原生 |
| FR-12.5 | Windsurf global_rules ≤6000 字符摘要 | sync 自动生成 |
| FR-12.6 | hooks/commands/mcp 不同步 | SYNC_GUIDE 明确 |
| FR-12.7 | _editor_hook_launcher v3 编辑器跳过 | 无 hook 循环 |

| FR-12.8 | sync.sh v11 与 sync.ps1 行为对齐（macOS/Linux） | sync.sh DryRun |
| FR-12.9 | Qoder/CodeArts 可选同步（沿用 sync.ps1 已有目标） | 文档说明 |

### FR-13 CI 模板

**来源**：anthropics/claude-code-action

| ID | 要求 | 验收 |
|----|------|------|
| FR-13.1 | templates/github-actions/claude-code-action.yml | YAML 合法 |
| FR-13.2 | 支持 PR review / issue triage 模式注释 | 模板含说明 |

### FR-14 本地 Legacy 迁移

**来源**：本地 ~/.claude 对照

| ID | 要求 | 验收 |
|----|------|------|
| FR-14.1 | migrate-from-legacy.py 扫描 120 skills | 输出 keep/deprecate/project 清单 |
| FR-14.2 | 56 agents 审计 → 保留 ≤15 + reviewer | deprecated 清单 |
| FR-14.3 | 50 hooks 合并 → 8 核心 + profile | hooks/README 更新 |
| FR-14.4 | 有效 patterns 不丢失 | experiences/patterns/ 有迁移记录 |
| FR-14.5 | 462 行 CLAUDE.md 重写 ≤200 行 | 行数检查 |

### FR-15 入口文档

| ID | 要求 | 验收 |
|----|------|------|
| FR-15.1 | CLAUDE.md 仅路由+指针+铁律摘要 | ≤200 行 |
| FR-15.2 | SPEC.md 完整索引+21 仓库溯源 | 每个 P0 组件有 source |
| FR-15.3 | SYNC_GUIDE.md 同步策略准确 | 与用户要求一致 |

| FR-15.4 | TOOL_MATCHING_GUIDE 语义匹配 | 自然语言→工具 |

### FR-17 mattpocock/skills 整合（catalog 按需）

| ID | 要求 | 验收 |
|----|------|------|
| FR-17.1 | tdd/diagnose/caveman 不重复导入全局 | MANIFEST 去重 |
| FR-17.2 | diagnose/grill/handoff 可 catalog 按需 | catalog 或 migrate 文档 |
| FR-17.3 | git-guardrails 行为由 pre-bash-guard 覆盖 | hooks/README |
| FR-17.4 | design.md §15.4 去重表完整 | 文档审查 |

### FR-18 mattpocock 全局 skill + triage 路由

**来源**：mattpocock/skills

| ID | 要求 | 验收 |
|----|------|------|
| FR-18.1 | 全局 skill triage + improve-codebase-architecture | skills/ 存在且 frontmatter 合法 |
| FR-18.2 | CLAUDE.md 决策树含 Bug→triage 路由 | 决策树可见 |
| FR-18.3 | 与 systematic-debugging/brainstorming 无 trigger 重叠 | grep 互博检查 |

### FR-19 安全三层防御

**来源**：trailofbits/claude-code-config, dwarvesf/claude-guardrails, marc-shade/claude-code-security

| ID | 要求 | 验收 |
|----|------|------|
| FR-19.1 | settings.json deny 含凭证路径（~/.ssh, ~/.aws 等） | settings 审查 |
| FR-19.2 | defaultMode 非 bypassPermissions（企业默认 acceptEdits） | settings 审查 |
| FR-19.3 | rules/SECURITY.md §11 `/sandbox` 文档 | SECURITY.md |
| FR-19.4 | strict profile 可选 UserPromptSubmit 密钥扫描 | hooks/_optional/ + hooks/README |
| FR-19.5 | deny 须配合 `/sandbox` 才防 Bash 绕过（文档说明） | SECURITY.md §11 |

### FR-20 P3 外部仓库溯源

| ID | 要求 | 验收 |
|----|------|------|
| FR-20.1 | 每个 P3 concern 在 MANIFEST.yaml 有 source 字段 | YAML 审查 |
| FR-20.2 | design.md §15.6 与 SPEC.md 溯源表一致 | 文档交叉检查 |
| FR-20.3 | rules/SECURITY.md frontmatter 标注 P3 来源 | frontmatter source |

### FR-16 上下文管理

**来源**：GSD-redux, claude-mem, 本地 context-engineering

| ID | 要求 | 验收 |
|----|------|------|
| FR-16.1 | 上下文阈值：50%/70%/85% 策略写入 rules/WORKFLOW 或 CLAUDE 指针 | 文档可查 |
| FR-16.2 | /compact 战略压缩；/clear 切任务重置 | commands 存在 |
| FR-16.3 | pre-compact-state hook 保存状态 | hook 注册 |
| FR-16.4 | 长任务子 Agent  fresh context（subagent-driven-development） | skill 可触发 |
| FR-16.5 | 完成后输出状态摘要释放上下文（executing-plans） | skill 含要求 |

---

## 3. 非功能需求

| ID | 类别 | 要求 | 度量 |
|----|------|------|------|
| NFR-01 | Token | CLAUDE.md 始终加载预算 | ≤500 行（目标 ~165） |
| NFR-02 | 一致性 | MANIFEST 零 duplicate owner | validate_config 通过 |
| NFR-03 | 兼容性 | 三编辑器无 hook 冲突 | 手动验证清单 |
| NFR-04 | 可验证 | 所有变更可脚本验证 | validate_config + sync DryRun |
| NFR-05 | 可追溯 | 组件 → source_repo 映射 | SPEC.md 溯源表 |
| NFR-06 | 简洁 | Karpathy 四原则 + R10 | 代码 review 不判过度设计 |
| NFR-07 | 安全 | 无 hardcoded secrets | post-secret-detector |
| NFR-08 | 可维护 | 新 skill 可按 anthropics spec 创建 | writing-skills 流程 |
| NFR-09 | 可扩展 | domain skill 放项目级 | placement policy |
| NFR-10 | 持续学习 | 模式可固化 | experiences/ 闭环 |

---

## 4. FR → Task 追溯矩阵

| FR | 主要 Task |
|----|-----------|
| FR-01 | T1.1–T1.3, T1.7 |
| FR-02 | T2.1–T2.3, T2.6 |
| FR-03 | T3.1–T3.5 |
| FR-04 | T4.3, T4.4 |
| FR-05 | T4.1, T4.2, T4.8 |
| FR-06 | T5.1–T5.3 |
| FR-07 | T2.4, T1.6 |
| FR-08 | T2.5, T2.7, T6.5 |
| FR-09 | T1.3, T4.6, T4.7 |
| FR-10 | T1.6, T1.9, T2.3 |
| FR-11 | T4.6, T1.8 |
| FR-12 | T6.1–T6.7 |
| FR-13 | T5.4 |
| FR-14 | T7.1–T7.5 |
| FR-15 | T1.4, T1.7, T1.8, T6.4 |
| FR-16 | T2.3, T4.8, T1.4 |
| FR-17 | T8.3–T8.4, T10 |
| FR-18 | T10 |
| FR-19 | T11 |
| FR-20 | T10 |
| FR-03.7 | T8.5 |
| FR-11.2 | T8.6 |

---

## 5. 24 + P3 仓库整合规格详表

### 5.1 五柱（必须）

| 柱 | 仓库 | 保留优点 | 目标路径 |
|----|------|----------|----------|
| ① | superpowers | 13 skill 链、HARD-GATE、SessionStart | skills/, hooks/ |
| ② | GSD-redux | phase 模板、阈值、read-before-edit | rules/CONTEXT, templates/planning/ |
| ③ | OpenSpec | changes/ 结构、propose/apply/archive | templates/openspec/, commands/ |
| ④ | gstack | 5 审查 + 7 补全 agents、autoplan/ship | agents/, skills/autoplan,ship |
| ⑤ | claude-mem | 6 hooks、mem-search、plan/do | plugins/, hooks/ |

### 5.2 结构 + 格式 + 优化（P0）

| 仓库 | 保留优点 | 目标路径 |
|------|----------|----------|
| ECC | MANIFEST、catalog、hook profile | agent.yaml, catalog/ |
| anthropics/skills | SKILL.md spec | writing-skills, catalog/ |
| best-practice | lazy-load、settings 层级 | rules/BESTPRACTICE, CLAUDE.md |
| karpathy-skills | 四原则 | karpathy-guidelines, CORE.md |
| RTK + caveman | Token 双轨 | pre-rtk-rewrite, caveman-compress |
| github-mcp-server | gh MCP | .mcp.json |

### 5.3 P1 增强

awesome-design-md | ui-ux-pro-max | claude-code-action | claude-task-master（模式） | claude-context（策略） | ComposioHQ（索引） | **mattpocock/skills（全局 2 + catalog 3）**

### 5.4 P2 参考

x1xhlol | hesreallyhim | 30-seconds-of-code | gsd-build（废弃） | deer-flow（WORKFLOW 参考） | ruflo（排除，WORKFLOW 吸收）

### 5.5 P3 安全补强（cherry-pick，非柱）

| 仓库 | source | 落地 |
|------|--------|------|
| trailofbits/claude-code-config | main | SECURITY.md §11, settings.json |
| trailofbits/claude-code-devcontainer | main | templates/devcontainer/ |
| dwarvesf/claude-guardrails | main | hooks/_optional/pre-userprompt-secret-scan.py |
| lasso-security/claude-hooks | main | hooks/_optional/post-prompt-injection-scan.py |
| efij/awesome-claude-code-security | main | SPEC.md 外链 |
| EveryInc/compound-engineering-plugin | main | SPEC.md Cursor plugin 注明 |
| kumaran-is/claude-code-guide | main | rules/CONTEXT.md |
| domengabrovsek/claude | main | agents/README.md |
| marc-shade/claude-code-security | main | SECURITY.md §14 |
| disler/claude-code-hooks-mastery | main | hooks/tests/fixtures/ |

---

## 6. 本地对照参考（非需求源）

仅用于 Phase 7 迁移审计：

| 本地组件 | 当前数量 | 迁移规则 |
|----------|----------|----------|
| skills/ | ~120 | 与 superpowers 13 重复 → deprecated |
| skills/ domain | ~80 | 保留 → 项目 `.claude/skills/` 或 catalog |
| agents/ | ~56 | 保留 ≤15 通用 + language reviewer |
| hooks/ | ~50 | 合并 8 核心；其余 profile=strict 可选 |
| rules/ | ~22 | 合并 8 alwaysApply；语言 → lazy |
| commands/ | ~10 | 对齐 superpowers+OpenSpec 链 |
| experiences/patterns/ | ~4 | 保留有效项 |

---

## 7. 验收标准（总清单）

### 6.1 骨架

- [x] MANIFEST.yaml 零 conflict（v2.1）
- [x] agent.yaml 可解析
- [x] CLAUDE.md ≤500 行（~165）
- [x] AGENTS.md pointer 模式
- [x] rules/ 9 文件
- [x] skills/ 25 global
- [x] agents/ 20 global
- [x] 五柱表在 CLAUDE.md

### 6.2 工作流

- [x] 13 superpowers + 8 扩展 skills
- [x] SessionStart bootstrap 唯一
- [x] brainstorming HARD-GATE
- [x] discuss→plan→execute→verify→ship + /review
- [x] gstack 审查路由 5 agents

### 6.3–6.7

见 [compliance.md](./compliance.md)（v2.1 已通过 validate_config 8 checks）

### 6.8 文档

- [x] design/spec/tasks v2.3
- [x] SPEC.md 22 仓库溯源
- [x] design §15.5 追溯矩阵

### 6.9 Phase 8（v2.3）

- [x] mattpocock catalog ×3（diagnose, grill-with-docs, handoff）
- [x] templates/taskmaster/（FR-03.7）
- [x] claude-context optional MCP（FR-11.2）
- [x] SYNC_GUIDE agents 20 / rules 9

### 6.10 v2.3 doc drift

- [x] design §4/§9/§16 与实测一致
- [x] tasks 里程碑 M1/M4/M7 门控对齐

---

## 8. 约束与假设

**约束**：
- Windows 为主环境（sync.ps1）；macOS/Linux 用 sync.sh
- Claude Code hooks 不同步到编辑器
- 不整包导入 ECC/GSD/deer-flow

**假设**：
- 用户有 Claude Code CLI 访问权限
- GitHub token 用于 gh MCP（可选）
- RTK 可选安装（未安装则 passthrough）

---

## 9. 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 配置膨胀 context rot | 高 | CLAUDE.md≤500；P0 skill 仅 4 强制 |
| 三轨 spec 混用 | 中 | MANIFEST 互斥 + spec/README |
| 编辑器 hook 循环 | 高 | 不同步 hooks；launcher v3 |
| Legacy 优点丢失 | 中 | migrate-from-legacy + experiences |
| RTK 未安装 | 低 | passthrough |
| Windsurf 6000 字符 | 中 | sync 自动摘要 |

---

_版本：2.3 | 日期：2026-05-25 | Phase 8 完成 + 追溯矩阵_
