# 配置工程优化 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** L0入口去重(~25% token节省) + 索引补全 + Hook分级实现 + MANIFEST动态化 + Scripts去重 + R16合规

**Architecture:** 四层依赖推进。L1(L0三级分工)→L2(索引+docs)→L3(Hook分级+MANIFEST动态化)→L4(Scripts去重+R16验证)。每层独立验证，全部为非破坏性结构优化。

**Tech Stack:** Python 3 (hooks), PowerShell (sync), YAML (MANIFEST), Markdown (config docs)

---

## 文件结构

```
~/.claude/
├── CLAUDE-ROUTER.mdc       # [修改] L1 - 纯路由入口 ~50行
├── CLAUDE.md               # [修改] L1 - 用户查阅层 ~180行
├── rules/CORE.md           # [修改] L1 - 机器执行层 ~220行
├── SPEC.md                 # [修改] L1 - 版本号对齐 v10.2
├── skills-INDEX.md         # [新建] L2 - skills索引
├── agents-INDEX.md         # [新建] L2 - agents索引
├── rules-INDEX.md          # [新建] L2 - rules索引
├── docs/research/README.md # [修改] L2 - 指向当前SSOT
├── skills/deep-research/SKILL.md  # [修改] L2 - L1→L2→L3升级标准
├── mcp-configs/optional-dev.json  # [修改] L2 - 添加Exa条目
├── settings.json           # [修改] L3 - hook分级profile字段
├── hooks/_editor_hook_launcher.py      # [修改] L3 - profile过滤
├── hooks/pre-manifest-validator.py     # [修改] L3 - 动态excludes
├── hooks/stop-context-monitor.py       # [修改] L3 - 合并pre-suggest-compact
├── hooks/pre-bash-guard.py             # [修改] L3 - 合并循环检测
├── MANIFEST.yaml           # [可能修改] L3 - excludes补全
├── scripts/validate_config.py          # [修改] L4 - 合并+V17
├── scripts/_validate_config.py         # [删除] L4 - 合并后移除
├── scripts/check.ps1                   # [修改] L4 - 职责注释
├── scripts/accept-v10_1.py             # [移动] L4 → archive/
└── archive/accept-v10_1.py             # [新建] L4 - 归档
```

---

### Task 1: 重写 CLAUDE-ROUTER.mdc — 纯路由入口

**Files:**
- Modify: `C:\Users\DELL\.claude\CLAUDE-ROUTER.mdc`

- [ ] **Step 1: 备份当前内容**

```powershell
Copy-Item C:\Users\DELL\.claude\CLAUDE-ROUTER.mdc C:\Users\DELL\.claude\_backup_CLAUDE-ROUTER.mdc
```

- [ ] **Step 2: 写入精简版 (~50行)**

用 Edit 工具替换 CLAUDE-ROUTER.mdc 全文为：

```markdown
---
description: Claude 配置总纲路由 — Tool-First 入口（全编辑器必加载）
alwaysApply: true
layer: router
---

## 总纲链（Tool-First Read，禁止凭记忆执行）

1. **路由入口** — 编辑器目录 `CLAUDE.md`（软链 → `~/.claude/CLAUDE.md`）
2. **归属矩阵** — `MANIFEST.yaml`
3. **发现索引** — `skills-INDEX.md` | `agents-INDEX.md` | `rules-INDEX.md`
4. **法典** — `SPEC.md`
5. **按需加载**（任务触发后再 Read，禁止全量扫描）：
   - 技能：`skills/<name>/SKILL.md`
   - Agent：`agents/<name>.md`
   - 规则：`rules/<name>.md`

## P0 路由集（5）= L1×2 + L2 门控×3

| Skill | 等级 | 触发 |
|-------|------|------|
| using-superpowers | L1 | 会话开始、分类路由 |
| change-impact-analysis | L1 | 任何修改意图 |
| brainstorming | L2 | 非简单 ①规划（HARD-GATE） |
| verification-before-completion | L2 | ④验收 |
| systematic-debugging | L2 | Bug/调试 |

## 加载等级 L0–L3

| 等级 | 内容 | 机制 |
|------|------|------|
| L0 | 本文件 + CLAUDE.md + rules/CORE.md | alwaysApply (~2K tokens) |
| L1 | using-superpowers（会话常驻）, change-impact-analysis（改前必读） |
| L2 | brainstorming / writing-plans / executing-plans / verification / debugging | 阶段触发 Read 全文 |
| L3 | 所有其他 skills/rules/agents/MCP/Firecrawl/Exa | description 触发词 + slash 路由，按需 Read |

**探索优先级（R17）**：`codegraph_explore` 先于 Grep/Read — 详见 `CORE.md` R17-R18 章节。
```

