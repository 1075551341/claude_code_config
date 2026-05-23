# .claude 架构设计文档

## 1. 骨架选型决策

### 推荐骨架：Superpowers × GSD × OpenSpec × gstack × claude-mem

**不推荐** gstack 作主骨架原因：gstack 是 23 个角色 skill 的集合，是执行层工具，不是方法论骨架。  
**不推荐** claude-task-master 作主骨架原因：其 MCP 服务器模式需要外部依赖，适合作 optional 组件。  
**不推荐** ECC 单独作骨架：作为 hook 集成进 memory 系统即可。

### 骨架分工

| 层 | 来源 | 职责 |
|----|------|------|
| **方法论层** | superpowers | 完整开发流程：brainstorm→spec→plan→execute→review |
| **上下文工程层** | GSD | 相位隔离：每任务独立子agent，主会话保持<40%上下文 |
| **规格层** | OpenSpec | Delta spec 格式，变更可追溯，spec 为单一真相源 |
| **角色执行层** | gstack | 23个专家角色 skill（CEO/Designer/Eng/QA/Security...）|
| **记忆层** | claude-mem | 跨会话压缩记忆，hooks 自动注入 |
| **错误学习层** | ECC | 错误上下文捕获 → gotchas.md |
| **规范层** | shanraisshan/claude-code-best-practice + caveman | rules 核心约束 |
| **同步层** | claude-task-master 的跨编辑器思路 | 软链同步脚本 |

---

## 2. 统一工作流

```
用户输入
   │
   ▼
[brainstorm]  ← superpowers:brainstorming
   │  设计文档 (.planning/design.md)
   ▼
[propose]     ← OpenSpec: openspec/changes/<name>/proposal.md
   │  delta spec + 影响范围
   ▼
[plan]        ← superpowers:writing-plans + GSD phase structure
   │  docs/plans/YYYY-MM-DD-<feature>.md (任务列表, 文件映射)
   ▼
[execute]     ← superpowers:subagent-driven-development
   │  GSD 模式: 每任务独立子agent, fresh 200K context
   │  两阶段审查: spec compliance → code quality
   ▼
[review]      ← gstack 角色路由
   │  eng-review (必须) + CEO/design review (按需)
   ▼
[ship]        ← gstack:/ship (tests, docs, coverage)
   │
   ▼
[learn]       ← claude-mem hooks 压缩 → memory/index.md
               ECC 错误捕获 → memory/knowledge/gotchas.md
```

---

## 3. 文件夹结构（最终骨架）

