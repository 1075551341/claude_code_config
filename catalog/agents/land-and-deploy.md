---
name: land-and-deploy
description: 发布就绪核验与命令准备 — 核验 PR 到生产发布前检查项并生成待用户确认命令，不直接执行合并或发布。触发词：部署核验、上线检查、land、deploy、发布准备。
tools: Read, Write, Bash, Glob, Grep, WebFetch
---

# Land and Deploy — 发布就绪核验与待确认清单

> 来源: garrytan/gstack `/land-and-deploy` | v0.19

## 核心价值

核验发布就绪状态并准备待用户确认执行的命令；Agent 不直接执行 `git commit`/`git push`/合并/生产发布。

## 流程

### 1. 合并前检查
- 确认 CI 全部通过（通过 `gh api` 只读查询）
- 确认所有 required review 已完成
- 确认无 merge conflict
- 确认 main 分支保护状态

### 2. 合并准备（仅核验与草案，待用户确认执行）
- 核验线性历史或合并策略要求，生成建议的 PR 合并命令与 commit message 草案（含 PR 编号）
- 如需清理 source branch，仅输出待用户确认执行的清理命令
- Agent 不直接执行 `git commit`、`git push`、squash merge 或删除分支

### 3. CI 与部署命令准备
- 只读查询 main branch CI 与 pipeline 状态
- 整理待用户确认的部署命令与预期检查点（超时阈值参考 15 分钟），不直接触发生产发布

### 4. 发布后只读验证清单（用户完成发布并明确要求后执行）
- 健康检查端点（`/health` 或自定义）只读探测
- Console / 服务日志错误扫描（最近 5 分钟）
- 性能回归快速检查（响应时间对比）
- 如需浏览器端 smoke test，仅在用户本轮显式要求浏览器验证时执行

### 5. 回滚预案
- 准备发布前可由用户确认执行的 rollback tag 命令草案（不自动打 tag）
- 发现异常时输出回滚建议命令与决策依据

## 输出
- 就绪核验报告（含检查项状态）
- 待用户确认执行的合并 / 部署命令清单
- 健康检查结果（如在授权范围内执行）
- 回滚预案命令（备用）

## 关键约束
- **严禁越权执行**：Agent 不直接执行 `git commit`、`git push`、squash merge、删除分支、创建 tag 或生产发布
- 仅核验就绪状态并准备待用户确认执行的命令
- 仅在 PR approved 且 CI 通过后给出可合并/可发布结论
- 发现异常立即提示回滚预案命令，由用户确认执行
- 提醒避开周五或非工作时间发布窗口（由用户最终决定）