- [ ] **Step 3: 验证文件无语法错误**

```powershell
# 检查 frontmatter 完整性
Select-String -Path C:\Users\DELL\.claude\CLAUDE-ROUTER.mdc -Pattern '^---' | Measure-Object | ForEach-Object {
    if ($_.Count -ne 2) { Write-Error "frontmatter 不完整" }
}
```

---

### Task 2: 重写 CLAUDE.md — 用户快速查阅层

**Files:**
- Modify: `C:\Users\DELL\.claude\CLAUDE.md`

- [ ] **Step 1: 备份当前内容**

```powershell
Copy-Item C:\Users\DELL\.claude\CLAUDE.md C:\Users\DELL\.claude\_backup_CLAUDE.md
```

- [ ] **Step 2: 写入精简版 (~180行)**

核心变更：
1. 删除"加载等级 L0–L3"章节（SSOT 已移至 ROUTER）
2. 删除"三横切基础设施"章节（SSOT 在 CORE）
3. 删除 R17-R18 详细说明（SSOT 在 CORE），保留一条引用
4. 铁律表合并为一行：`#1-11 核心约束 → 本表；#12-19 详情 → rules/CORE.md`
5. "上下文腐烂三级阈值"改为一行引用 `→ rules/CORE.md`
6. 保留：优先级链、五柱、五阶段、命令速查、审查路由、指针

保留结构：
```
优先级链 → 五柱×五阶段×三横切（概要） → 铁律 R1-R18（编号+核心词）
→ 五阶段流程（SSOT） → Tool-First 路由 → 审查路由 → 命令速查 → 指针
```

- [ ] **Step 3: 验证行数**

```powershell
(Get-Content C:\Users\DELL\.claude\CLAUDE.md | Measure-Object -Line).Lines
# 预期: ≤200
```

---

### Task 3: 重写 rules/CORE.md — 机器执行层

**Files:**
- Modify: `C:\Users\DELL\.claude\rules\CORE.md`

- [ ] **Step 1: 备份**

```powershell
Copy-Item C:\Users\DELL\.claude\rules\CORE.md C:\Users\DELL\.claude\_backup_CORE.md
```

- [ ] **Step 2: 重构 CORE.md (~220行)**

变更：
1. 删除"五阶段流程"详细描述（SSOT 已移至 CLAUDE.md），仅保留状态机+门控
2. 删除"P0路由集"（SSOT 在 ROUTER），改为引用
3. 删除"加载等级"详细（SSOT 在 ROUTER），保留一句话引用
4. **保留（SSOT）**：三横切基础设施、上下文阈值、编码规范、铁律R12-R19全文、R17-R18工具路由、变更彻底性三阶段、错误升级路径
5. 新增 R16 详细声明末尾加一条："所有 Python 脚本裸 except 必须为 0"
6. 在开头加注释标记哪些是 SSOT 块

```markdown
---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义
---

# CORE — 机器执行层骨架

> P0路由集 → `CLAUDE-ROUTER.mdc` | 五阶段详细 → `CLAUDE.md` | 加载等级 → `CLAUDE-ROUTER.mdc`
```

- [ ] **Step 3: 验证**

```powershell
(Get-Content C:\Users\DELL\.claude\rules\CORE.md | Measure-Object -Line).Lines
# 预期: ≤250
```

---

### Task 4: 更新 SPEC.md — 版本对齐

**Files:**
- Modify: `C:\Users\DELL\.claude\SPEC.md`

- [ ] **Step 1: 版本号对齐**

用 Edit 替换：
- `版本：10.1` → `版本：10.2`
- `CLAUDE.md ≤250` → `CLAUDE.md ≤200`
- 在规模约束表新增一行：`| Exa MCP | 按需 | mcp-configs/optional-dev.json，L3 调研时 merge |`

