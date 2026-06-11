---
name: autoplan
description: 自动审查流水线，一条命令完成 CEO→Design→Eng 审查，仅暴露品味决策。
layer: supplement
source: garrytan/gstack
disable-model-invocation: true
loading_tier: L3
---

# Autoplan

## 触发
- 手动：`/autoplan`

## 流程
1. 读取 design doc（来自 office-hours 或 brainstorming）
2. 自动运行 CEO Review（范围挑战）
3. 自动运行 Design Review（评分 + AI slop 检测）
4. 自动运行 Eng Review（架构 + 测试矩阵）
5. 自动检测哪些审查适用（后端变更跳过 Design Review）
6. 仅暴露品味决策点给用户确认
7. 技术决策自动确定

## 智能路由
| 变更类型 | 审查 |
|----------|------|
| UI/前端 | CEO + Design + Eng |
| 后端/API | CEO + Eng |
| 架构/数据流 | Eng |
| 安全敏感 | CEO + Eng + Security |

## 输出
完整审查后的实施计划，可直接进入 executing-plans
