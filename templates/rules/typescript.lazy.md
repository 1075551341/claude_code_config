---
description: 项目 TypeScript 规则示例，复制后按项目配置调整
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript 规则示例

- 尊重项目 tsconfig、公共接口和已有类型模式。
- 在系统边界收窄未知输入；尽量避免 any，必要例外说明原因。
- 异步错误明确传播或处理；使用项目现有类型检查与测试命令。
- 路径匹配 frontmatter 属于宿主能力，复制后验证实际触发。
