---
name: token-conservation
description: 减少冗余输出、聚焦要点、言简意赅
triggers: [精简, 废话, 简化输出, 聚焦要点, 减少token]
---

# Token 节约准则

## @Examples

```
用户: "详细解释一下"
Claude: /token-conservation → 精简回答 → 核心点 + 必要细节

用户: "太长了"
Claude: /token-conservation → 直接回答 → 无解释过程
```

## 输出准则

| 要求 | 执行 |
|------|------|
| 直击要点 | 先结论，后解释 |
| 禁止废话 | 不解释过程、不汇报步骤 |
| 代码精简 | 最小改动集 |
| 按需补充 | 用户要求时才展开 |
