---
name: browser-qa
description: 浏览器QA测试，真实浏览器点击验证，发现bug并原子提交修复。
layer: supplement
source: garrytan/gstack
---

# Browser QA

## 触发
- 手动：`/qa <url>`
- 自动：/ship 前建议

## 流程
1. 启动真实浏览器（Chromium）
2. 按测试计划点击关键流程
3. 发现 bug → 原子提交修复
4. 为每个修复生成回归测试
5. 重新验证修复
6. 输出：bug 报告 + 修复提交列表

## 与 qa agent 的关系
browser-qa 用真实浏览器；qa agent 做测试充分性审查。互补。
