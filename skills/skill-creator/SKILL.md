---
name: skill-creator
description: 创建新技能、更新现有技能、设计AI编辑器技能包、编写SKILL.md文档
triggers: [创建新技能, 更新现有技能, 设计AI编辑器技能包, 编写SKILL.md文档, Skill创建, 技能创建]
---

# 技能创建器

## 核心原则：Token 是公共资源

- **只写模型不知道的内容**：通用知识、标准库用法无需重复
- **代码优于描述**：一个示例胜过三段解释
- **精准触发**：`description` 决定技能何时加载，必须明确

## 文件结构

```
skill-name/
  SKILL.md          # 必须：技能主文件
  scripts/          # 可执行脚本
  references/       # 参考文档
  templates/        # 代码模板
```

## SKILL.md 格式

```markdown
---
name: skill-name
description: [何时触发，动词开头，50 字以内]
triggers: [触发词1, 触发词2, 触发词3]
---

# 标题
[核心工作流]

## [章节] [只写模型可能不确定的内容]
```

## Description 编写

```
✅ "使用 Playwright 测试 Web 应用，支持导航、表单、截图。测试前端功能时使用。"
❌ "这是一个强大的测试工具，可以帮助您以各种方式测试应用程序..."
```

## 内容取舍

```
这条内容必要吗？
├─ 模型通用知识 → 删除
├─ 工具 API 的非直觉用法 → 保留
├─ 项目特有约定 → 保留
└─ 多步骤工作流顺序 → 保留
```

## 质量检查

- [ ] description 一句话说清"何时用"
- [ ] 代码示例可直接复用
- [ ] 无重复信息
- [ ] 无废话（"这个技能将帮助您..."一律删除）
- [ ] 总行数 ≤ 150 行（特殊情况 ≤ 300 行）

## 打包脚本

```bash
python scripts/quick_validate.py skill-name/
python scripts/package_skill.py skill-name/ --output dist/
```
