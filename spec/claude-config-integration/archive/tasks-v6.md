# Tasks v6.0 — 27 仓库全量重新整合

> **设计源**: design-v6.md | **日期**: 2026-06-05 | **原则**: 原子任务 2-5min，精确文件路径，可执行验证

---

## DAG 依赖图

```
Wave1 (并行，无依赖)
  T1: CLAUDE.md 精炼
  T2: rules/CORE.md 骨架归位
  T3: research-summary 更新
  T4: catalog/skills/vibe-coding-cn 创建
         ↓
Wave2 (并行，依赖 Wave1)
  T5: rules/CONTEXT.md 去骨架化
  T6: rules/WORKFLOW.md deer-flow 2.0 更新
  T7: rules/BESTPRACTICE.md 去骨架化
  T8: rules/SECURITY.md §15 ML注入防御
         ↓
Wave3 (并行，依赖 Wave2)
  T9: MANIFEST.yaml v7.2
  T10: agents/ 新增 codex-reviewer + ios-specialist
  T11: hooks/ loop防护 + context上限
         ↓
Wave4 (并行，依赖 Wave3)
  T12: agent.yaml 更新
  T13: settings.json hook注册更新
  T14: sync 提示 + 最终验证
```

---

## Wave1: 骨架精炼 (无依赖，并行)

### T1: CLAUDE.md 精炼 [P0]

**文件**: `C:\Users\DELL\.claude\CLAUDE.md`

**操作**: 
1. 更新架构公式为 "五柱 × 五阶段 × 三横切"
2. 三级横切层 (L1治理/L2优化/L3洞察) 在入口可见
3. 精炼至 ~220 行 (当前 ~260)
4. 更新 gsd 源为 open-gsd/gsd-core
5. 更新 claude-mem 版本 13.4.0
6. 更新 codegraph 数据 47%/58%/16%

**验证**: `wc -l CLAUDE.md` ≤ 240, `grep -c "L1治理\|L2优化\|L3洞察" CLAUDE.md` = 3

### T2: rules/CORE.md 骨架归位 [P0]

**文件**: `C:\Users\DELL\.claude\rules\CORE.md`

**操作**:
1. 新增 "三横切基础设施" 节 (~10行)
2. 迁入三级阈值 <40%/50%/70% + 行动 (~15行)
3. 迁入五阶段定义 + 状态机 (~15行)
4. 迁入 R14-R16 铁律详情 (~10行)
5. 新增 vibe-coding-cn 道/法/术/器 摘要 (~10行)
6. 总增量 ~60行

**验证**: `grep -c "三横切\|40%.*50%.*70%\|①规划.*②规格\|R16.*except:pass" rules/CORE.md` ≥ 4

### T3: research-summary 更新 [P1]

**文件**: `C:\Users\DELL\.claude\docs\research\27-repo-research-v6.md`

**操作**:
1. 基于本轮全量 WebFetch 结果更新所有仓库版本
2. 标注关键发现 (ECC 2.0.0-rc.1, gstack 0.19, deer-flow 2.0, gsd迁移)
3. 更新架构公式和仓库落点表

**验证**: 文件存在，含 27 仓库版本号

### T4: catalog/skills/vibe-coding-cn 创建 [P1]

**文件**: `C:\Users\DELL\.claude\catalog\skills\vibe-coding-cn\SKILL.md`

**操作**:
1. 创建目录 + SKILL.md
2. 吸收益/法/术/器框架 + α/Ω 元技能概念
3. 五步协作流程融入现有五阶段

**验证**: `grep -c "道\|法\|术\|器\|α\|Ω" catalog/skills/vibe-coding-cn/SKILL.md` ≥ 4

---

## Wave2: 规则层去骨架化 (依赖 Wave1)

### T5: rules/CONTEXT.md 去骨架化 [P1]

**文件**: `C:\Users\DELL\.claude\rules\CONTEXT.md`

**操作**:
1. 删除已迁入 CORE.md 的三级阈值节
2. 保留详细策略 (claude-context MCP/codegraph/UA使用策略)
3. 在 frontmatter 新增 `paths:` glob 触发
4. 在首行标注 "骨架内容已迁至 CORE.md"

**验证**: 文件不含 "<40%/50%/70%" 完整描述块, 含 `paths:` frontmatter

### T6: rules/WORKFLOW.md deer-flow 2.0 更新 [P1]

**文件**: `C:\Users\DELL\.claude\rules\WORKFLOW.md`

**操作**:
1. 更新 deer-flow 描述为 "LangGraph-based 2.0"
2. 新增 flash/standard/pro/ultra 四模式
3. 新增 claude-to-deerflow 桥接说明
4. 删除已迁入 CORE.md 的阶段定义
5. 在首行标注 "骨架内容已迁至 CORE.md"

**验证**: `grep -c "LangGraph\|flash\|standard\|pro\|ultra\|claude-to-deerflow" rules/WORKFLOW.md` ≥ 3

### T7: rules/BESTPRACTICE.md 去骨架化 [P1]