---

### Task 5: 验证 sync.ps1 L0 入口模式

**Files:**
- No changes needed

- [ ] **Step 1: Dry-run 验证**

```powershell
cd C:\Users\DELL\.claude
powershell -ExecutionPolicy Bypass -File scripts\sync.ps1 -DryRun
# 预期: 每个编辑器显示 "Would symlink: CLAUDE.md", "Would symlink: rules/CORE.mdc" 等
# 预期: Synced 计数 = 5 editors × (1 CLAUDE.md + 2 rules) = 15
```

---

### Task 6: 生成 skills-INDEX.md

**Files:**
- Create: `C:\Users\DELL\.claude\skills-INDEX.md`

- [ ] **Step 1: 扫描 skills/ 目录并生成索引**

```powershell
Get-ChildItem C:\Users\DELL\.claude\skills -Recurse -Filter SKILL.md |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $desc = if ($content -match 'description:\s*(.+)') { $matches[1] } else { "(无描述)" }
        $relPath = $_.FullName.Replace("$env:USERPROFILE\.claude\", "")
        "- [$($_.Directory.BaseName)]($relPath) — $desc"
    } | Sort-Object
```

- [ ] **Step 2: 写入索引文件**

按 L1/L2/L3 手动分级排列（从 MANIFEST loading_tiers 获取分级信息）

---

### Task 7: 生成 agents-INDEX.md

**Files:**
- Create: `C:\Users\DELL\.claude\agents-INDEX.md`

- [ ] **Step 1: 扫描 agents/ 目录并生成索引**

```powershell
Get-ChildItem C:\Users\DELL\.claude\agents -Filter *.md |
    Where-Object { $_.Name -ne 'README.md' } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $desc = if ($content -match 'description:\s*(.+)') { $matches[1] } else { "(无描述)" }
        "- [$($_.BaseName)]($($_.Name)) — $desc"
    } | Sort-Object
```

- [ ] **Step 2: 按分组排列**（核心7 / gstack审查6 / gstack补全 / gstack v0.19）

---

### Task 8: 生成 rules-INDEX.md

**Files:**
- Create: `C:\Users\DELL\.claude\rules-INDEX.md`

- [ ] **Step 1: 扫描 rules/ 目录并生成索引**

```powershell
Get-ChildItem C:\Users\DELL\.claude\rules -Filter *.md |
    Where-Object { $_.Name -notin @('README.md','INDEX.md') } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $trigger = if ($content -match 'trigger:\s*(.+)') { $matches[1] } else { "lazy" }
        $always = if ($content -match 'alwaysApply:\s*true') { "✅ alwaysApply" } else { "📎 $trigger" }
        "- [$($_.BaseName)]($($_.Name)) — $always"
    } | Sort-Object
```

---

### Task 9: 更新 ROUTER 引用新索引

**Files:**
- Modify: `C:\Users\DELL\.claude\CLAUDE-ROUTER.mdc`

- [ ] **Step 1: 确认引用完整性**

总纲链第3条已包含 `skills-INDEX.md | agents-INDEX.md | rules-INDEX.md`，确认一致即可。

---

### Task 10: 更新 docs/research/README.md

**Files:**
- Modify: `C:\Users\DELL\.claude\docs\research\README.md`

- [ ] **Step 1: 添加 SSOT 指向说明**

在文件头部添加：
```markdown
> **当前 SSOT**: `30-repo-deep-research-v10.md` — v10 全量仓库深度调研
> **archive/**: v7-v9 历史调研版本，仅供参考
```

---

### Task 11: 添加 Exa 到 mcp-configs/optional-dev.json

**Files:**
- Modify: `C:\Users\DELL\.claude\mcp-configs\optional-dev.json`

- [ ] **Step 1: 添加 Exa 条目**

```json
{
  "exa": {
    "_description": "Exa 语义搜索 — L3 深度调研时按需 merge。触发：/deep-research、多源交叉验证（与 Firecrawl 互补）",
    "command": "npx",
    "args": ["-y", "@anthropic/exa-mcp-server"],
    "env": {
      "EXA_API_KEY": "${EXA_API_KEY}"
    }
  }
}
```

---

### Task 12: 更新 deep-research SKILL.md — L1→L2→L3升级标准

