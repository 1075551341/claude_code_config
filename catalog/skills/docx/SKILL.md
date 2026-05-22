---
name: docx
description: 创建Word文档
triggers: [创建Word文档, 编辑docx文件, 处理Word文档格式]
---

# DOCX 创建、编辑和分析

## 概述

用户可能要求您创建、编辑或分析 .docx 文件的内容。.docx 文件本质上是一个包含 XML 文件和其他资源的 ZIP 存档，您可以读取或编辑

## 工作流决策树

### 读取/分析内容

使用下方"文本提取"或"原始 XML 访问"部分

### 创建新文档

使用"创建新 Word 文档"工作流

### 编辑现有文档

- **您自己的文档 + 简单更改**：使用"基本 OOXML 编辑"工作流
- **他人的文档**：使用**"红线修订工作流"**（推荐默认）
- **法律、学术、商业或政府文档**：使用**"红线修订工作流"**（必需）

## 读取和分析内容

### 文本提取

如果您只需要读取文档的文本内容，使用 pandoc 将文档转换为 markdown：

```bash
# 将文档转换为 markdown 并保留追踪更改
pandoc --track-changes=all path-to-file.docx -o output.md
```

### 原始 XML 访问

以下情况需要原始 XML 访问：批注、复杂格式、文档结构、嵌入媒体和元数据

#### 关键文件结构

- `word/document.xml` - 主文档内容
- `word/comments.xml` - document.xml 中引用的批注
- `word/media/` - 嵌入的图像和媒体文件

## 创建新 Word 文档

从头创建新 Word 文档时，使用 **docx-js**，它允许您使用 JavaScript/TypeScript 创建 Word 文档

### 工作流

1. 阅读文档了解详细语法
2. 使用 Document、Paragraph、TextRun 组件创建 JavaScript/TypeScript 文件
3. 使用 Packer.toBuffer() 导出为 .docx

## 编辑现有 Word 文档

编辑现有 Word 文档时，使用 **Document 库**（用于 OOXML 操作的 Python 库）

### 工作流

1. 阅读 ooxml 文档
2. 解压文档
3. 使用 Document 库创建并运行 Python 脚本
4. 打包最终文档

## 文档审查的红线修订工作流

此工作流允许您在 markdown 中规划全面的追踪更改，然后在 OOXML 中实现它们

**原则：最小、精确的编辑**
实现追踪更改时，仅标记实际更改的文本

### 追踪更改工作流

1. **获取 markdown 表示**：将文档转换为 markdown 并保留追踪更改
2. **识别并分组更改**：审查文档并识别所有需要的更改
3. **阅读文档并解压**
4. **分批实现更改**
5. **打包文档**
6. **最终验证**

## 将文档转换为图像

要视觉分析 Word 文档，使用两步过程将其转换为图像：

1. **将 DOCX 转换为 PDF**：

   ```bash
   soffice --headless --convert-to pdf document.docx
   ```

2. **将 PDF 页面转换为 JPEG 图像**：
   ```bash
   pdftoppm -jpeg -r 150 document.pdf page
   ```