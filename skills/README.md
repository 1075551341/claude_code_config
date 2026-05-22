# Skills 技能库

> **全局 17 个**（运行时加载）+ **catalog/**（领域库，按需复制）。格式标准：anthropics/skills

---

## 全局（17）

### P0 强制（4）

brainstorming | verification-before-completion | systematic-debugging | using-superpowers

### Workflow（9）

writing-plans | executing-plans | test-driven-development | subagent-driven-development | using-git-worktrees | requesting-code-review | receiving-code-review | finishing-a-development-branch | writing-skills

### Meta（4）

memory-compression | spec-validation | karpathy-guidelines | caveman-compress

---

## Catalog（按需）

路径：`~/.claude/catalog/skills/`（97）

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project <path> --skill python-backend
```

领域示例：frontend-design, api-development, deep-research, ui-ux-pro-max …

---

## 格式

```yaml
---
name: skill-name
description: 一句话 + 触发场景
---
```

---

## 互斥（见 MANIFEST.yaml）

- 计划 → writing-plans（非 hook/pre-task-planner）
- 审查 → requesting/receiving-code-review（非独立 code-review skill）
- 记忆 → claude-mem plugin + memory-compression skill

---

## 来源

superpowers（workflow）| anthropics/skills（格式）| ECC/catalog（领域）
