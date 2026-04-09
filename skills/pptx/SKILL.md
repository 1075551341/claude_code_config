---
name: pptx
description: 当需要创建PPT演示文稿、编辑pptx文件、制作幻灯片时调用此技能。触发词：PPT制作、pptx、演示文稿、幻灯片、PPT编辑、演示PPT、PowerPoint、PPT生成、PPT设计。
license: Proprietary. LICENSE.txt has complete terms
---

# PPTX 创建、编辑和分析

## 概述

用户可能要求您创建、编辑或分析 .pptx 文件的内容。.pptx 文件本质上是一个包含 XML 文件和其他资源的 ZIP 存档。

## 读取和分析内容

### 文本提取

如果您只需要读取演示文稿的文本内容：

```bash
# 将文档转换为 markdown
python -m markitdown path-to-file.pptx
```

### 原始 XML 访问

以下情况需要原始 XML 访问：批注、演讲者备注、幻灯片布局、动画、设计元素和复杂格式。

#### 关键文件结构

- `ppt/presentation.xml` - 主演示文稿元数据和幻灯片引用
- `ppt/slides/slide{N}.xml` - 各幻灯片内容
- `ppt/notesSlides/notesSlide{N}.xml` - 每张幻灯片的演讲者备注
- `ppt/slideLayouts/` - 幻灯片布局模板
- `ppt/slideMasters/` - 母版幻灯片模板
- `ppt/theme/` - 主题和样式信息
- `ppt/media/` - 图像和其他媒体文件

## **不使用模板**创建新 PowerPoint 演示文稿

从头创建新 PowerPoint 演示文稿时，使用 **html2pptx** 工作流。

### 设计原则

**关键**：创建任何演示文稿之前，分析内容并选择适当的设计元素：

1. **考虑主题**：它暗示什么基调、行业或情绪？
2. **检查品牌**：如果用户提到公司/组织，考虑其品牌颜色
3. **配色与内容匹配**：选择反映主题的颜色
4. **说明您的方法**：在编写代码前解释您的设计选择

**要求**：

- ✅ 仅使用网页安全字体：Arial、Helvetica、Times New Roman、Georgia、Courier New、Verdana、Tahoma、Trebuchet MS、Impact
- ✅ 通过大小、粗细和颜色创建清晰的视觉层次
- ✅ 确保可读性：强对比度、适当大小的文字、清晰对齐
- ✅ 保持一致：在幻灯片中重复模式、间距和视觉语言

### 布局提示

- **两栏布局（推荐）**：使用跨全宽的标题，然后下方两栏
- **全幻灯片布局**：让特色内容占据整张幻灯片以获得最大冲击力
- **永远不要垂直堆叠**：不要在单栏中将图表/表格放在文本下方

## 编辑现有 PowerPoint 演示文稿

编辑现有 PowerPoint 演示文稿中的幻灯片时，需要使用原始 Office Open XML (OOXML) 格式。

### 工作流

1. 阅读 ooxml 文档
2. 解压演示文稿
3. 编辑 XML 文件
4. **关键**：每次编辑后立即验证
5. 打包最终演示文稿

## 创建缩略图网格

创建 PowerPoint 幻灯片的视觉缩略图网格：

```bash
python scripts/thumbnail.py template.pptx [output_prefix]
```

**功能**：

- 创建：`thumbnails.jpg`
- 默认：5 列，每个网格最多 30 张幻灯片
- 幻灯片从零开始索引（幻灯片 0、幻灯片 1 等）

## 将幻灯片转换为图像

1. **将 PPTX 转换为 PDF**：

   ```bash
   soffice --headless --convert-to pdf template.pptx
   ```

2. **将 PDF 页面转换为 JPEG 图像**：
   ```bash
   pdftoppm -jpeg -r 150 template.pdf slide
   ```