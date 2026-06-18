# 配置工程优化 — 设计文档

> 日期：2026-06-18 | 版本：v10.2 | 状态：设计完成，待实施

## 动机

当前 `.claude/` 配置体系经过 v7→v10 多轮迭代，积累了以下问题：

1. **L0 入口重复**：CLAUDE.md(600行) / ROUTER.mdc(37行) / CORE.md(250行) 三文件 ~6K tokens，估算 ~1.5K 为重复内容（优先级链、加载等级、P0路由集、R17探索规则在多处出现）
2. **SPEC.md 版本漂移**：自称 v10.1，MANIFEST v10.2
3. **索引文件缺失**：ROUTER 引用 skills-INDEX.md / agents-INDEX.md / rules-INDEX.md 但不存在
4. **Hook 分级未实现**：MANIFEST 声明 `LOCAL_HOOK_PROFILE` 三档但 settings.json 全量加载，重叠 hook 未合并
5. **MANIFEST 硬编码**：pre-manifest-validator TOOL_INTENT_MAP 未全覆盖，excludes 表硬编码在 hook 中
6. **Scripts 重复/历史遗留**：validate_config.py 与 _validate_config.py 并存，v10.1 验收脚本未归档
7. **R16 合规未验证**：裸 except 扫描缺自动化
8. **调研管线缺失决策标准**：L1→L2→L3 升级条件模糊，Exa 未配置

## 目标

满足10项要求，在不破坏现有功能的前提下：
- 消除 L0 三文件重复 → ~25% token 节省
- 补全缺失索引 → ROUTER 引用完整
- 实现三级 hook 分级 → 按场景加载
- MANIFEST 动态化 → 冲突对自动生效
- 文档/配置版本一致性 → 无漂移

## 四层架构

```
Layer 1: L0 入口去重（CLAUDE.md / ROUTER.mdc / CORE.md / SPEC.md）
Layer 2: 索引生成 + 文档同步（INDEX文件 + docs + Exa 配置）
Layer 3: Hook 分级 + MANIFEST 动态化（pre-manifest-validator 改造）
Layer 4: Scripts 去重 + R16 验证（validate_config 合并 + 归档）
```

依赖关系：Layer 1 → 2 → 3 → 4（逐层依赖，不可并行）

---

## Layer 1: L0 入口三级分工

### 原则

SSOT（Single Source of Truth）：每条规则只在一处定义，其余文件只引用不重复。

### 三级分工

```
CLAUDE-ROUTER.mdc  (~50行)   纯路由入口
  ├── 总纲链（指向 CLAUDE.md → MANIFEST → SPEC.md → INDEX文件）
  ├── P0路由集(5)  ← SSOT
  ├── 加载等级 L0-L3  ← SSOT
  ├── 探索优先级（引用 CORE R17）
  └── 同步模式说明

CLAUDE.md  (~180行)   用户快速查阅层
  ├── 优先级链 + 五柱声明
  ├── 五阶段流程 + 状态机  ← SSOT
  ├── 命令速查 + 审查路由
  ├── 铁律摘要（编号+核心词，全文 → CORE）
  └── 指针（文件位置 + 插件/同步）

CORE.md  (~220行)   机器执行层（alwaysApply）
  ├── 三横切基础设施  ← SSOT
  ├── 上下文腐烂三级阈值  ← SSOT
  ├── 编码规范 + 注释模板
  ├── 铁律 R12-R19 全文  ← SSOT
  ├── R17-R18 工具路由与协同  ← SSOT
  ├── 变更彻底性保障（三阶段流程）  ← SSOT
  ├── 错误升级路径  ← SSOT
  └── 快速指令前缀 + 工作原则
```

### SSOT 分配表

