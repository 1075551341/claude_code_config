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

## 质量门

```
□ Schema Drift: ORM 变更缺 migration → 阻断
□ Security Anchor: 验证绑定威胁模型 → 阻断
□ Scope Reduction: 静默丢弃需求 → 警告
```

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
