# Egonex-AI/Understand-Anything

> 层: L3 洞察 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub + jishuzhan + agent-wars 三源交叉 | 组织: Egonex-AI（原 Lum1104）

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

| MANIFEST concern | 路径 |
|------------------|------|
| understand_anything | `MANIFEST.yaml` → `status: disabled` |
| catalog | `skills/understand-anything/SKILL.md` |
| ADR | `docs/ADR/2026-06-16-v10-ua-disabled-endless-mode.md` |

## 吸收决策

**disabled** — 文档保留优点；探索链 codegraph → Grep → Read。

## 互博检查

- vs codegraph：避免 L3 双轨互博
- 复启用条件见 ADR（业务团队图谱 / 用户显式要求）

## v10.1 增量

- 访谈二次确认 disabled
- catalog skill 保留，不删仓库优点文档

## v10.3 增量

- Delta 刷新：组织迁移 Lum1104 → Egonex-AI；Stars 26.5K+
- 架构升级：Tree-sitter + LLM 混合引擎；5 Agent 流水线
- 新增业务域视图 + Diff 影响分析 + 多语言输出（含中文）
- 决策不变：disabled；codegraph 探索链优先（R17）
