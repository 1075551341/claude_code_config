---
description: 按 gstack 路由规则执行多角色审查
---

# /review — gstack 多角色审查

按变更类型自动路由到对应审查角色。

## 路由规则

1. **所有变更** → `eng-reviewer`（必须）
2. **产品/新功能/scope 变更** → + `ceo-reviewer`
3. **UI/UX 变更** → + `designer`
4. **安全敏感变更** → + `security`
5. **infra/配置/cleanup** → CEO Review 可跳过

## 执行步骤

1. 运行 `git diff --name-only HEAD~1`（或指定 base）获取变更文件列表
2. 根据文件类型和变更内容判断路由：
   - 含 `.tsx/.css/.scss/components/` → 触发 designer
   - 含 `auth/security/crypto/payment/` → 触发 security
   - 新功能 / spec 变更 → 触发 ceo-reviewer
3. 依次执行对应 catalog agent 审查
4. 汇总输出审查结果

## 输出

```
## 审查汇总: [变更名]

### Eng Review: PASS/NEEDS-CHANGES
[摘要]

### CEO Review: GO/RETHINK/REJECT (如触发)
[摘要]

### Design Review: APPROVED/NEEDS-POLISH (如触发)
[摘要]

### Security Review: SAFE/RISKS-FOUND (如触发)
[摘要]

### 总结
[最终建议：可合并 / 需修改]
```

## 角色 Agents 位置

`~/.claude/catalog/agents/`：eng-reviewer、ceo-reviewer、designer、qa、security
