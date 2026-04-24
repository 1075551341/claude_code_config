# 非简单任务规格目录

> 存放非简单任务的规格、设计与任务分解文件

## 目录结构约定

```
spec/
├── <project>/                    # 项目名称（如：api-gateway, mobile-app）
│   ├── spec.md                  # 需求规格与验收标准（必须）
│   ├── design.md                # 技术设计（可选）
│   └── tasks.md                 # 任务分解与进度（可选）
└── README.md                    # 本文件
```

## 使用方式

1. **新建任务时**：在对应项目目录下创建 `spec.md`，记录需求与验收标准
2. **复杂设计时**：如需架构决策，补充 `design.md`
3. **长任务跟踪时**：用 `tasks.md` 记录子任务完成状态，便于释放上下文

## 命名示例

- `spec/api-gateway/v2-migration.md` — API 网关 V2 迁移规格
- `spec/mobile-app/offline-sync.md` — 移动端离线同步设计
- `spec/refactor/auth-module.md` — 认证模块重构任务

---

_与 `CLAUDE.md` 中的 Spec 驱动章节对齐_
