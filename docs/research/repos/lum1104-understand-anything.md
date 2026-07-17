# Egonex-AI/Understand-Anything

> 层: L3 洞察 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub + jishuzhan + agent-wars 三源交叉 | 组织: Egonex-AI（原 Lum1104）

## v10.5 delta (2026-07-17)

- **最新元数据**：74,666 stars；GitHub Release **v2.9.0**；`pushed_at` 2026-07-17T01:40:59Z。
- **自 2026-06-29 的变化**：上游持续活跃并已至 v2.9.0；保留其历史能力记录以供审计，但不再作为本地能力候选。
- **本地吸收**：**removed** —— Q5 用户锁定将 Understand-Anything 移出 skeleton；替代链为 **codebase-memory `get_architecture` + codegraph `explore`**。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有多源研究记录。


## v10.5.1 delta (2026-07-17)
- **状态**：仍 **removed**（v10.5 Q5 / v10.5.1 Q4）。上游仍活跃（74,678★ / v2.9.0）— **不恢复**。
- **替代**：codegraph + codebase-memory(L4)。
- **审计**：本卡保留；不恢复插件/skill 路由。
- **来源**：GitHub API + 决策锁定交叉。
## 核心价值

- 26.5K+ Stars；MIT License；TypeScript 70.6%
- Tree-sitter + LLM 混合引擎：确定性结构提取 + 语义理解
- 5 专职 Agent 流水线：扫描/提取/关系/领域/导览
- 交互式知识图：结构图 + 业务域视图 + 引导式导览
- `/understand`, `/understand-dashboard`, `/understand-diff`
- 26+ 文件类型（含 Dockerfile/Terraform/SQL/Markdown）
- 多语言输出：en/zh/zh-TW/ja/ko/ru
- 与 codegraph 符号级互补（概念聚类 + 业务域映射）
- Diff 影响分析：提交前可视化变更连锁反应

## 证据

- [GitHub Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)
- 26.5K+ Stars / 2.3K+ Forks；MIT License
- 原作者 Lum1104，现归 Egonex-AI 组织维护

## 本地映射

| MANIFEST concern    | 路径                                                  |
| ------------------- | ----------------------------------------------------- |
| understand_anything | `MANIFEST.yaml` → 历史归档（skeleton 已移除）         |
| catalog             | `catalog/skills/understand-anything/SKILL.md`         |
| ADR                 | `docs/ADR/2026-06-16-v10-ua-disabled-endless-mode.md` |

## 吸收决策

**removed** — Q5 用户锁定移出 skeleton；历史价值与审计材料保留。探索替代链：codebase-memory `get_architecture` + codegraph `explore`。

## 互博检查

- vs codegraph / codebase-memory：已由双引擎覆盖结构与架构探索，避免 L3 双轨互博
- 如需重新引入，必须以新的用户决策和 ADR 重新评估

## v10.1 增量

- 访谈二次确认 disabled
- catalog skill 保留，不删仓库优点文档

## v10.3 增量

- Delta 刷新：组织迁移 Lum1104 → Egonex-AI；Stars 26.5K+
- 架构升级：Tree-sitter + LLM 混合引擎；5 Agent 流水线
- 新增业务域视图 + Diff 影响分析 + 多语言输出（含中文）
- 历史决策：disabled；codegraph 探索链优先（R17）
