---
name: spec-validation
description: 规格可执行验证，将 spec/plan 转化为可验证的验收标准。触发：②规格门控、spec验证。
triggers: [规格验证, spec验证, 验收标准, 规格检查, 门控]
layer: supplement
disable-model-invocation: true
loading_tier: L2
source: Fission-AI/OpenSpec
---

# 规格验证

> **L2 仅②门控**：writing-plans 草案完成后 Read。未通过禁止 `/execute`。
> ④实现验收由 `verification-before-completion` 负责，本 skill 不在④重复 Read。

## 触发条件

- writing-plans 产出 plan/spec 草案后（**必须**）
- 用户显式要求验证规格

**不触发**：实现完成后的验收（→ verification-before-completion）

## 执行步骤

1. **解析规格**：读取 plan/spec，提取业务规则和验收条件
2. **生成验证清单**：每条验收条件转为可执行检查项
3. **门控检查**：每原子任务是否有验证命令；有无静默缩 scope
4. **输出报告**：通过 / 失败 / 待验证，附证据

## 验证格式

- 业务规则：EARS — When [event], the [system] shall [response]
- 验收条件：触发场景 → 预期行为

## 门控失败

输出 `BLOCKED` + 原因 + 回到 writing-plans。禁止静默缩 scope。

## 来源

- 仓库：Fission-AI/OpenSpec
- 置信度：0.75
