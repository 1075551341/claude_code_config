# Skills 技能库

> **全局 31 个**（运行时加载）+ **catalog/**（97 领域库，按需复制）。格式标准：anthropics/skills
> 本地 13 个覆盖 superpowers 插件同名 skill（token 节省 45-74%，中文适配，五阶段集成）

---

## 全局（31）

### P0 强制（5，skeleton）

using-superpowers | brainstorming | change-impact-analysis | verification-before-completion | systematic-debugging

### Superpowers Workflow（9，supplement）

writing-plans | executing-plans | test-driven-development | subagent-driven-development | using-git-worktrees | requesting-code-review | receiving-code-review | finishing-a-development-branch | writing-skills

### Meta（5，supplement）

memory-compression | spec-validation | karpathy-guidelines | caveman-compress | change-impact-analysis

### 扩展（8，supplement — gstack/GSD/ECC）

autoplan | browser-qa | design-pipeline | ship | office-hours | context-engineering | structured-artifacts | instinct-learning

### Mattpocock（2）

triage | improve-codebase-architecture

### 项目洞察（1）

understand-anything

### 外部桥接（1）

deer-flow(claude-to-deerflow skill，可选)

---

## Catalog（按需）

路径：`~/.claude/catalog/skills/`（97）

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project <path> --skill python-backend
```

领域示例：frontend-design, api-development, ui-ux-pro-max …

---

## 格式

```yaml
---
name: skill-name
description: 一句话 + 触发场景
layer: skeleton | supplement
---
```

---

## 互斥（见 MANIFEST.yaml）

- 计划 → writing-plans（非 hook/pre-task-planner）
- 审查 → requesting/receiving-code-review
- 记忆 SSOT → claude-mem plugin + memory-compression skill
- 模式提取 Stop → stop-pattern-extraction hook（v1）；instinct-learning 负责 v2 置信度/evolve，不替代 hook

---

## 来源

superpowers（13 链）| gstack/GSD/ECC（扩展 8）| anthropics/skills（格式）| catalog（领域）
