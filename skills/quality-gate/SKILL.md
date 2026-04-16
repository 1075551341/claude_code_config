---
name: quality-gate
description: 质量门检查，自动检测schema drift、安全锚定、范围缩减
triggers:
  - 质量门
  - quality gate
  - 质量检查
  - 门控
priority: P1
---
# 质量门

## 三道门

### 1. Schema Drift 检测
- 检查ORM变更是否缺少对应migration
- 阻断条件：发现未同步的schema变更

### 2. 安全锚定
- 检查验证逻辑是否绑定到威胁模型
- 阻断条件：安全相关变更缺少验证绑定

### 3. 范围缩减检测
- 检查planner是否静默丢弃需求
- 警告条件：实现范围小于计划范围

## 执行时机
- 配置变更时自动触发
- Verify阶段强制执行
- Ship阶段前必须全部通过
