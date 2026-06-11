---
name: onboarding-guide
description: 新项目/新成员引导（对标 OpenSpec onboard）。触发词：onboard、新人引导、项目入门、熟悉代码库。
triggers: [onboard, 新人引导, 项目入门, 熟悉代码库]
layer: supplement
source: Fission-AI/OpenSpec
disable-model-invocation: true
loading_tier: L3
---

# Onboarding Guide

11 阶段精简为 5 阶段实用引导。

## Phase 1 — 项目概览

- 读 `README.md` + `CLAUDE.md`（若存在）
- `/understand-domain` 或 understand-anything 领域视图
- 输出：一句话项目目标 + 主要用户

## Phase 2 — 代码结构

- `/understand` 生成交互知识图
- `codegraph_explore` 扫描顶层模块
- 输出：目录职责表（≤10 行）

## Phase 3 — 关键路径

- `codegraph_trace` 主入口函数
- 识别 3 条核心用户路径
- 输出：调用链摘要

## Phase 4 — 开发环境

- 验证依赖安装 + 构建/测试命令
- 记录 TTHW 与摩擦点（→ dx-reviewer 视角）
- 输出：可运行的最小验证命令

## Phase 5 — 第一个任务

- 选最小有价值任务（≤3 文件）
- 走完整五阶段：discuss → plan → execute → verify
- 输出：PR 或本地 commit

## 约束

- 每阶段有明确产出，不跳过 verification
- 代码探索遵守 R17（codegraph 优先）
- 历史先查 claude-mem（R18）
