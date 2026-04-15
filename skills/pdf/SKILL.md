---
name: pdf
description: 处理PDF文件、提取PDF文本、合并拆分PDF、填写PDF表单
triggers: [PDF处理, PDF文件, PDF提取, PDF合并, PDF拆分, PDF编辑, PDF表单]
---

# PDF 处理指南

## 概述

本指南涵盖使用 Python 库和命令行工具进行的基本 PDF 处理操作

## 快速开始

```python
from pypdf import PdfReader, PdfWriter

# 读取 PDF
reader = PdfReader("document.pdf")
print(f"页数: {len(reader.pages)}")

# 提取文本
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python 库

### pypdf - 基本操作

#### 合并 PDF

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### 拆分 PDF

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

### pdfplumber - 文本和表格提取

#### 带布局提取文本

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### 提取表格

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"第 {i+1} 页的表格 {j+1}:")
            for row in table:
                print(row)
```

### reportlab - 创建 PDF

#### 基本 PDF 创建

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# 添加文本
c.drawString(100, height - 100, "Hello World!")
c.save()
```

## 命令行工具

### pdftotext (poppler-utils)

```bash
# 提取文本
pdftotext input.pdf output.txt

# 保留布局提取文本
pdftotext -layout input.pdf output.txt
```

### qpdf

```bash
# 合并 PDF
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# 拆分页面
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
```

## 快速参考

| 任务         | 最佳工具    | 命令/代码                  |
| ------------ | ----------- | -------------------------- |
| 合并 PDF     | pypdf       | `writer.add_page(page)`    |
| 拆分 PDF     | pypdf       | 每文件一页                 |
| 提取文本     | pdfplumber  | `page.extract_text()`      |
| 提取表格     | pdfplumber  | `page.extract_tables()`    |
| 创建 PDF     | reportlab   | Canvas 或 Platypus         |
| 命令行合并   | qpdf        | `qpdf --empty --pages ...` |
| OCR 扫描 PDF | pytesseract | 先转换为图像               |

## 依赖项

所需依赖项（如不可用则安装）：

- **pandoc**: `sudo apt-get install pandoc`（用于文本提取）
- **LibreOffice**: `sudo apt-get install libreoffice`（用于 PDF 转换）
- **Poppler**: `sudo apt-get install poppler-utils`（用于 pdftoppm）
- **defusedxml**: `pip install defusedxml`（用于安全 XML 解析）
