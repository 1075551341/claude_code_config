---
description: 交叉验证与质量门检查（④验证阶段）
---

# /verify — 交叉验证与质量门检查

对已完成工作执行完整验证。Claim → Evidence，每项验证必须附证据。

## 代码验证

```
□ 构建通过（零错误、零警告）
□ 类型检查通过
□ Lint 通过
□ 所有修改文件已重读确认生效
□ 无调试残留（console.log / debugger / print）
□ 无未处理 TODO / FIXME / HACK
```

## 安全验证

```
□ 无硬编码密钥/凭证/Token
□ 无 SQL 注入 / XSS / CSRF 风险
□ 敏感操作有权限检查
□ 输入验证在系统边界完成
□ 无 new Date() 等不稳定时间处理
```

## 质量门（stop-verification-gate.py 消费 config/quality_gates.json）

```
□ Schema Drift: ORM/model 变更缺 migration → 启发式提醒（model/ORM 文件变更无 migration）
□ Security Anchor: auth 相关变更 → 提醒绑定威胁模型
□ Scope Reduction: 存在活跃 plan/spec 制品 → 强制对照 tasks 清单确认无静默缩范围
```

## 审查委派（非简单任务必须）

```
□ 代码文件变更 ≥3 个 → 委派 eng-reviewer（只读审查 diff）获取 PASS/NEEDS-CHANGES
□ 项目已建 code-review-graph → 调用 detect_changes_tool 检查 test-gap 与高风险函数
```

> 「≥3 个」是 Stop 门按**会话累计编辑数**触发的代理规则，与 task-triage 六维分类不是同一维度：
> 2 文件的非简单任务不触发本项，但 verify_tier 仍为全量。分类 SSOT → `skills/task-triage/SKILL.md`。

> **硬门兜底**：Stop 时 stop-verification-gate.py 自动核查上述项，未通过 exit 2 阻止停止。

## 输出格式

```
## 验证结果
| 检查项 | 状态 | 证据 |
|--------|------|------|
| 构建   | ✅   | `npm run build` 零错误 |
| 类型   | ✅   | `tsc --noEmit` 零错误 |
| ...    | ...  | ...  |

## 未通过项
[若有，列出修复计划]
```
