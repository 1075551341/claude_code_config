---
name: xlsx
description: 当需要处理Excel表格、操作xlsx文件、处理CSV数据时调用此技能。触发词：Excel处理、xlsx、表格处理、CSV、Excel表格、电子表格、数据分析表格、Excel公式、Excel编辑。
license: Proprietary. LICENSE.txt has complete terms
---

# XLSX 创建、编辑和分析

## 概述

用户可能要求您创建、编辑或分析 .xlsx 文件的内容。

## 关键：使用公式，而非硬编码值

**始终使用 Excel 公式，而非在 Python 中计算值后硬编码。**

### ❌ 错误 - 硬编码计算值

```python
# 错误：在 Python 中计算并硬编码结果
total = df['Sales'].sum()
sheet['B10'] = total  # 硬编码 5000
```

### ✅ 正确 - 使用 Excel 公式

```python
# 正确：让 Excel 计算求和
sheet['B10'] = '=SUM(B2:B9)'
```

## 读取和分析数据

### 使用 pandas 进行数据分析

```python
import pandas as pd

# 读取 Excel
df = pd.read_excel('file.xlsx')  # 默认：第一个工作表
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # 所有工作表作为字典

# 分析
df.head()  # 预览数据
df.info()  # 列信息
df.describe()  # 统计信息

# 写入 Excel
df.to_excel('output.xlsx', index=False)
```

## 创建新 Excel 文件

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# 添加数据
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['行', '数据', '这里'])

# 添加公式
sheet['B2'] = '=SUM(A1:A10)'

# 格式化
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# 列宽
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

## 编辑现有 Excel 文件

```python
from openpyxl import load_workbook

# 加载现有文件
wb = load_workbook('existing.xlsx')
sheet = wb.active

# 操作多个工作表
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"工作表: {sheet_name}")

# 修改单元格
sheet['A1'] = '新值'
sheet.insert_rows(2)
sheet.delete_cols(3)

# 添加新工作表
new_sheet = wb.create_sheet('新工作表')
new_sheet['A1'] = '数据'

wb.save('modified.xlsx')
```

## 财务模型标准

### 颜色编码标准

- **蓝色文本 (RGB: 0,0,255)**：硬编码输入
- **黑色文本 (RGB: 0,0,0)**：所有公式和计算
- **绿色文本 (RGB: 0,128,0)**：来自其他工作表的链接
- **红色文本 (RGB: 255,0,0)**：指向其他文件的外部链接
- **黄色背景**：需要关注的关键假设

### 数字格式标准

- **年份**：格式化为文本字符串（如 "2024" 而非 "2,024"）
- **货币**：使用 $#,##0 格式；始终在标题中注明单位
- **百分比**：默认使用 0.0% 格式（一位小数）
- **倍数**：格式化为 0.0x 用于估值倍数
- **负数**：使用括号 (123) 而非减号 -123

## 最佳实践

### 库选择

- **pandas**：最适合数据分析、批量操作和简单数据导出
- **openpyxl**：最适合复杂格式化、公式和 Excel 特定功能

### 使用 openpyxl

- 单元格索引从 1 开始（row=1, column=1 指向单元格 A1）
- 使用 `data_only=True` 读取计算值
- 对于大文件：使用 `read_only=True` 读取或 `write_only=True` 写入