**Files:**
- Modify: `C:\Users\DELL\.claude\skills\deep-research\SKILL.md`

- [ ] **Step 1: 在文件头部添加升级决策表**

```markdown
## 升级决策（L1→L2→L3）

| 档 | 场景 | 工具 | 触发条件 |
|----|------|------|---------|
| L1 | 单点事实/API | Context7 / Exa 单次 | 需要确认一个具体参数/签名/版本 |
| L2 | 方案对比/最佳实践 | Exa + Firecrawl 单页 | 需要对比 ≥2 个方案或需要最新最佳实践 |
| L3 | 深度选型/完整调研 | Firecrawl + Exa + Context7 三源 + V1-V5 交叉验证 | 影响架构决策、技术选型、或需要多角度验证 |

升级信号：L1不足（答案矛盾/过时/不完整）→L2→仍不足→L3
```

---

### Task 13: 合并 pre-suggest-compact → stop-context-monitor

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\stop-context-monitor.py`
- Delete: `C:\Users\DELL\.claude\hooks\pre-suggest-compact.py`

- [ ] **Step 1: 读取两个文件，确认合并点**

`pre-suggest-compact.py` 功能：在上下文接近阈值时注入提醒消息
`stop-context-monitor.py` 功能：在任务停止时评估上下文使用率

合并逻辑：stop-context-monitor 在 Stop 事件中已经能获取上下文使用率，将 pre-suggest-compact 的提醒阈值逻辑作为其附加检查（到达70%时输出建议消息，到达90%时输出强制消息）

- [ ] **Step 2: 在 stop-context-monitor.py 中添加阈值提醒逻辑**

在 stop-context-monitor 的现有逻辑后添加：
```python
# 阈值提醒（原 pre-suggest-compact 逻辑）
USAGE = ctx.get("usage_ratio", 0)
if USAGE >= 0.90:
    print(json.dumps({
        "continue": True,
        "warning": "上下文使用率 ≥90% — 建议立即 /compact 或新子Agent",
        "severity": "critical"
    }))
elif USAGE >= 0.70:
    print(json.dumps({
        "continue": True,
        "warning": "上下文使用率 ≥70% — 择机 /compact",
        "severity": "warning"
    }))
```

- [ ] **Step 3: 删除 pre-suggest-compact.py**

```powershell
Remove-Item C:\Users\DELL\.claude\hooks\pre-suggest-compact.py
```

- [ ] **Step 4: 从 settings.json 中移除 pre-suggest-compact 的 hook 注册**

在 settings.json 中找到并删除引用 `pre-suggest-compact` 的 hook group。

---

### Task 14: 合并 pre-loop-guard 循环检测 → pre-bash-guard

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\pre-bash-guard.py`
- Delete: `C:\Users\DELL\.claude\hooks\pre-loop-guard.py`

- [ ] **Step 1: 读取 pre-loop-guard.py，提取循环检测逻辑**

确认 pre-loop-guard 的核心功能：检测连续重复的命令调用模式（循环保护）

- [ ] **Step 2: 在 pre-bash-guard.py 添加循环检测**

在 pre-bash-guard 的 bash 命令检查前添加：
```python
# 循环检测（原 pre-loop-guard 逻辑）
# 检查最近 N 条历史中的重复命令模式
RECENT_HISTORY = data.get("recent_commands", [])
LOOP_THRESHOLD = 3  # 同一命令连续出现 ≥3 次触发

if len(RECENT_HISTORY) >= LOOP_THRESHOLD:
    last_cmd = RECENT_HISTORY[-1]
    if all(cmd == last_cmd for cmd in RECENT_HISTORY[-LOOP_THRESHOLD:]):
        print(json.dumps({
            "continue": False,
            "reason": f"[LOOP-GUARD] 命令 '{last_cmd[:80]}' 已连续执行 {LOOP_THRESHOLD} 次，疑似无限循环。请确认是否继续。"
        }))
        sys.exit(2)
```

- [ ] **Step 3: 删除 pre-loop-guard.py**

```powershell
Remove-Item C:\Users\DELL\.claude\hooks\pre-loop-guard.py
```

- [ ] **Step 4: 从 settings.json 中移除 pre-loop-guard hook 注册**

---

### Task 15: 添加 profile 字段到 settings.json hook 组

