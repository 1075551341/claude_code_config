# .claude 配置集成设计文档

> 版本 v9.0 | 基于仓库分析 01-ANALYSIS.md | 骨架: 五柱×五阶段×三横切

---

## 一、设计原则

```
P1. 骨架清晰 — 五柱各司其职，不互博，不重叠
P2. 按需加载 — 必须 ≤ 5个 always-on skills，其余 lazy/on-demand
P3. Token first — 所有设计决策以 token 效率为优先约束
P4. 软链同步 — 规则/技能/Agent 通过脚本同步到其他编辑器，不手动维护双份
P5. 错误暴露 — 异常必须传播或显式处理，禁止 silent fail
P6. 工具复用 — 优先调用已安装工具（codegraph/UA/claude-mem），避免重复造轮子
```

---

## 二、系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户输入 / 会话开始                         │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              骨架层（always-on，强制加载）                      │
│  CLAUDE.md(入口) + rules/CORE.md + P0 skills(5个)            │
│  SessionStart hooks: superpowers-bootstrap + claude-mem       │
└────────────┬────────────────────────────────────────────────┘
             ↓
┌────────────────────────────────────────────────────────────┐
│                    五阶段处理流程                              │
│                                                              │
│  ①规划           ②规格           ③执行                        │
│  brainstorming → writing-plans → executing-plans             │
│  (HARD-GATE)    OpenSpec/GSD    SDD+TDD+subagent             │
│                                                              │
│  ④验证           ⑤学习                                        │
│  verification  → instinct-learning + memory-compression       │
│                  + claude-mem 持久化                          │
└────────────┬───────────────────────────────────────────────┘
             ↓
┌────────────────────────────────────────────────────────────┐
│                    三横切关注点                                │
│                                                              │
│  L1 治理    ECC hooks(防互博+分级) + deer-flow编排(可选)        │
│  L2 优化    RTK(Shell) + caveman(输出) + codegraph(探索)       │
│  L3 洞察    codegraph(符号) + UA(全貌) + Firecrawl/Exa(调研)   │
└────────────┬───────────────────────────────────────────────┘
             ↓