```
~/.claude/                              # Claude Code 全局配置根
│
├── CLAUDE.md                           # 核心入口：上下文路由 + 工作规范
├── AGENTS.md                           # Agent 路由表（gstack 模式）
├── settings.json                       # MCP + 权限 + hooks 配置
│
├── rules/                              # ← 同步到其他编辑器
│   ├── 01-core.md                      # 基础原则（caveman 极简 + best-practice）
│   ├── 02-code.md                      # 代码规范
│   ├── 03-git.md                       # Git 工作流
│   ├── 04-testing.md                   # TDD 优先（superpowers 方法）
│   └── 05-security.md                  # 安全规范（gstack OWASP）
│
├── agents/                             # ← 同步到其他编辑器
│   ├── architect.md                    # 架构师（superpowers brainstorming 模式）
│   ├── eng-reviewer.md                 # Eng Review（gstack plan-eng-review）
│   ├── ceo-reviewer.md                 # CEO Review（gstack plan-ceo-review）
│   ├── designer.md                     # 设计师（gstack + VoltAgent/awesome-design-md）
│   ├── qa.md                           # QA（gstack + TDD）
│   ├── debugger.md                     # 调试（ECC 错误捕获）
│   ├── researcher.md                   # 研究（deer-flow 多agent）
│   └── security.md                     # 安全审计（gstack OWASP/STRIDE）
│
├── skills/                             # ← 同步到其他编辑器
│   ├── _template.md                    # Skill 编写规范（superpowers:writing-skills）
│   ├── dev/
│   │   ├── brainstorm.md               # superpowers:brainstorming
│   │   ├── write-plan.md               # superpowers:writing-plans
│   │   ├── subagent-execute.md         # superpowers:subagent-driven-development
│   │   ├── tdd.md                      # superpowers:test-driven-development
│   │   ├── refactor.md                 # 安全重构
│   │   └── debug-fix.md                # ECC 错误捕获模式
│   ├── docs/
│   │   ├── write-spec.md               # OpenSpec delta spec 格式
│   │   ├── write-readme.md
│   │   └── adr.md                      # 架构决策记录
│   ├── design/
│   │   ├── ui-component.md             # VoltAgent + nextlevelbuilder
│   │   └── design-system.md
│   └── ops/
│       ├── context-save.md             # gstack:context-save
│       └── context-restore.md          # gstack:context-restore
│
├── commands/                           # Claude Code 专用（不同步）
│   ├── brainstorm.md                   # /brainstorm → skill:dev/brainstorm
│   ├── spec.md                         # /spec → OpenSpec propose
│   ├── plan.md                         # /plan → skill:dev/write-plan
│   ├── execute.md                      # /execute → skill:dev/subagent-execute
│   ├── review.md                       # /review → agent 路由（eng/ceo/design）
│   ├── ship.md                         # /ship → gstack ship 流程
│   ├── fix.md                          # /fix → debugger agent
│   ├── mem-save.md                     # /mem-save → 手动保存记忆
│   └── sync-editors.md                 # /sync → 触发软链同步
│
├── hooks/                              # Claude Code 专用（不同步）
│   ├── pre-tool-use/
│   │   └── read-before-edit.js         # GSD 模式：编辑前必须读文件
│   ├── post-session.sh                 # 会话后压缩记忆（claude-mem 模式）
│   ├── pre-session.sh                  # 会话前注入记忆索引
│   └── on-error.sh                     # 错误捕获（ECC 模式）
│
├── memory/                             # 跨会话持久化（claude-mem 模式）
│   ├── index.md                        # 轻量索引，每次会话自动加载（<500 token）
│   ├── knowledge/
│   │   ├── architecture.md             # 架构决策
│   │   ├── conventions.md              # 约定
│   │   └── gotchas.md                  # 错误教训（ECC 输出）
│   └── sessions/                       # AI 压缩的历史会话摘要
│
├── mcp/                                # MCP 配置（不同步）
│   ├── README.md
│   └── settings.json                   # github + filesystem + taskmaster
│
└── scripts/
    ├── sync-editors.sh                 # 核心：软链同步工具
    └── setup.sh                        # 一键初始化
```

**项目级（每个项目）**：
```
{project}/.claude/
├── CLAUDE.md           # import 全局 + 项目专属上下文
└── openspec/           # OpenSpec 变更记录（项目专属）
    ├── specs/          # 合并后的主规格
    └── changes/        # 每个功能的 delta spec
```

---

## 4. 关键设计决策

### D1: 方法论优先，工具其次
superpowers 的流程是骨架，gstack/GSD/OpenSpec 是增强工具。不强制全套，每个独立可用。

### D2: 上下文相位隔离（GSD 核心思想）
- 主会话只做编排，不做实现
- 每个任务派发独立子 agent，保持 fresh context
- 主会话目标：始终 <40% context 占用

### D3: Spec 即合约（OpenSpec 核心思想）
- 所有非简单变更必须先有 delta spec
- 代码实现必须能追溯到 spec
- spec archive 时合并到主 specs

### D4: 两阶段审查（superpowers 核心思想）
1. Spec compliance reviewer：实现是否符合规格
2. Code quality reviewer：代码质量独立评估

### D5: 记忆外化（claude-mem 核心思想）
- 会话内知识不依赖上下文，写入 memory/
- hooks 自动压缩，index.md 保持精简
- 错误必须记录到 gotchas.md，防止重蹈覆辙

### D6: 软链单一来源
- `~/.claude/` 是唯一真相源
- 其他编辑器只读软链，不维护副本
- 同步范围：rules/, agents/, skills/, CLAUDE.md（不含 hooks/mcp/memory）