**Files:**
- Modify: `C:\Users\DELL\.claude\settings.json`

- [ ] **Step 1: 为每个 hook group 添加 `"profile"` 字段**

按以下映射添加 `"profile"` 字段到每个 hook group：

```json
{
  "pre-bash-guard":          ["minimal", "standard", "strict"],
  "post-secret-detector":    ["minimal", "standard", "strict"],
  "post-edit-format":        ["minimal", "standard", "strict"],
  "stop-quality-gate":       ["minimal", "standard", "strict"],
  "pre-manifest-validator":  ["standard", "strict"],
  "pre-context-injector":    ["standard", "strict"],
  "pre-read-before-edit":    ["standard", "strict"],
  "pre-compact-state":       ["standard", "strict"],
  "stop-context-monitor":    ["standard", "strict"],
  "pre-rtk-rewrite":         ["standard", "strict"],
  "pre-config-protection":   ["strict"],
  "stop-pattern-extraction": ["strict"],
  "pre-tmux-reminder":       ["strict"],
  "post-codegraph-sync":     ["strict"]
}
```

- [ ] **Step 2: 验证 JSON 格式**

```powershell
python -c "import json; json.load(open(r'C:\Users\DELL\.claude\settings.json')); print('JSON valid')"
# 预期: JSON valid
```

---

### Task 16: 更新 _editor_hook_launcher.py — profile 过滤

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\_editor_hook_launcher.py`

- [ ] **Step 1: 添加 profile 过滤逻辑**

在 launcher 的 hook 调度循环前添加：

```python
import os

def get_active_profile():
    """读取 LOCAL_HOOK_PROFILE 环境变量，默认 standard"""
    return os.environ.get("LOCAL_HOOK_PROFILE", "standard")

def hook_matches_profile(hook_config, active_profile):
    """检查 hook 是否应在当前 profile 下激活"""
    profiles = hook_config.get("profile", ["minimal", "standard", "strict"])
    profile_order = {"minimal": 0, "standard": 1, "strict": 2}
    return profile_order.get(active_profile, 1) >= min(
        profile_order.get(p, 1) for p in profiles
    )
