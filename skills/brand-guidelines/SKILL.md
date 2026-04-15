---
name: brand-guidelines
description: 创建品牌指南
triggers: [创建品牌指南, 设计规范, 视觉风格指南, 品牌一致性文档]
---

# 品牌指南创建

## 核心能力

**创建完整的品牌视觉规范文档，确保设计一致性。**

---

## 适用场景

- 品牌风格指南编写
- 设计系统文档
- 视觉规范制定
- 团队设计一致性

---

## 指南结构

### 1. 品牌概述

```markdown
## 品牌故事
- 品牌定位
- 核心价值观
- 目标受众
- 品牌个性
```

### 2. Logo 规范

```markdown
## Logo 使用规范

### 主 Logo
- 清晰版本
- 适用场景

### Logo 变体
- 带底色版本
- 单色版本
- 简化版本

### 使用规则
- 最小尺寸：xx px
- 安全区域：xx px
- 禁止变形/遮挡
- 禁止自定义颜色
```

### 3. 色彩系统

```markdown
## 品牌色彩

### 主色
- Primary: #HEX (名称)
- 使用场景

### 辅助色
- Secondary: #HEX
- Accent: #HEX

### 功能色
- Success: #HEX
- Warning: #HEX
- Error: #HEX

### 调色板
- 亮色/暗色变体
- 渐变组合
```

### 4. 字体规范

```markdown
## 字体系统

### 主字体
- Heading: Font Name
- Body: Font Name

### 字号层级
- H1: xx px
- H2: xx px
- H3: xx px
- Body: xx px

### 行高/字距
- Line Height: xx
- Letter Spacing: xx
```

### 5. 图形元素

```markdown
## 图形风格

### 图标风格
- 线性/填充
- 尺寸规范
- 颜色使用

### 插画风格
- 技术说明
- 使用场景

### 照片风格
- 色调要求
- 构图规则
```

### 6. 应用示例

```markdown
## 应用场景

### 网站设计
- 首页布局
- 组件样式

### 文档设计
- 报告模板
- 演示模板

### 营销物料
- 海报规范
- 社交媒体
```

---

## 设计系统 Token

```css
/* Design Tokens */
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-secondary: #6366F1;
  --color-success: #22C55E;
  
  /* Typography */
  --font-heading: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-size-h1: 48px;
  --font-size-h2: 32px;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  
  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
}
```

---

## 输出格式

| 格式 | 适用场景 |
|------|----------|
| PDF | 正式文档分发 |
| Markdown | 团队 Wiki |
| Figma/Sketch | 设计团队 |
| CSS/JSON | 开发集成 |

---

## 注意事项

```
必须：
- 提供足够使用示例
- 明确禁止使用方式
- 包含可执行规范
- 定期更新维护

避免：
- 规范过于抽象
- 缺乏视觉示例
- 与实际设计脱节
- 不考虑技术实现
```

---

## 相关技能

- `frontend-design` - 前端设计
- `theme-config` - 主题配置
- `doc-coauthoring` - 文档协作
- `theme-factory` - 主题生成