**文件**: `C:\Users\DELL\.claude\rules\BESTPRACTICE.md`

**操作**:
1. 删除已迁入 CORE.md 的错误处理规范节
2. 保留 API设计/日志规范/会话管理/代码精炼
3. 在 frontmatter 新增 `paths:` glob 触发
4. 在首行标注 "骨架内容已迁至 CORE.md"

**验证**: 文件不含 "异步操作必须 try/catch" 完整描述块

### T8: rules/SECURITY.md §15 ML注入防御 [P2]

**文件**: `C:\Users\DELL\.claude\rules\SECURITY.md`

**操作**:
1. 新增 §15 "ML 注入防御" 节
2. 吸收 gstack v0.19 三层防护: 22MB本地分类器 + canary tokens + Haiku转录检查
3. 标注来源: garrytan/gstack v0.19

**验证**: `grep -c "22MB.*分类器\|canary.*token\|Haiku.*转录" rules/SECURITY.md` ≥ 2

---

## Wave3: 治理与Agent层 (依赖 Wave2)

### T9: MANIFEST.yaml v7.2 [P0]

**文件**: `C:\Users\DELL\.claude\MANIFEST.yaml`

**操作**:
1. 版本 7.1 → 7.2
2. 架构描述更新为 "五柱×五阶段×三横切"
3. 新增 governance 分区 (L1治理: ECC+deer-flow)
4. 新增 insight 分区 (L3洞察: codegraph+UA+Firecrawl/Exa)
5. gstack 扩展: 新增 ios_specialist, codex_review, ml_defense
6. gsd source 更新为 open-gsd/gsd-core
7. deer-flow 更新为 2.0 LangGraph
8. vibe_coding_cn owner 从 catalog/skills 明确

**验证**: `grep -c "governance\|7.2\|open-gsd/gsd-core\|deer.*2.0\|ios_specialist" MANIFEST.yaml` ≥ 4

### T10: agents/ 新增 gstack v0.19 角色 [P2]

**文件**: 
- `C:\Users\DELL\.claude\agents\codex-reviewer.md` (新建)
- `C:\Users\DELL\.claude\agents\ios-specialist.md` (新建)

**操作**:
1. codex-reviewer: 跨模型独立审查，来自 gstack /codex
2. ios-specialist: iOS QA/fix/design-review/clean/sync，来自 gstack v0.19

**验证**: 2个新文件存在，frontmatter 含 source: garrytan/gstack

### T11: hooks/ loop防护 + context上限 [P1]

**文件**: 
- `C:\Users\DELL\.claude\hooks\pre-loop-guard.py` (新建)
- `C:\Users\DELL\.claude\hooks\pre-context-injector.py` (修改)

**操作**:
1. pre-loop-guard.py: 吸收 ECC observer loop 防护机制 (5层守卫简化版)
2. pre-context-injector.py: 新增 SessionStart 上下文上限 8000 字符 (ECC 机制)

**验证**: pre-loop-guard.py 存在且含重入检测; pre-context-injector.py 含 8000 字符上限

---

## Wave4: 整合验证 (依赖 Wave3)

### T12: agent.yaml 更新 [P2]

**文件**: `C:\Users\DELL\.claude\agent.yaml`

**操作**:
1. 新增 deer-flow 2.0 LangGraph 编排引用
2. 新增 codex-reviewer + ios-specialist 注册
3. 同步 MANIFEST v7.2 变更

**验证**: YAML lint 通过

### T13: settings.json hook注册更新 [P1]

**文件**: `C:\Users\DELL\.claude\settings.json`

**操作**:
1. 注册 pre-loop-guard hook
2. 确认 context上限参数
3. 新增 ECC_HOOK_PROFILE 环境变量支持

**验证**: `grep -c "pre-loop-guard\|ECC_HOOK_PROFILE" settings.json` ≥ 1

### T14: sync提示 + 最终验证 [P1]

**文件**: 
- `C:\Users\DELL\.claude\hooks\post-edit-format.py` (修改)

**操作**:
1. post-edit-format.py 新增: 检测 rules/ 编辑 → 提示重跑 sync.ps1
2. 最终验证: MANIFEST check + validate_config + grep 互博检查

**验证**: `python scripts/validate_config.py --quick` 返回 0

---

## 验收标准

- [ ] CLAUDE.md 含 "五柱 × 五阶段 × 三横切" 架构公式
- [ ] CORE.md 含三级阈值 + 五阶段定义 + 铁律 R14-R16
- [ ] CONTEXT.md/WORKFLOW.md/BESTPRACTICE.md 骨架内容已去重
- [ ] MANIFEST.yaml v7.2 含 governance + insight 分区
- [ ] vibe-coding-cn 道/法/术/器 落地
- [ ] gstack v0.19 iOS + codex-reviewer + ML防御 落地
- [ ] deer-flow 2.0 LangGraph 描述正确
- [ ] 27 仓库全部有落点，版本号最新
- [ ] validate_config 通过
- [ ] 无左右互博 (MANIFEST excludes 完整)