```

- [ ] **Step 2: 在调度循环中应用过滤**

在决定执行某个 hook 前调用 `hook_matches_profile()`，不匹配则跳过。

---

### Task 17: 重写 pre-manifest-validator.py — 动态 excludes

**Files:**
- Modify: `C:\Users\DELL\.claude\hooks\pre-manifest-validator.py`

- [ ] **Step 1: 补全 TOOL_INTENT_MAP 覆盖率到 63**

新增映射条目覆盖全部 38 skills + 25 agents（当前 ~30 条 → 63 条）。完整列表：

```python
TOOL_INTENT_MAP: dict[str, str] = {
    # P0 路由集 (5)
    "skill/using-superpowers": "bootstrap",
    "skill/change-impact-analysis": "change_impact",
    "skill/brainstorming": "brainstorming",
    "skill/verification-before-completion": "verification",
    "skill/systematic-debugging": "debugging",
    # L2 门控 (8)
    "skill/writing-plans": "planning",
    "skill/spec-validation": "spec_review",
    "skill/executing-plans": "execution",
    "skill/subagent-driven-development": "multi_agent",
    "skill/test-driven-development": "tdd",
    "skill/requesting-code-review": "code_review_request",
    "skill/receiving-code-review": "code_review_receive",
    "skill/triage": "triage",
    # L3 信号 (10)
    "skill/deep-research": "deep_research",
    "skill/adr-management": "adr",
    "skill/workstream-management": "workstreams",
    "skill/claude-to-deerflow": "deer_flow_bridge",
    "skill/git-workflow": "git_workflow",
    "skill/pr-workflow": "pr_workflow",
    "skill/claude-mem-maintenance": "claude_mem_maintenance",
    "skill/autoplan": "autoplan",
    "skill/ship": "ship_pipeline",
    "skill/office-hours": "office_hours",
    # Supplement (15)
    "skill/understand-anything": "concept_navigation",
    "skill/context-engineering": "context_engineering",
    "skill/memory-compression": "context_rot",
    "skill/caveman-compress": "output_token",
    "skill/instinct-learning": "instinct_v2",
    "skill/improve-codebase-architecture": "architecture_improvement",
    "skill/design-pipeline": "design_pipeline",
    "skill/taste-memory": "taste_memory",
    "skill/browser-qa": "gstack_qa",
    "skill/onboarding-guide": "onboarding",
    "skill/karpathy-guidelines": "coding_philosophy",
    "skill/finishing-a-development-branch": "ship_pipeline",
    "skill/using-git-worktrees": "workstreams",
    "skill/writing-skills": "planning",
    "skill/structured-artifacts": "gsd_context",
    # Agents — 核心7
    "agent/planner": "planning",
    "agent/code-explorer": "code_exploration",
    "agent/code-reviewer": "code_review_receive",
    "agent/build-error-resolver": "debugging",
    "agent/architect": "brainstorming",
    "agent/spec-reviewer": "spec_review",
    "agent/agentic-orchestrator": "multi_agent",
    # Agents — gstack 审查
    "agent/eng-reviewer": "gstack_eng",
    "agent/ceo-reviewer": "gstack_ceo",
    "agent/designer": "gstack_designer",
    "agent/dx-reviewer": "gstack_dx",
    "agent/qa": "gstack_qa",
    "agent/security-reviewer": "gstack_security",
    # Agents — gstack 补全
    "agent/cso": "gstack_cso",
    "agent/sre": "gstack_sre",
    "agent/release-engineer": "land_and_deploy",
    "agent/product-manager": "office_hours",
    "agent/design-engineer": "gstack_designer",
    "agent/performance-engineer": "gstack_eng",
    "agent/doc-writer": "gstack_eng",
    # Agents — gstack v0.19
    "agent/design-shotgun": "design_pipeline",
    "agent/pair-agent": "agentic_orchestrator",
    "agent/land-and-deploy": "land_and_deploy",
    "agent/ios-specialist": "gstack_ios",
    "agent/codex-reviewer": "gstack_codex",
    # MCP
    "mcp/codegraph": "code_exploration",
}
```

- [ ] **Step 2: 删除硬编码 EXCLUDES 表，改为动态读取**

```python
# 删除原有的 EXCLUDES 硬编码字典
# 新增动态加载函数：

import yaml

EXCLUDES_CACHE = None
MANIFEST_MTIME = 0

def load_excludes_from_manifest():
    """动态读取 MANIFEST.yaml 的 concerns.*.excludes"""
    global EXCLUDES_CACHE, MANIFEST_MTIME
    mtime = os.path.getmtime(str(MANIFEST_PATH))
    if EXCLUDES_CACHE is not None and mtime == MANIFEST_MTIME:
        return EXCLUDES_CACHE
    
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    
    excludes = {}
    for name, concern in manifest.get("concerns", {}).items():
        if isinstance(concern, dict) and "excludes" in concern:
            excludes[name] = set(concern["excludes"])
    
    EXCLUDES_CACHE = excludes
    MANIFEST_MTIME = mtime
    return excludes
```

- [ ] **Step 3: 更新 main() 使用动态加载**

```python
def main() -> None:
    data = load_stdin()
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    concern = resolve_concern(tool_name, tool_input)
    if concern is None:
        sys.exit(0)

    current_entity = (
        f"agent/{tool_input.get('subagent_type')}"
        if tool_name == "Agent"
        else f"skill/{tool_input.get('skill', '')}"
    )

    # 动态读取 excludes
    excludes = load_excludes_from_manifest()
    blocked = excludes.get(concern, set())
    
    if current_entity in blocked:
        print(json.dumps({
            "continue": False,
            "reason": (
                f"[MANIFEST] {current_entity} 与 {concern} 互博。"
                f"MANIFEST excludes: {blocked}. 请使用 MANIFEST.yaml 指定的 owner。"
            ),
        }))
        sys.exit(2)
    
    sys.exit(0)
```

---

### Task 18: 验证 MANIFEST.yaml excludes 一致性

**Files:**
- Verify: `C:\Users\DELL\.claude\MANIFEST.yaml` (no edits unless gaps found)

- [ ] **Step 1: 交叉验证 TOOL_INTENT_MAP 覆盖**

```powershell
python -c "
import yaml, json
m = yaml.safe_load(open(r'C:\Users\DELL\.claude\MANIFEST.yaml', encoding='utf-8'))
concerns = [k for k, v in m.get('concerns', {}).items() if isinstance(v, dict) and 'excludes' in v]
print(f'有 excludes 的 concern: {len(concerns)}')
for c in sorted(concerns):
    print(f'  {c}: {m[\"concerns\"][c][\"excludes\"]}')
