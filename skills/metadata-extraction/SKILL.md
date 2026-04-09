---
name: metadata-extraction
description: 当需要提取文件元数据、分析文档属性、检查图片Exif信息、文件取证分析时调用此技能。触发词：元数据提取、metadata、文件属性、Exif信息、文档信息、图片信息、文件分析、元数据分析。
---

# 文件元数据提取

## 核心能力

**提取各类文件元数据、分析文档属性、获取Exif信息。**

---

## 适用场景

- 文件取证分析
- 元数据提取
- 文档信息检查
- 图片Exif分析

---

## 图片元数据

### Exif 信息

```python
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    if exif_data:
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"{tag}: {value}")

# 常见Exif字段
- Make: 设备厂商
- Model: 设备型号
- DateTime: 拍摄时间
- GPSInfo: GPS定位
- ExposureTime: 曝光时间
- FNumber: 光圈值
- ISOSpeedRatings: ISO感光度
```

### ExifTool

```bash
# 提取所有元数据
exiftool image.jpg

# 提取GPS信息
exiftool -gps:all image.jpg

# 批量提取
exiftool -r -json . > metadata.json

# 删除元数据
exiftool -all= image.jpg
```

---

## 文档元数据

### PDF

```python
import PyPDF2

def get_pdf_metadata(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        meta = reader.metadata
        
        return {
            'Title': meta.title,
            'Author': meta.author,
            'Creator': meta.creator,
            'Producer': meta.producer,
            'CreationDate': meta.creation_date,
            'ModDate': meta.modification_date
        }
```

### Word 文档

```python
from docx import Document

def get_docx_metadata(docx_path):
    doc = Document(docx_path)
    props = doc.core_properties
    
    return {
        'Title': props.title,
        'Author': props.author,
        'Created': props.created,
        'Modified': props.modified,
        'LastModifiedBy': props.last_modified_by,
        'Revision': props.revision
    }
```

### Excel

```python
import openpyxl

def get_xlsx_metadata(xlsx_path):
    wb = openpyxl.load_workbook(xlsx_path)
    props = wb.properties
    
    return {
        'Title': props.title,
        'Creator': props.creator,
        'Created': props.created,
        'Modified': props.modified,
        'LastModifiedBy': props.lastModifiedBy
    }
```

---

## 视频/音频元数据

### FFprobe

```bash
# 获取所有信息
ffprobe -v quiet -print_format json -show_format -show_streams video.mp4

# 提取时长
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4

# 提取分辨率
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 video.mp4
```

### MediaInfo

```bash
# 完整信息
mediainfo video.mp4

# JSON格式
mediainfo --Output=JSON video.mp4
```

---

## 系统文件元数据

### 基本属性

```bash
# Linux/macOS
stat file.txt

# 输出
# Size: 1024
# Access: 2024-01-15 10:00:00
# Modify: 2024-01-14 15:30:00
# Change: 2024-01-14 15:30:00
# Birth: 2024-01-10 09:00:00
```

### 扩展属性

```bash
# Linux
getfattr -d file.txt

# macOS
xattr -l file.txt

# Windows
icacls file.txt  # ACL信息
```

---

## 批量提取

```python
import os
from datetime import datetime

def extract_all_metadata(directory):
    results = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            stat = os.stat(filepath)
            
            results.append({
                'filename': file,
                'path': filepath,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat()
            })
    
    return results
```

---

## 取证分析

### 时间线分析

```python
def analyze_timeline(metadata_list):
    """分析文件时间线，发现异常"""
    
    # 检查创建时间晚于修改时间
    for m in metadata_list:
        if m['created'] > m['modified']:
            print(f"异常: {m['filename']} 创建时间晚于修改时间")
    
    # 检查批量修改时间
    # 检查时间戳合理性
    # 分析访问模式
```

### 完整性检查

```python
import hashlib

def calculate_hash(filepath):
    """计算文件哈希"""
    sha256 = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    
    return sha256.hexdigest()
```

---

## 注意事项

```
必须：
- 保持原始文件完整
- 记录提取时间
- 验证元数据有效性

避免：
- 修改原始文件
- 忽略时区问题
- 依赖单一元数据源
```

---

## 相关技能

- `security-forensics` - 安全取证
- `data-analysis` - 数据分析
- `file-organization` - 文件整理