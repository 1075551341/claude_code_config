---
name: understand-anything
description: 代码知识图谱分析 — 扫描项目生成交互式知识图，支持结构/领域/引导导览视图
argument-hint: "[path] [--full|--review|--language <lang>]"
source: Lum1104/Understand-Anything
layer: supplement
triggers:
  - 项目架构理解
  - 代码知识图谱
  - understand-anything
  - 交互知识图
  - 引导导览
disable-model-invocation: true
loading_tier: L3
---

# Understand-Anything — 交互式知识图谱

> **v10 状态：disabled** — 插件已关、探索走 codegraph（R17）。复启用见 `docs/ADR/2026-06-16-v10-ua-disabled-endless-mode.md`
>
> 来源：Lum1104/Understand-Anything v2.7.5 | 多 Agent 管线生成交互式知识图

## 功能

扫描项目生成 `knowledge-graph.json`，提供：
- **结构视图**：文件/模块/类/函数 节点与关系
- **领域视图**：按业务领域聚类
- **引导导览**：新人 onboarding 路径
- **影响分析**：修改文件前评估影响面
- **团队共享**：图谱 JSON 可提交到仓库供团队共用

## 子命令

| 命令 | 用途 |
|------|------|
| `/understand` | 生成/更新知识图谱 |
| `/understand --full` | 强制全量重建 |
| `/understand --review` | 运行 LLM 审查验证图谱质量 |
| `/understand --language zh` | 中文输出 |
| `/understand-chat` | 基于图谱的交互问答 |
| `/understand-dashboard` | 打开交互式仪表板 |
| `/understand-domain` | 领域驱动分析 |
| `/understand-onboard` | 生成新人导览文档 |
| `/understand-explain` | 解释特定模块/函数 |
| `/understand-knowledge` | 分析 Karpathy 模式 LLM wiki |
| `/understand-diff` | 基于图谱分析 git diff 影响 |

## 何时使用

- **新项目接手**：`/understand --review` 生成知识图谱
- **架构评审**：`/understand --full` 重建最新结构
- **影响分析**：改代码前 `/understand-diff` 评估影响面
- **新人入职**：`/understand-onboard` 生成导览
- **代码审查**：`/understand-explain <file>` 理解变更上下文

## 与 codegraph 互补

| 场景 | 工具 |
|------|------|
| 预索引快速查询（结构/调用链） | codegraph MCP |
| 交互式可视化/领域聚类/导览 | understand-anything |
| 符号级追踪 | codegraph |
| 新人 onboarding | understand-anything |

## 原则

- 图谱 JSON 可提交到 `.understand-anything/` 团队共享
- 重大重构后建议 `--full` 重建
- 结合 codegraph MCP 实现"快速查询 + 深度理解"双模式