"
```

- [ ] **Step 2: 确认每个 concern→excludes 的意图正确**

检查已知冲突对是否都有合理的 `excludes` 声明。

---

### Task 19: 合并 _validate_config.py → validate_config.py

**Files:**
- Read: `C:\Users\DELL\.claude\scripts\_validate_config.py`
- Modify: `C:\Users\DELL\.claude\scripts\validate_config.py`
- Delete: `C:\Users\DELL\.claude\scripts\_validate_config.py`

- [ ] **Step 1: 对比两个文件，识别 _validate_config 中的独有逻辑**

```powershell
# 识别两文件的差异
$main = Get-Content C:\Users\DELL\.claude\scripts\validate_config.py
$alt = Get-Content C:\Users\DELL\.claude\scripts\_validate_config.py
# 找出 _validate_config 中 validate_config 没有的检查项
```

- [ ] **Step 2: 将独有逻辑合并到 validate_config.py**

在 validate_config.py 末尾（V16 之后）追加新的验证项。

- [ ] **Step 3: 删除 _validate_config.py**

```powershell
Remove-Item C:\Users\DELL\.claude\scripts\_validate_config.py
```

- [ ] **Step 4: 检查其他脚本是否有对 _validate_config 的引用**

```powershell
Select-String -Path C:\Users\DELL\.claude\* -Pattern '_validate_config' -Recurse
# 预期：无引用（或全部更新为 validate_config）
```

---

### Task 20: 添加 V17 裸 except 扫描到 validate_config.py

**Files:**
- Modify: `C:\Users\DELL\.claude\scripts\validate_config.py`

- [ ] **Step 1: 添加 V17 检测函数**

```python
def check_v17_bare_except():
    """V17: R16 合规 — 裸 except 扫描（hooks/ + scripts/）
    
    要求: 所有 .py 文件中不允许裸 `except:` 或 `except Exception:` 
          异常必须传播或显式处理并报告。
    """
    violations = []
    scan_dirs = [
        BASE / "hooks",
        BASE / "scripts",
    ]
    # 匹配裸 except 但排除合法的：
    #   except ... as e:  (有变量绑定)
    #   except (X, Y):    (指定了异常类型)
    #   # noqa: R16       (显式豁免)
    bare_pattern = re.compile(r'^\s*except\s*:')
    broad_pattern = re.compile(r'^\s*except\s+Exception\s*:')
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if bare_pattern.match(line):
                    # 检查下一行是否包含 noqa 豁免
                    if i < len(lines) and 'noqa: R16' not in lines[i]:
                        violations.append(f"{py_file.relative_to(BASE)}:{i}: bare 'except:'")
                elif broad_pattern.match(line):
                    if i < len(lines) and 'noqa: R16' not in lines[i]:
                        violations.append(f"{py_file.relative_to(BASE)}:{i}: bare 'except Exception:'")
    
    if violations:
        print(f"  V17 R16 裸 except: FAIL ({len(violations)} violations)")
        for v in violations:
            print(f"    - {v}")
        return False
    else:
        print("  V17 R16 裸 except: PASS")
        return True
```

- [ ] **Step 2: 在主流程中调用 V17**

在 `main()` 函数的验证链末尾添加：
```python
results.append(("V17 R16 裸 except", check_v17_bare_except()))
```

---

### Task 21: 归档 accept-v10_1.py

**Files:**
- Move: `C:\Users\DELL\.claude\scripts\accept-v10_1.py` → `C:\Users\DELL\.claude\archive\accept-v10_1.py`

- [ ] **Step 1: 移动文件**

```powershell
Move-Item C:\Users\DELL\.claude\scripts\accept-v10_1.py C:\Users\DELL\.claude\archive\accept-v10_1.py
```

- [ ] **Step 2: 确保 archive/ 目录有 README 说明**

如果 `archive/README.md` 不存在，创建简要说明：
```markdown
# Archive — 历史脚本与验收文件
> 不再活跃使用的脚本，保留供参考
```

---

### Task 22: 添加 check.ps1 职责注释

**Files:**
- Modify: `C:\Users\DELL\.claude\scripts\check.ps1`

- [ ] **Step 1: 在文件头部添加职责注释**

在 param 块前添加：
```powershell
<#
.SYNOPSIS
    快速诊断（<5 秒）— 检查关键文件和目录存在性
