# 非简单任务规格目录

> 存放规格、设计与任务分解。**仓库 PRIMARY 设计**见 [claude-config-integration/](./claude-config-integration/)。

---

## 三轨规格边界

| 轨道 | 路径 | 适用场景 | 命令 |
|------|------|----------|------|
| **OpenSpec** | 项目根 `openspec/changes/<id>/` | 功能变更、brownfield、需审批 | /propose /apply /archive |
| **GSD-redux** | 项目根 `.planning/phases/XX-*/` | 大功能多阶段、>2 周里程碑 | /plan |
| **轻量 spec** | `spec/<project>/` | ≤3 文件、需求明确小功能 | /plan |

**互斥**：同一功能 ID 不可同时存在于两轨。

### 选型决策树

```
收到功能需求
├─ 影响多模块 / brownfield / 需审批 → openspec/changes/<id>/
├─ 大功能 / 多阶段 / >2 周 → .planning/phases/XX-*/
└─ ≤3 文件 / 小改动 → spec/<project>/
```

---

## 目录结构

### 轻量 spec（本目录）

```
spec/
├── claude-config-integration/     # 全局配置整合（示例）
│   ├── design.md                  # 架构设计
│   ├── spec.md                    # 需求规格
│   └── tasks.md                   # 任务分解
└── <project>/
    ├── spec.md                    # 需求 + 验收标准
    ├── design.md                  # 技术设计（可选）
    └── tasks.md                   # 任务 + 进度（可选）
```

### OpenSpec（项目根，模板见 ~/.claude/templates/openspec/）

```
openspec/changes/<change-id>/
├── proposal.md
├── specs/
├── design.md
└── tasks.md
```

### GSD-redux（项目根，模板见 ~/.claude/templates/planning/）

```
.planning/phases/03-feature/
├── 03-SPEC.md      # WHAT/WHY（锁定）
├── 03-CONTEXT.md   # HOW（discuss 产出）
└── 03-PLAN.md      # 任务分解
```

---

## 模板位置

| 类型 | 模板路径 |
|------|----------|
| OpenSpec | `~/.claude/templates/openspec/` |
| GSD-redux | `~/.claude/templates/planning/` |
| 轻量 spec | `~/.claude/templates/spec/` |
| DESIGN.md | `~/.claude/templates/DESIGN.md` |

---

## 使用方式

1. **小功能**：在 `spec/<project>/` 创建三件套
2. **功能变更**：`/propose` → `openspec/changes/<id>/`
3. **大功能**：`.planning/phases/` + GSD 模板
4. **UI 项目**：额外创建项目根 `DESIGN.md`

---

_与 CLAUDE.md Spec 驱动章节、design.md 三轨设计对齐_
