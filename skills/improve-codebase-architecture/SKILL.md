---
name: improve-codebase-architecture
description: 领域驱动架构改进。对现有代码做结构化重构，跨文件、渐进式、有验证保障。
triggers: [架构改进, 重构, 代码结构, architecture, refactor, 模块拆分, 领域驱动]
layer: supplement
source: mattpocock/skills
---

# 架构渐进改进

对现有代码库做领域驱动的架构改进，跨文件、渐进式、不破坏现有功能。

## 术语表（共享词汇）

| 术语 | 定义 |
|------|------|
| Module | 一组相关文件，有明确定义的对外接口 |
| Interface | Module 的唯一入口点，消费者不绕过接口直接访问内部 |
| Implementation | Interface 背后的具体实现，可独立替换 |
| Depth | Module 的依赖链深度 — 越深越难改 |
| Seam | 两个 Module 之间可被拦截/替换的连接点 |
| Adapter | 桥接不同 Interface 的薄转换层 |
| Leverage | 给定改动影响的功能数量 — 高杠杆 = 小改动大影响 |
| Locality | 给定功能涉及的 Module 数量 — 高局部性 = 改动集中在少量 Module |

## 何时触发

- 模块超过 800 行
- 跨文件职责混乱
- 循环依赖
- 边界的 Seam 缺失（无法独立测试）

## 改进流程

### 1. Explore（探索）
派 Explore 子Agent 分析代码库，输出：
- 当前 Module 边界图
- 违规项：循环依赖、Interface 缺失、深度超标
- 受影响文件清单

### 2. Plan（方案）
基于术语表诊断问题，提出最小改动方案：
- 拆分/合并/提取 Interface / 插入 Adapter
- 改动前后对比（Mermaid 架构图）
- 推荐强度：STRONG（高杠杆+高局部性）/ MODERATE / WEAK

### 3. Report（报告）
生成包含以下内容的架构报告：
- 问题诊断（以术语表为分析框架）
- 前后架构对比图
- 改动文件清单 + 推荐强度徽章
- 验证策略

### 4. Grill（质疑循环）
对报告做逐个方案的质疑：
- 这个改动是否增加了 Depth？如果增加，成本是什么？
- 改动后的 Interface 是否能独立测试？
- 是否存在更小的 Seam 插入？
- 验证方法是否能证明"不破坏现有功能"？

### 5. Apply（渐进实施）
- 一次只改一个边界（文件数 ≤5）
- 每个边界改动独立 commit
- 改动后运行全量测试，失败即回退

## 核心原则

- **删除测试** — 写一个测试验证"旧行为存在"→ 删除旧代码 → 测试仍然通过 = 改动安全
- **接口即测试面** — 每个 Interface 必须有独立的测试面，不依赖 Implementation
- **最小改动** — 能插入 Adapter 不重写 Module
- **渐进提交** — 每步可独立 revert，不搞大爆炸

## 输出格式

```
## 架构改进方案: [名称]
### 诊断
- 问题: [边界违规/循环依赖/Interface缺失] 
- 术语分析: [Depth/X, Locality/Y, Seam/Z]
- 影响文件: [列表]

### 方案
- 改进方向: [拆分/合并/提取Interface/插入Adapter]
- 杠杆度: [高(HIGH LEVERAGE)/中/低]
- 风险: [低/中/高]

### 验证
- 删除测试: [测试文件 + 用例名]
- 全量测试: [命令 + 预期结果]
```

## 边界

- 与 brainstorming 的边界：brainstorming 设计新功能，本 skill 改进已有代码
- 与 code-reviewer 的边界：code-reviewer 审查单次 PR，本 skill 做跨文件的架构层面改进
- 一次最多改 5 个文件，更大重构分多次渐进