┌────────────────────────────────────────────────────────────┐
│                    工具路由层                                  │
│  MANIFEST.yaml → P0 skills → catalog → agent 委派 → MCP      │
│  codegraph_explore → 先于 Grep/Glob（代码探索首选）             │
│  claude-mem search → 先于重复文件读取（历史记忆首选）             │
└────────────────────────────────────────────────────────────┘
```

---

## 三、目录结构设计（v9.0）

```
~/.claude/
├── CLAUDE.md              # 入口：优先级链 + 铁律 + 路由（精简，≤200行）
├── SPEC.md                # 配置法典（详细参考，不强制加载）
├── MANIFEST.yaml          # 组件归属：防互博权威源
│
├── rules/                 # 10条规则
│   ├── CORE.md            # ★ always-on：编码规范+铁律+阈值（骨架）
│   ├── WORKFLOW.md        # glob触发：完整工作流阶段定义
│   ├── CONTEXT.md         # glob触发：上下文工程（3阈值+压缩策略）
│   ├── BESTPRACTICE.md    # glob触发：综合最佳实践
│   ├── AGENTS.md          # 按需：多Agent协作规则
│   ├── DESIGN.md          # 按需：UI/设计规范（DESIGN.md触发）
│   ├── GIT.md             # 按需：Git版本控制规范
│   ├── MCP.md             # 按需：MCP使用规范
│   ├── SECURITY.md        # 按需：安全开发规范
│   └── OPENSPEC.md        # 新增：OpenSpec delta-spec 使用规范【新增】
│
├── skills/                # 34个技能（5 P0 + 29 lazy）
│   ├── using-superpowers/    # P0:always — 技能发现路由
│   ├── brainstorming/        # P0:always — 方案设计HARD-GATE
│   ├── change-impact-analysis/  # P0:always — 变更影响分析
│   ├── verification-before-completion/  # P0:always — 完成前验证
│   ├── systematic-debugging/ # P0:always — 系统化调试
│   ├── [24 lazy skills...]   # 按需加载
│   └── # 新增:
│       ├── workstream-management/  # 新增:并行任务流【新增】
│       ├── adr-management/         # 新增:架构决策记录【新增】
│       └── onboarding-guide/       # 新增:项目引导（OpenSpec onboard）【新增】
│
├── agents/                # 25个智能体（含 dx-reviewer）
│
├── hooks/                 # 18个生命周期钩子（Claude Code专用）
│   ├── hooks.json         # 钩子注册表
│   ├── session-start/     # 会话开始：bootstrap + mem-inject
│   ├── pre-compact/       # 压缩前：状态保存（ECC PreCompact模式）【增强】
│   ├── post-tool-use/     # 工具后：codegraph auto-sync check
│   ├── pre-bash/          # Shell前：RTK rewrite + tmux check【增强】
│   └── context-monitor/   # 上下文监控：ECC GateGuard升级版【增强】
│
├── plugins/               # 18个插件（15启用+3禁用）
│   └── [无变化]
│
├── commands/              # 斜杠命令
│   ├── /discuss, /plan, /execute, /verify, /ship, /compact
│   ├── /deep-research      # Firecrawl+Exa+WebSearch
│   ├── /deer-flow          # 外部编排
│   ├── /opsx:*             # OpenSpec命令（via openspec plugin）
│   └── /workstream         # 新增:并行任务流命令【新增】
│
├── docs/                  # 调研+同步指南
│   ├── SYNC_GUIDE.md      # v14 同步指南
│   ├── REPO_ANALYSIS.md   # 本次分析报告（归档）
│   └── ADR/               # 架构决策记录目录【新增】
│       └── 2026-06-10-v9-config-integration.md
│
├── scripts/
│   ├── sync.ps1           # 同步脚本（现有）
│   └── sync.sh            # 新增Linux/macOS版本【新增】
│
├── catalog/               # 按需复制的技能/Agent/规则库
└── templates/             # OpenSpec/GSD/DESIGN模板
```

---

## 四、CLAUDE.md v9.0 核心变更

### 变更点 1：优先级链精细化
```
用户显式指令 > CLAUDE.md指针 > 激活skill > lazy规则 > alwaysApply规则 > 默认
+ 工具路由: codegraph_explore > Grep/Glob（代码探索）
+ 记忆路由: claude-mem search > 重复文件读取
```

### 变更点 2：搜索策略明确化
```
搜索策略（四轨互补）:
- 代码结构探索 → codegraph（first）→ Grep fallback
- 项目全貌理解 → understand-anything（/understand-chat）
- 外部技术文档 → Context7 MCP
- 外部信息/调研 → Firecrawl(爬虫) + Exa(语义)
- 概念/历史记忆 → claude-mem search
```

### 变更点 3：workstreams 支持
```
GSD v1.42.3 并行任务流:
- /workstream new <name>  — 创建独立任务流（git worktree隔离）
- /workstream status      — 查看所有流状态
- /workstream merge <name> — 合并任务流（claude-mem整合记忆）
```

### 变更点 4：ADR 机制
```
架构决策记录（Architecture Decision Records）:
位置: docs/ADR/YYYY-MM-DD-<title>.md
格式: 状态/背景/决策/后果
触发: 架构变更 / 技术选型 / 重大重构
```

### 变更点 5：铁律扩展至 R17-R18
```
R17 代码探索优先 — 代码探索先用 codegraph_explore，再用 Grep
R18 记忆优先     — 历史上下文先查 claude-mem，再重复分析
```

---

## 五、技能加载策略（精确设计）

### Always-on（骨架，5个）
```yaml
# 强制加载，每会话必须
P0_skills:
  - using-superpowers      # 发现路由：知道用哪个技能
  - brainstorming          # 方案设计：禁止未审批就实现
  - change-impact-analysis # 影响分析：改前必须分析
  - verification-before-completion  # 完成验证：改后必须验证
  - systematic-debugging   # 系统调试：Bug处理规范
```

### Lazy-glob 触发（上下文类）
```yaml
lazy_glob:
  - pattern: "**/*.ts,**/*.tsx"
    skills: [test-driven-development]
  - pattern: "DESIGN.md,design/**"
    skills: [design-pipeline]
  - pattern: ".planning/**"
    skills: [writing-plans, executing-plans]
  - pattern: "openspec/**"
    skills: [spec-validation]
  - pattern: "**/*.test.*"
    skills: [test-driven-development]
```

### 按需（关键词触发）
```yaml
on_demand:
  - keywords: ["并行", "多任务", "worktree"]
    skills: [workstream-management, using-git-worktrees]
  - keywords: ["架构决策", "技术选型", "ADR"]
    skills: [adr-management]
  - keywords: ["/compact", "记忆压缩", "上下文腐烂"]
    skills: [memory-compression, instinct-learning]
  - keywords: ["/deep-research", "深度调研", "多角度"]
    skills: [deep-research-workflow]
