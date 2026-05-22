---
name: figma-design
description: Figma 设计工具集成与设计稿转代码
triggers: [Figma 设计工具集成与设计稿转代码]
---

# Figma 设计集成

## 核心功能

```
🎨 设计稿解析 - 读取 Figma 文件结构
📐 组件提取 - 导出设计组件
🔧 设计转代码 - 自动生成前端代码
📱 原型预览 - 交互流程展示
```

## API 配置

### Personal Access Token

```bash
FIGMA_ACCESS_TOKEN=figd-xxx
```

### API 基础

```typescript
const FIGMA_API = 'https://api.figma.com/v1';

async function figmaRequest(path: string) {
  const response = await fetch(`${FIGMA_API}${path}`, {
    headers: {
      'X-Figma-Token': process.env.FIGMA_ACCESS_TOKEN!,
    },
  });
  return response.json();
}
```

## 文件操作

### 获取文件

```typescript
// 获取文件信息
const file = await figmaRequest(`/files/${fileKey}`);
console.log(`文件名: ${file.name}`);
console.log(`页面数: ${file.document.children.length}`);

// 获取特定节点
const node = await figmaRequest(`/files/${fileKey}/nodes?ids=${nodeId}`);
```

### 导出图片

```typescript
async function exportImages(fileKey: string, nodeIds: string[]) {
  const response = await figmaRequest(
    `/images/${fileKey}?ids=${nodeIds.join(',')}&format=png&scale=2`
  );

  const images = response.images;
  for (const [nodeId, url] of Object.entries(images)) {
    console.log(`Node ${nodeId}: ${url}`);
  }
}
```

## 设计转代码

### 提取样式

```typescript
function extractStyles(node: FigmaNode) {
  const styles: CSSStyles = {};

  // 尺寸
  styles.width = node.absoluteBoundingBox?.width;
  styles.height = node.absoluteBoundingBox?.height;

  // 布局
  if (node.layoutMode === 'HORIZONTAL') {
    styles.display = 'flex';
    styles.flexDirection = 'row';
    styles.gap = node.itemSpacing;
  }

  // 文本
  if (node.type === 'TEXT') {
    styles.fontSize = node.style.fontSize;
    styles.fontWeight = node.style.fontWeight;
    styles.fontFamily = node.style.fontFamily;
    styles.color = rgbaToHex(node.fills[0]?.color);
  }

  return styles;
}
```

### 生成 React 组件

```typescript
function generateReactComponent(node: FigmaNode, name: string): string {
  const styles = extractStyles(node);

  return `
import React from 'react';
import styled from 'styled-components';

const Container = styled.div\`
  width: ${styles.width}px;
  height: ${styles.height}px;
  display: ${styles.display};
  gap: ${styles.gap}px;
\`;

export const ${name} = () => {
  return (
    <Container>
      ${generateChildren(node.children)}
    </Container>
  );
};
`;
}
```

### 生成 Tailwind 类名

```typescript
function generateTailwindClasses(node: FigmaNode): string {
  const classes: string[] = [];

  // 布局
  if (node.layoutMode === 'HORIZONTAL') {
    classes.push('flex', 'flex-row');
  }
  if (node.itemSpacing) {
    classes.push(`gap-${node.itemSpacing / 4}`);
  }

  // 内边距
  if (node.paddingLeft) {
    classes.push(`pl-${node.paddingLeft / 4}`);
  }

  // 背景
  if (node.fills?.[0]?.type === 'SOLID') {
    const color = rgbaToHex(node.fills[0].color);
    classes.push(`bg-[${color}]`);
  }

  // 圆角
  if (node.cornerRadius) {
    classes.push(`rounded-${node.cornerRadius / 4}`);
  }

  return classes.join(' ');
}
```

## 组件库同步

### 获取组件

```typescript
// 获取组件库
const components = await figmaRequest(
  `/files/${fileKey}/components`
);

for (const component of components.meta.components) {
  console.log(`组件: ${component.name}`);
  console.log(`描述: ${component.description}`);
}
```

### 组件变体

```typescript
function parseVariants(node: FigmaNode) {
  if (node.type !== 'COMPONENT_SET') return [];

  const variants = node.children.map((child) => {
    const props = parseVariantProperties(child.name);
    return {
      id: child.id,
      name: child.name,
      props,
      styles: extractStyles(child),
    };
  });

  return variants;
}

// Button/Primary, Size=Large, State=Hover
function parseVariantProperties(name: string) {
  return name.split(',').reduce((acc, part) => {
    const [key, value] = part.trim().split('=');
    acc[key] = value || key;
    return acc;
  }, {} as Record<string, string>);
}
```

## 设计 Token 提取

```typescript
interface DesignTokens {
  colors: Record<string, string>;
  typography: Record<string, TypographyToken>;
  spacing: number[];
  radii: number[];
}

async function extractDesignTokens(fileKey: string): Promise<DesignTokens> {
  const file = await figmaRequest(`/files/${fileKey}`);

  const tokens: DesignTokens = {
    colors: {},
    typography: {},
    spacing: [],
    radii: [],
  };

  // 遍历所有节点提取 token
  traverseNodes(file.document, (node) => {
    // 颜色
    if (node.styles?.fill) {
      const style = node.styles.fill;
      const color = node.fills[0]?.color;
      if (color) {
        tokens.colors[style] = rgbaToHex(color);
      }
    }

    // 圆角
    if (node.cornerRadius) {
      tokens.radii.push(node.cornerRadius);
    }
  });

  return tokens;
}
```

## 与开发工作流集成

### 自动化同步

```typescript
// GitHub Action 自动同步设计
// .github/workflows/sync-figma.yml
name: Sync Figma

on:
  schedule:
    - cron: '0 0 * * *'  # 每天同步

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run sync-figma
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_TOKEN }}
```

### Storybook 集成

```typescript
// 从 Figma 自动生成 Story
function generateStory(componentName: string, figmaNode: FigmaNode) {
  return `
import { ${componentName} } from './${componentName}';

export default {
  title: 'Components/${componentName}',
  component: ${componentName},
};

export const Default = () => <${componentName} />;
export const Hover = () => <${componentName} state="hover" />;
export const Disabled = () => <${componentName} disabled />;
`;
}
```

## 最佳实践

```markdown
1. 使用 Auto Layout 便于代码生成
2. 命名规范：组件名/变体名
3. 颜色/字体使用样式库
4. 保持设计组件与代码组件对应
5. 使用 Dev Mode 查看代码提示
6. 定期同步设计变更到代码
```