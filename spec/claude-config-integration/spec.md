# Spec — .claude 配置整合需求规格

> **设计源**：21 个 GitHub 仓库 PRIMARY | 本地 `~/.claude` 仅迁移对照  
> **关联**：[design.md](./design.md) | [tasks.md](./tasks.md)

---

## 1. 概述

### 1.1 背景

需将 21 个社区优秀 AI Agent 配置仓库的优点整合为统一的 `~/.claude` 全局配置体系，满足：

- Claude Code 完整运行时（hooks/MCP/commands）
- Cursor / Windsurf / Trae 通过软链接同步核心配置
- 非简单任务有计划、有规格、有验证
- 持续学习、上下文可控、Token 不浪费
- 无左右手互博

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

### FR-01 PRIMARY 骨架（5 源合一）

**来源**：superpowers, ECC, anthropics/skills, best-practice, claude-mem

| ID | 要求 | 验收 |
|----|------|------|
| FR-01.1 | 全局 skills ≤20：13 workflow + ≤7 meta（memory/karpathy/caveman/spec-validation/ui-ux 等） | SKILL.md 计数 ≤20 |
| FR-01.2 | 全局 agents ≤15，薄编排无领域知识 | agents/README 声明职责 |
| FR-01.3 | rules ≤8 alwaysApply 文件 | rules/ 无冗余重复 |
| FR-01.4 | MANIFEST.yaml 覆盖所有 concern | validate_config --check-manifest 通过 |
| FR-01.5 | agent.yaml harness manifest 可解析 | YAML lint 通过 |
| FR-01.6 | 每个组件标注 source_repo | SPEC.md 溯源表完整 |

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

**≤7 meta skills 清单**（其他仓库）：

14. memory-compression（claude-mem）
15. karpathy-guidelines（karpathy-skills）
16. caveman-compress（caveman）
17. spec-validation（OpenSpec）
18. ui-ux-pro-max（optional, nextlevelbuilder）

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
| FR-06.3 | ui-ux-pro-max skill 可选启用 | search 脚本可运行 |
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
| FR-11.2 | claude-context 可选 MCP 条目（commented） | 大 monorepo 启用指南 |
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

| FR-15.4 | TOOL_MATCHING_GUIDE.md 语义匹配表与 MCP 分组一致 | 自然语言→工具 |

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
| NFR-01 | Token | CLAUDE.md 始终加载预算 | ≤200 行 |
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

---

## 5. 21 仓库整合规格详表

### 5.1 P0 — 骨架组成（必须实现）

| # | 仓库 | 保留优点 | 目标路径 | 验收命令/标准 |
|---|------|----------|----------|---------------|
| 1 | superpowers | 13 skill 链、HARD-GATE、SessionStart bootstrap、两阶段 review | skills/, hooks/ | brainstorming 触发 |
| 2 | anthropics/skills | SKILL.md spec、template、skill-creator eval | skills/writing-skills/ | 新建 skill 通过 quick_validate |
| 3 | ECC | agent.yaml、mcp-configs、placement policy、hook profile、AgentShield | agent.yaml, mcp-configs/, rules/SECURITY.md | manifest 解析 |
| 4 | best-practice | settings 层级、rules lazy-load、Command→Agent→Skill | rules/, commands/ | lazy rule 按 glob 触发 |
| 5 | claude-mem | 6 hooks、SQLite+Chroma、mem-search、plan/do skills | plugins/, hooks/ | 跨会话检索 |
| 6 | OpenSpec | changes/ 结构、config.yaml、propose/apply/archive | templates/openspec/, commands/ | /propose 创建 change |
| 7 | karpathy-skills | 四原则 skill | skills/karpathy-guidelines/ | 触发词有效 |
| 8 | RTK | PreToolUse bash 重写、filters 概念 | hooks/pre-rtk-rewrite.* | git status 压缩 |
| 9 | caveman | 输出压缩 skill、lite 模式 | skills/caveman-compress/ | 长输出压缩 |
| 10 | github-mcp-server | 官方 gh MCP、toolset 裁剪 | .mcp.json, mcp-configs/ | gh 工具可用 |

### 5.2 P1 — 选择性增强

