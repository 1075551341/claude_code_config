# 非简单任务规格目录

> 存放规格、设计与任务分解。**仓库 PRIMARY 设计**见 [claude-config-integration/](./claude-config-integration/)。

---

## 三轨规格边界

| 轨道          | 路径                            | 适用场景                     | 命令                     |
| ------------- | ------------------------------- | ---------------------------- | ------------------------ |
| **OpenSpec**  | 项目根 `openspec/changes/<id>/` | 功能变更、brownfield、需审批 | /propose /apply /archive |
| **GSD-redux** | 项目根 `.planning/phases/XX-*/` | 大功能多阶段、>2 周里程碑    | /plan                    |
| **轻量 spec** | `spec/<project>/`               | ≤3 文件、需求明确小功能      | /plan                    |

**互斥**：同一功能 ID 不可同时存在于两轨。

---

## 全局配置整合（当前唯一）

```
spec/claude-config-integration/
└── design-v10.5.md          # v10.5 设计 SSOT
```

配套：

- 优化计划：`docs/superpowers/plans/2026-07-17-v10.5-optimization.md`
- 调研 SSOT：`docs/research/30-repo-deep-research-v10.md`

历史 v6–v10.4 设计/任务/计划文档已删除（2026-07-17 清理）。