```

---

## 六、Hook 架构设计（v9.0）

### Hook 分级映射
```
ECC minimal  ← 本地必须层（5个核心hook）
ECC standard ← 本地标准层（当前18个hook）
ECC strict   ← 本地增强层（含GateGuard+安全规则）
```

### 新增/增强 hooks

#### context-monitor（增强，基于ECC GateGuard）
```json
{
  "event": "Stop",
  "description": "上下文监控：usage>70%警告，>90%强制压缩，检测tool loop",
  "checks": [
    "context_usage_percent → 70%警告/90%强制",
    "tool_call_repeat_count → >3次相同调用警告",
    "scope_creep_detection → 偏离原始任务警告",
    "cost_estimate → 高成本操作警告（可关闭）"
  ]
}
```

#### pre-compact（增强，ECC PreCompact模式）
```json
{
  "event": "PreCompact",
  "description": "压缩前：保存工作状态到 .claude/state.json",
  "saves": [
    "current_task_summary",
    "in_progress_files",
    "pending_decisions",
    "last_verified_checkpoint"
  ]
}
```

#### post-tool-use/codegraph-sync（新增）
```json
{
  "event": "PostToolUse",
  "tools": ["Write", "Edit", "MultiEdit"],
  "description": "文件变更后触发 codegraph sync（增量更新知识图）",
  "condition": "changed_files > 3 OR significant_structure_change"
}
```

---

## 七、同步脚本设计（v9.0）

### sync.sh（新增，Linux/macOS）
```bash
#!/bin/bash
# 同步模式: index（默认）| full
# 目标: Cursor | Windsurf | VS Code | Zed

SYNC_MODE="${1:-index}"
TARGETS="${2:-cursor,windsurf}"

# 7总纲软链接
for file in CLAUDE.md SPEC.md MANIFEST.yaml; do
    ln -sf ~/.claude/$file $EDITOR_DIR/$file
done

# skills/ agents/ 联接
ln -sf ~/.claude/skills $EDITOR_DIR/.claude/skills
ln -sf ~/.claude/agents $EDITOR_DIR/.claude/agents

# rules/ 单文件链接（index模式）
for rule in ~/.claude/rules/*.md; do
    ln -sf $rule $EDITOR_DIR/.cursor/rules/$(basename $rule .md).mdc
done

# Full模式：格式转换
if [ "$SYNC_MODE" = "full" ]; then
    # 转换为各编辑器原生格式（mdc/jsonc等）
    node scripts/convert-rules.js
fi
```

### 去重策略
- skills/agents 软链（不复制），保证单一真相源
- 同名 skill：本地精简版优先（`--priority local`）
- 编辑器专属配置（hooks/settings）不同步

---

## 八、规格三轨（v9.0）保持不变

| 轨道 | 路径 | 场景 | 触发命令 |
|------|------|------|----------|
| OpenSpec | `openspec/changes/<id>/` | 功能变更/brownfield | /opsx:propose → apply → archive |
| GSD Redux | `.planning/phases/` | 大功能多阶段 + workstreams | /gsd-plan-phase + /workstream |
| 轻量 | `spec/<project>/` | ≤3文件小功能 | /discuss → /plan → /execute |

---

## 九、审查路由（v9.0，增加DX维度）

```
所有变更     → eng-reviewer（必须）
产品/新功能  → + ceo-reviewer
UI/UX变更   → + designer + dx-reviewer（新增）
安全敏感     → + security-reviewer（OWASP+STRIDE）
iOS变更      → + ios-specialist
infra/配置   → CEO可跳过
跨模型验证   → + codex-reviewer
DX体验变更   → + dx-reviewer（新增）
```

---

## 十、Token 效率设计汇总

```
三轨优化:
  Shell输出   → RTK proxy（60-90%压缩）
  AI输出      → caveman-compress（65%减少）+ caveman memory（46%上下文减少）
  代码探索    → codegraph（47%少token，58%少调用）

上下文管理:
  <70%  → 正常运行
  70%   → 择机压缩（优先压缩历史消息）
  90%   → 强制 /compact
  100%  → ⛔ 绝对禁止

Token 节省来源:
  codegraph        → -47% 探索token
  RTK              → -60~90% shell输出
  caveman          → -65% AI输出
  deferred MCP     → -16% 初始context（task-master等）
  claude-mem 3层   → -N% 冗余文件重读
  CLAUDE.md压缩    → -46% 启动context（caveman-compress）
```

---

## 十一、接口契约（API boundaries）

### MCP 工具优先级
```
代码查询: codegraph_explore > codegraph_search > Grep > Read
变更影响: codegraph_impact > change-impact-analysis skill > 手动分析
历史记忆: claude-mem:search > claude-mem:get_observations > 重新分析
技术文档: Context7:query-docs > Firecrawl > 普通搜索
外部调研: Firecrawl(爬取) + Exa(语义搜索) > 普通搜索
```

### 技能触发契约
```
变更前 → change-impact-analysis（必须）
完成前 → verification-before-completion（必须）
Bug时  → systematic-debugging（必须）
架构时 → brainstorming → HARD-GATE → 用户批准 → 实现
```
