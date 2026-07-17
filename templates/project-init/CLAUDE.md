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

## 代码探索（双引擎，v10.4）

1. **codegraph（R17 常驻）**：`codegraph init` → `codegraph index` — 日常符号/调用链
2. **codebase-memory（L4 按需）**：`npx -y codebase-memory-mcp@0.8.1` → `scripts/cbm-index.ps1` → merge `mcp-configs/optional-dev.json` — 架构/ADR/变更影响

启用 cbm 条件见全局 `rules/CONTEXT.md`（满足 ≥2：大 monorepo / ADR / 跨服务 / 变更风险）。

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
- 铁律 R1–R19
- 上下文三级阈值（70%/90%/100%）
- 变更彻底性保障（codegraph_explore + codebase-memory L4 + Grep）
- 工具路由优先级（codegraph > cbm L4 架构/ADR > Grep > Read）
- L0–L3 加载等级

## 覆盖声明

<!-- 如需覆盖全局规则，在此声明并给出理由 -->
<!-- 示例:本项目使用 npm 而非 pnpm（已有 package-lock.json）-->