.DESCRIPTION
    轻量级健康检查，仅验证文件/目录存在、基本格式。
    深度校验（冲突检测、R16扫描、完整验证）→ scripts/validate_config.py。
    设计原则：check.ps1 = 快速诊断；validate_config.py = 深度校验。
#>
```

---

### Task 23: R16 全量扫描 + 修复

**Files:**
- Scan: `C:\Users\DELL\.claude\hooks\*.py`, `C:\Users\DELL\.claude\scripts\*.py`
- Fix: 如有违规

- [ ] **Step 1: 运行扫描**

```powershell
python -c "
import re
from pathlib import Path
BASE = Path(r'C:\Users\DELL\.claude')
violations = []
for d in ['hooks', 'scripts']:
    for f in (BASE / d).rglob('*.py'):
        content = f.read_text(encoding='utf-8')
        for i, line in enumerate(content.split('\n'), 1):
            if re.match(r'^\s*except\s*:', line):
                violations.append(f'{f.name}:{i}')
            elif re.match(r'^\s*except\s+Exception\s*:', line):
                violations.append(f'{f.name}:{i} (broad)')
if violations:
    print(f'FAIL: {len(violations)} violations')
    for v in violations: print(f'  {v}')
else:
    print('PASS: 0 bare except')
"
# 预期: PASS
```

- [ ] **Step 2: 逐项修复**

对每个违规：
1. 确认异常类型 → 替换为具体异常
2. 添加错误处理和日志

- [ ] **Step 3: 重新扫描确认 0**

---

### Task 24: 全量验证

- [ ] **Step 1: 运行 validate_config.py**

```powershell
cd C:\Users\DELL\.claude
python scripts/validate_config.py
# 预期: 全部 PASS（包括 V17）
```

- [ ] **Step 2: 运行 sync.ps1 干燥跑**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync.ps1 -All -DryRun
# 预期: 无错误，所有目标正确列出
```

- [ ] **Step 3: 运行 check.ps1**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check.ps1
# 预期: 无严重错误
```

- [ ] **Step 4: MANIFEST 一致性检查**

```powershell
python -c "
import yaml
m = yaml.safe_load(open(r'C:\Users\DELL\.claude\MANIFEST.yaml', encoding='utf-8'))
# 检查版本
assert m['version'] == '10.2', f'版本号不对: {m[\"version\"]}'
print(f'MANIFEST version: {m[\"version\"]} - OK')

# 检查所有 concern owner 引用的文件存在性
from pathlib import Path
BASE = Path(r'C:\Users\DELL\.claude')
missing = []
for name, c in m.get('concerns', {}).items():
    if isinstance(c, dict) and 'owner' in c:
        owner = c['owner']
        if '/' in owner and not '.' in owner.split('/')[-1]:
            # skip abstract references
            continue
        # check if referenced file exists in .claude/
        parts = owner.split('/')
        if len(parts) > 1:
            candidate = BASE / owner
            if not candidate.exists():
                missing.append(f'{name}: {owner}')
if missing:
    print(f'Missing owner references: {len(missing)}')
    for mref in missing: print(f'  {mref}')
else:
    print('All concern owners reference existing files - OK')
"
```

- [ ] **Step 5: 提交**

```powershell
git add -A
git commit -m @"
chore: 配置工程优化 v10.2

Layer 1: L0入口三级分工 (CLAUDE-ROUTER/CLAUDE/CORE 去重 ~25% token节省)
Layer 2: 索引生成 + 文档同步 (skills/agents/rules INDEX + Exa配置 + deep-research升级标准)
Layer 3: Hook分级实现 + MANIFEST动态化 (LOCAL_HOOK_PROFILE + excludes动态解析)
Layer 4: Scripts去重 + R16验证 (validate_config合并 + V17裸except扫描)

CC: 10项要求全覆盖
"@
```
