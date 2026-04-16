---
date: 2026-04-15
confidence: 0.8
category: workflow
status: active
verified_count: 1
---

# 工作流经验模式

> 来源：obra/superpowers, gsd-build/get-shit-done, bytedance/deer-flow

---

## 模式5: Iron Law

```markdown
---
name: iron-law-enforcement
date: 2026-04-15
confidence: 0.95
source: superpowers
tags: [workflow, discipline, quality]
---

# Iron Law 强制执行

## 背景
开发者经常跳过前置步骤直接进入实现，导致质量问题。

## 模式
使用 Iron Law 强制前置步骤：
```markdown
## The Iron Law
NO [ACTION] WITHOUT [PREREQUISITE] FIRST

变体：
- NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST (TDD)
- NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST (Debugging)
- NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

## 反合理化检查
| 合理化借口 | 反驳 |
|------------|------|
| "我检查过了" | 重新运行验证命令，输出证据 |
| "小改动不需要测试" | 任何改动都可能引入回归 |
| "太简单不需要验证" | 铁律无一例外 |

## 提取决策
- 置信度: 0.95
- 提取为: workflow rule
- 原因: 多次验证，几乎总是有效
```

---

## 模式6: Phase工作流

```markdown
---
name: phased-implementation
date: 2026-04-15
confidence: 0.85
source: get-shit-done
tags: [workflow, phases, iteration]
---

# 分阶段实现工作流

## 背景
大型功能PR难以review，容易引入回归。

## 模式
将大型功能分解为独立可交付阶段：
```
Phase 1: Minimum Viable — 最小可工作切片
Phase 2: Core Experience — 完整快乐路径
Phase 3: Edge Cases — 错误处理、边界情况、打磨
Phase 4: Optimization — 性能、监控
```

## 优势
- 每阶段可独立合并
- 降低大PR的review难度
- 更快获得用户反馈
- 减少回归风险

## 提取决策
- 置信度: 0.85
- 提取为: workflow template
- 原因: 显著改善大型功能的交付质量
```

---

## 模式7: TDD RED-GREEN-REFACTOR

```markdown
---
name: tdd-red-green-refactor
date: 2026-04-15
confidence: 0.9
source: superpowers, everything-claude-code
tags: [tdd, testing, quality]
---

# TDD RED-GREEN-REFACTOR 循环

## 模式
```
RED:    写一个失败的测试 → 运行测试确认失败
GREEN:  写最小代码通过测试 → 运行测试确认通过
REFACTOR: 清理代码，测试保持通过
```

## 关键原则
1. 测试必须在实现之前编写
2. 目标 80%+ 覆盖率（金融/认证 100%）
3. 写最小代码使测试通过
4. 不跳过任何阶段

## 红牌警告 - STOP
- Code before test
- "I already manually tested it"
- "Tests after achieve the same purpose"

## 提取决策
- 置信度: 0.9
- 提取为: workflow skill
- 原因: 业界验证的质量保障方法
```

---

## 模式8: PR多角色审查

```markdown
---
name: multi-role-pr-review
date: 2026-04-15
confidence: 0.85
source: awesome-claude-code
tags: [pr, review, quality]
---

# PR多角色审查

## 背景
单一角色审查容易遗漏问题。

## 模式
8阶段PR审查协议：
```
FETCH → CONTEXT → REVIEW → VALIDATE → DECIDE → REPORT → PUBLISH → OUTPUT
```

## 多角色审查链
1. Product Manager Review → 商业价值/用户体验
2. Developer Review → 代码质量/性能
3. Quality Engineer Review → 测试覆盖/边缘case
4. Security Engineer Review → 漏洞/数据保护
5. DevOps Review → CI/CD/基础设施
6. UI/UX Designer Review → 视觉/可用性

## 关键原则
所有"未来"改进必须立即实施，无延迟。

## 提取决策
- 置信度: 0.85
- 提取为: review workflow
- 原因: 全面覆盖多个维度
```
