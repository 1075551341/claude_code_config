---
description: 项目级 Claude 配置（继承全局 ~/.claude/CLAUDE.md v10.4+）
alwaysApply: true
---

# {{PROJECT_NAME}} — 项目级配置

> 继承全局: `~/.claude/CLAUDE.md` | 归属: `MANIFEST.yaml` | 创建: `sync.ps1 -InitProject`

## 项目信息

- **名称**: {{PROJECT_NAME}}
- **技术栈**: {{TECH_STACK}} <!-- 如: TypeScript + React + Vite + TailwindCSS -->
- **包管理器**: {{PACKAGE_MANAGER}} <!-- pnpm / npm / yarn -->
- **初始化日期**: {{DATE}}

## 代码探索（R17 + CRG + everything；cbm 已禁用 v10.10+）

常驻 MCP 5：codegraph / code-review-graph / serena / everything / grep（按语义名调用，禁止 `mcp0_`）。

1. **codegraph（R17）**：`codegraph init` → `codegraph index` — 符号/调用链/「怎么运作」；默认 `codegraph_explore` / `codegraph_node` / `codegraph_search` / `codegraph_callers`
2. **CRG**：改前/完成前 `get_minimal_context` + `get_impact_radius`（有 git diff 再 `detect_changes`）；审查/PR 用 `get_review_context`
3. **everything**：本机文件名搜索；禁止替代工作区 Glob / R17 / CRG `detect_changes`
4. 无双图 → deny Grep/Glob/everything/编辑/查询 MCP

> codebase-memory 已永久禁用（全盘索引爆 CPU/内存）。架构/ADR 用 codegraph_explore；变更影响有图走 CRG，再叠加 codegraph blast-radius。

## 项目约定

<!-- 在此声明项目特有的约定，覆盖或补充全局规则 -->

### 目录结构

```
src/
  components/   # UI 组件
  services/     # 业务逻辑
  utils/        # 工具函数
  types/        # 类型定义
tests/          # 测试文件
```

### 命名规范

<!-- 项目特有命名约定，如: 组件 PascalCase / 工具函数 camelCase -->

### 依赖管理

- 锁定 major 版本（R14）
- 优先复用已有依赖，避免重复引入（R4）
- 安全补丁用同 major 最新版

## 项目特有规则

<!-- 声明项目独有的铁律/约束，如: -->
<!-- - 禁止直接修改 generated/ 目录下文件 -->
<!-- - API 请求统一走 services/api.ts -->

## 全局继承

以下配置从 `~/.claude/` 全局继承，无需重复声明：
- 五柱×五阶段×三横切骨架
- 铁律 R1–R20
- 上下文三级阈值（70%/90%/100%）
- 变更彻底性保障（有图：CRG `get_impact_radius` + `codegraph_explore` blast-radius + Grep）
- 工具路由（codegraph → 双图就绪后 Grep；本机文件名 → everything；cbm 已禁用）
- L0–L3 加载等级

## 覆盖声明

<!-- 如需覆盖全局规则，在此声明并给出理由 -->
<!-- 示例:本项目使用 npm 而非 pnpm（已有 package-lock.json）-->