| 内容 | SSOT 位置 | 其他文件 |
|------|----------|---------|
| P0路由集 | ROUTER.mdc | CLAUDE.md 一句话引用 |
| 加载等级 L0-L3 | ROUTER.mdc | 删除 CLAUDE.md 中的重复 |
| 五阶段流程 + 状态机 | CLAUDE.md | CORE.md 仅保留状态机简述 |
| 五柱声明 + 命令速查 | CLAUDE.md | — |
| 铁律 R1-R18 摘要 | CLAUDE.md（编号+核心词） | R12-R19 全文在 CORE.md |
| 三横切 | CORE.md | 删除 CLAUDE.md 重复 |
| R17 探索优先级 | CORE.md | ROUTER 一句话引用 |
| 上下文阈值 | CORE.md | CLAUDE.md 一句话引用 |
| 编码规范/注释模板 | CORE.md | — |
| 变更彻底性 | CORE.md | — |
| 错误升级路径 | CORE.md | — |

### SPEC.md 变更

- 版本号 v10.1 → v10.2
- 规模约束表更新（skills 38→38, agents 25→25，不变）
- CLAUDE.md 行数描述 250→180

---

## Layer 2: 索引生成 + 文档同步

### 新建文件

**skills-INDEX.md**：从 `skills/` 目录自动扫描，按 L1/L2/L3 分级输出
```markdown
# Skills 索引
## L1 (会话常驻)
- [using-superpowers](using-superpowers/SKILL.md) — 技能发现与 Tool-First 路由
- [change-impact-analysis](change-impact-analysis/SKILL.md) — 变更影响分析
## L2 (阶段门控)
- [brainstorming](brainstorming/SKILL.md) — HARD-GATE 设计方案
...
```

**agents-INDEX.md**：从 `agents/` 目录自动扫描
```markdown
# Agents 索引
## 核心 7
- [agentic-orchestrator](agentic-orchestrator.md) — 多 Agent 并行编排
...
## gstack 审查 6
...
```

**rules-INDEX.md**：从 `rules/` 目录自动扫描，标注加载方式
```markdown
# Rules 索引
## alwaysApply (skeleton)
- [CORE.md](CORE.md) — 编码规范 + 铁律 + 阈值
## lazy (supplement)
- [BESTPRACTICE.md](BESTPRACTICE.md) — 提示词设计 + API 设计 + 日志
...
```

### 编辑文件

| 文件 | 变更 |
|------|------|
| CLAUDE-ROUTER.mdc | 总纲链索引文件名补全为 skills-INDEX.md / agents-INDEX.md / rules-INDEX.md |
| SPEC.md | 版本号 v10.2，更新 CLAUDE.md 行数，补充 Exa 配置说明 |
| docs/research/README.md | 指向当前 SSOT（30-repo-deep-research-v10.md），说明 archive/ 为历史版本 |
| .mcp.json | Exa 按需加入 mcp-configs/optional-dev.json（不常驻） |
| skills/deep-research/SKILL.md | 明确 L1→L2→L3 升级决策标准 |

### Exa 配置

在 `mcp-configs/optional-dev.json` 中添加 Exa 条目，默认不 merge 到 `.mcp.json`。仅在 `/deep-research` L3 时按需 merge。

---

## Layer 3: Hook 分级 + MANIFEST 动态化

### 3a. Hook 三级分级

通过 `$env:LOCAL_HOOK_PROFILE` 控制 hook 加载子集。

| 档位 | 数量 | 触发条件 | 包含 Hooks |
|------|------|---------|-----------|
| **minimal** | 4 | 简单任务(≤3文件) | pre-bash-guard, post-secret-detector, post-edit-format, stop-quality-gate |
| **standard** | 10 | 默认非简单任务 | + pre-manifest-validator, pre-context-injector, pre-read-before-edit, pre-compact-state, stop-context-monitor, pre-rtk-rewrite |
| **strict** | 14 | 安全敏感/发布 | + pre-config-protection, stop-pattern-extraction, pre-tmux-reminder, post-codegraph-sync |

### 合并优化

| 合并 | 说明 |
|------|------|
| `pre-suggest-compact` → `stop-context-monitor` | 统一管理阈值提醒 + 强制压缩，消除功能重叠 |
| `pre-loop-guard`(循环检测) → `pre-bash-guard` | 命令安全统一入口，循环检测作为子功能 |

净效果：22 hooks → ~19 hooks（-3），minimal 档仅 4 个核心。

### 实现方式

