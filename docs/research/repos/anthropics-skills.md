# anthropics/skills

> 层: 技能/实践 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub + mer.vin + WebSearch 三源交叉


## v10.5.1 delta (2026-07-17)
- **最新元数据**：161,770★；无 GH release；`pushed_at` 2026-07-16。
- **本地映射**：SKILL 格式参考；不整仓导入。
- **来源**：GitHub API（Tier-2）。
## 核心价值

- SKILL.md 官方格式规范
- `description` 字段 = Agent 触发器（非 name）
- YAML frontmatter 元数据标准
- 技能发现与 Tool-First 路由对齐

## 证据

- [GitHub anthropics/skills](https://github.com/anthropics/skills)
- ~151K+ Stars；Agent Skills 开放标准 2025-12-18 发布

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| 格式标准 | 所有 `skills/*/SKILL.md` frontmatter |
| 索引 | `skills-INDEX.md` |

## 吸收决策

**采纳** — 全库 SKILL.md 格式对齐 anthropics 规范。

## 互博检查

- vs Superpowers skills：格式统一，内容本地覆盖

## v10.1 增量

- 格式对齐验收纳入 validate_config 惯例检查

## v10.3 增量

- Delta 刷新：Stars 138K → ~151K；开放标准跨平台采纳确认
- 渐进式披露 3 层：L1 metadata 预载 → L2 SKILL.md 按需 → L3+ references/scripts
- 决策不变：全库 SKILL.md 格式对齐 anthropics 规范

## v10.5 delta (2026-07-17)

- Stars：161,759；最新 Release：无正式 Release（`gh api`）。
- 保持现有采纳范围，无强制扩展。