| # | 仓库 | 保留优点 | 目标路径 |
|---|------|----------|----------|
| 11 | GSD-redux | phase SPEC/CONTEXT/PLAN、workflow guards | templates/planning/ |
| 12 | awesome-design-md | DESIGN.md YAML token | templates/DESIGN.md |
| 13 | ui-ux-pro-max | BM25 设计数据库 skill | skills/ui-ux-pro-max/ |
| 14 | claude-task-master | PRD→tasks、MCP optional | templates/taskmaster/ |
| 15 | claude-context | 语义代码索引 MCP | mcp-configs/dev.json optional |
| 16 | claude-code-action | GitHub Action 模板 | templates/github-actions/ |
| 17 | ComposioHQ/awesome-claude-skills | 1000+ skill 索引 | SPEC.md 外链 |
| 18 | shanraisshan/best-practice | orchestration 示例 | commands/ README |

### 5.3 P2 — 参考 only

| # | 仓库 | 处理方式 |
|---|------|----------|
| 19 | x1xhlol/system-prompts | SPEC.md 研究索引；GPL；禁止 copy 到 runtime |
| 20 | hesreallyhim/awesome-claude-code | SPEC.md catalog 外链 |
| 21 | 30-seconds-of-code | skills「30 秒约束」原则引用 |
| — | gsd-build/get-shit-done | 废弃；仅用 GSD-redux |
| — | deer-flow | SPEC.md 注明独立 super-agent 平台 |
| — | bytedance/deer-flow | sandbox+IM 概念参考，不复制目录 |

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

- [ ] MANIFEST.yaml 存在且零 conflict
- [ ] agent.yaml 可解析
- [ ] CLAUDE.md ≤200 行
- [ ] AGENTS.md 与 CLAUDE.md 不重复长文
- [ ] rules/ ≤8 alwaysApply 文件
- [ ] skills/ ≤20 global core
- [ ] agents/ ≤15

### 6.2 工作流

- [ ] 13 superpowers skills 完整
- [ ] SessionStart bootstrap 唯一
- [ ] brainstorming HARD-GATE 生效
- [ ] discuss→plan→execute→verify→ship 链可用
- [ ] TDD + verification-before-completion 可触发

### 6.3 规格

- [ ] templates/openspec/ 四件套
- [ ] templates/planning/ GSD 三件套
- [ ] templates/spec/ 轻量三件套
- [ ] /propose /apply /archive 路径正确
- [ ] spec/README 三轨边界清晰

### 6.4 运行时

- [ ] claude-mem plugin 启用
- [ ] RTK hook passthrough/压缩
- [ ] caveman-compress skill
- [ ] hooks profile minimal/standard/strict
- [ ] stop-pattern-extraction 写 patterns/

### 6.5 设计

- [ ] templates/DESIGN.md
- [ ] rules/DESIGN.md
- [ ] ui-ux-pro-max optional

### 6.6 同步

- [ ] sync.ps1 v11 DryRun 通过
- [ ] CLAUDE.md 软链接正确
- [ ] Cursor/Windsurf/Trae 加载无冲突
- [ ] validate_config.py 零错误

### 6.7 迁移

- [ ] migrate-from-legacy.py 清单完整
- [ ] deprecated 项有记录
- [ ] 有效 patterns 未丢失

### 6.8 文档

- [ ] design.md / spec.md / tasks.md 三件套完整
- [ ] SPEC.md 21 仓库溯源表

### 7.8 上下文

- [ ] 上下文阈值策略 documented
- [ ] /compact /clear commands 可用
- [ ] pre-compact-state hook 注册

### 7.9 需求符合性

- [ ] design.md §18 自检 12 项全 ✓
- [ ] 21 仓库均有 spec 映射
- [ ] FR→Task 矩阵无遗漏

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
| 配置膨胀 context rot | 高 | CLAUDE.md≤200；P0 skill 仅 4 强制 |
| 三轨 spec 混用 | 中 | MANIFEST 互斥 + spec/README |
| 编辑器 hook 循环 | 高 | 不同步 hooks；launcher v3 |
| Legacy 优点丢失 | 中 | migrate-from-legacy + experiences |
| RTK 未安装 | 低 | passthrough |
| Windsurf 6000 字符 | 中 | sync 自动摘要 |

---

_版本：1.1 | 日期：2026-05-22 | 审查修订_
