---
name: office-hours
description: 六问产品框架，重新定义问题，挑战前提，生成实现方案。触发：/office-hours、产品讨论。
layer: supplement
source: garrytan/gstack
---

# Office Hours

## 触发
- 手动：`/office-hours`
- 自动：检测到产品需求讨论时建议

## 流程

### 1. 六问框架
```
Q1: 你试图解决的具体痛点是什么？
    → 要具体例子，不要假设性描述

Q2: 现有方案为什么不够好？
    → 识别真正的不满，不是功能缺失

Q3: 谁会用这个？他们的技术水平？
    → 用户画像，不是"所有人"

Q4: 最核心的一个场景是什么？
    → 如果只能做一个，做哪个

Q5: 如果这个功能明天就上线，你会第一个用它吗？
    → 真实需求 vs 虚构需求

Q6: 成功是什么样子？怎么衡量？
    → 可量化指标，不是"更好"
```

### 2. 重新定义
- 挑战用户的前提（用户说的可能是错的）
- 从痛点提取用户没意识到的能力
- 生成3个实现方案 + 工作量估算

### 3. 推荐
- 最窄楔子先行（明天就能用的最小版本）
- 完整愿景的时间线
- 输出 design doc → 喂入下游 skill

### 输出路径
- `specs/<name>/design.md`（OpenSpec）
- `.planning/design.md`（GSD）
- 直接传递给 `/plan-ceo-review`

### 互斥
不替代 brainstorming。office-hours 做产品问题定义；brainstorming 做技术方案发散。
