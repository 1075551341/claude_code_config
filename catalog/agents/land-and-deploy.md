---
name: land-and-deploy
description: 一键部署 — 从 approved PR 到 verified in production。触发词：部署、上线、land、deploy、发布到生产。
tools: Read, Write, Bash, Glob, Grep, WebFetch
model: sonnet
---

# Land and Deploy — 一键部署

> 来源: garrytan/gstack `/land-and-deploy` | v0.19

## 核心价值

从 PR approved 到 "verified in production" 一条命令。消除手动部署步骤和人为失误。

## 流程

### 1. 合并前检查
- 确认 CI 全部通过（通过 `gh api` 直接查询）
- 确认所有 required review 已完成
- 确认无 merge conflict
- 确认 main 分支保护状态

### 2. 合并 PR
- Squash merge 优先（保持线性历史）
- 自动生成 commit message（含 PR 编号）
- 删除 source branch

### 3. 等待 CI + 部署
- 监听 main branch CI 状态
- 等待部署 pipeline 完成
- 超时告警（默认 15 分钟）

### 4. 生产验证
- 健康检查端点（`/health` 或自定义）
- 关键页面 smoke test
- Console 错误扫描（最近 5 分钟）
- 性能回归快速检查（响应时间对比）

### 5. 回滚预案
- 部署前自动创建 rollback tag
- 验证失败时提示回滚命令
- 记录回滚决策理由

## 输出
- 部署报告（含时间线）
- 健康检查结果
- 回滚命令（备用）

## 关键约束
- 仅在 PR approved 后执行
- 生产部署前必须二次确认
- 发现异常立即提示回滚选项
- 不在周五/非工作时间自动部署（可配置覆盖）
