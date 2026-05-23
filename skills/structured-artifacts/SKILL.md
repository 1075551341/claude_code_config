---
name: structured-artifacts
description: GSD 结构化制品管理，确保跨会话状态存活。
layer: supplement
source: GSD-redux
---

# Structured Artifacts

## 制品清单
| 文件 | 职责 | 何时更新 |
|------|------|----------|
| PROJECT.md | 项目愿景与目标 | 项目启动/重大变更 |
| REQUIREMENTS.md | 功能/非功能需求 | discuss阶段 |
| ROADMAP.md | 里程碑与阶段 | plan阶段 |
| STATE.md | 当前位置与决策 | 每次状态变更 |
| CONTEXT.md | 阶段实现决策 | execute阶段 |

## 原则
1. 制品是会话间的唯一真相源
2. 新会话首先加载所有制品
3. 每次修改制品后立即持久化
4. 制品冲突时以最新时间戳为准

## 模板
→ templates/artifacts/ 目录
