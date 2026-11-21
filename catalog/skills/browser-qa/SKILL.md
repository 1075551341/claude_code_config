---
name: browser-qa
description: 用户显式要求浏览器 UI 或 E2E 验证时，按测试计划检查真实交互并记录缺陷。
layer: supplement
source: garrytan/gstack
disable-model-invocation: true
---

# Browser QA

仅用户明确要求浏览器、UI 验证或 E2E 时使用，不因准备发布而自动启动浏览器。

1. 根据原始需求确定关键路径、环境、账号边界和预期结果。
2. 使用宿主可用且获准的真实浏览器能力，记录操作及观察结果。
3. 缺陷附最小复现与影响，修复由实施者在授权范围内完成；不执行 Git 提交或推送。
4. 复验受影响路径，必要时增加回归测试；不把截图存在当作交互成功。
5. 输出缺陷、修复及未验证项。审查者与实施者保持角色分离。