- 不是硬编码分级表在 hook 代码中，而是在 `settings.json` 的每个 hook group 上加 `profile` 字段标记归属
- `_editor_hook_launcher.py` 启动时读取 `$env:LOCAL_HOOK_PROFILE`（默认 standard），跳过不匹配档位的 hook
- 每个 hook 的 `profile` 字段取值为 `["minimal","standard","strict"]` 的子集

### 3b. MANIFEST 动态化

**pre-manifest-validator.py 改造**：

| 部件 | 改造前 | 改造后 |
|------|--------|--------|
| TOOL_INTENT_MAP | ~30 条硬编码 | 补全覆盖 63 个 skills+agents |
| EXCLUDES 表 | 硬编码 12 对 | **删除**——改为动态读取 `MANIFEST.yaml` 的 `concerns.*.excludes` |
| MANIFEST 解析 | 每次调用重读 | 会话内缓存（基于 mtime），只读一次 |

**动态解析逻辑**：
```python
def load_excludes():
    manifest = yaml.safe_load(open(MANIFEST_PATH))
    excludes = {}
    for name, concern in manifest.get('concerns', {}).items():
        if 'excludes' in concern:
            excludes[name] = set(concern['excludes'])
    return excludes
```

**收益**：新增冲突只需改 MANIFEST.yaml 的 excludes 字段，hook 自动生效。消除代码与配置漂移。

---

## Layer 4: Scripts 去重 + R16 验证

### 操作清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `_validate_config.py` | **删除** | 内容合并入 `validate_config.py` |
| `validate_config.py` | 编辑 | 吸收 `_validate_config.py` 有效逻辑，作为唯一验证入口 |
| `accept-v10_1.py` | **移动** | → `archive/accept-v10_1.py` |
| `check.ps1` | 编辑 | 头部加职责注释：快速诊断(<5s)，深度走 validate_config.py |
| 所有 `hooks/*.py` | **R16 扫描** | `grep -rn 'except\s*:'` → 必须为 0 |
| `scripts/*.py` | **R16 扫描** | 同上 |

### R16 合规验证

在 `validate_config.py` 中新增 V17 检测项：
```python
# V17: 裸 except 扫描 — R16 合规
bare_excepts = 0
for py_file in (hooks_dir + scripts_dir):
    if re.search(r'except\s*:', content):
        bare_excepts += 1
assert bare_excepts == 0, f"R16 violation: {bare_excepts} bare except(s)"
```

---

## 10项要求 → 决策 → Layer 映射

| # | 要求 | 决策 | Layer |
|---|------|------|:---:|
| 1 | 保留优点，优化补全文档配置 | L0去重+索引生成+SPEC对齐+scripts去重 | 1,2,4 |
| 2 | 强制加载必要，按需加载其余 | L0三级分工+hook分级 | 1,3 |
| 3 | 软连接同步，去重优化 | sync.ps1 L0入口(方案A) | 已有 |
| 4 | CodeGraph降本增效 | 业务仓库按需init(方案B) | 已有 |
| 5 | 持续迭代，管理上下文 | L0阈值+hook分级 | 1,3 |
| 6 | 深度调研多角度验证 | Exa补配+升级标准+deep-research skill | 2 |
| 7 | 少重复，低耦合高内聚 | L0 SSOT+scripts去重+plugins冲突表 | 1,4 |
| 8 | 杜绝左右手互博 | MANIFEST动态化+plugins冲突 | 3 |
| 9 | 错误暴露不掩盖 | R16扫描+validate_config V17 | 4 |
| 10 | 访谈每个设计分支 | 10个问题逐一确认 | 全部 |

---

## 风险与约束

- **不破坏现有功能**：所有变更为结构性优化，不改变工具行为
- **可回滚**：每层独立验证，一次只改一层
- **不影响编辑器日常使用**：sync.ps1 行为不变，软链目标不变
- **不对 plugins 做增删**：保持 installed 18/enabled 15/disabled 3 不变

## 验证标准

每层完成后：
1. `validate_config.py` 全量通过
2. `sync.ps1 -All -DryRun` 预览无异常
3. MANIFEST concern→excludes 无新增告警
4. R16 裸 except 计数 = 0
