---
name: python-automation
description: 当需要编写Python自动化脚本、批量处理任务、自动化日常工作、编写工具脚本时调用此技能。触发词：Python自动化、自动化脚本、批量处理、Python脚本、自动化任务、工具脚本、批处理。
---

# Python 自动化脚本

## 核心能力

**自动化脚本编写、批量任务处理、工作流程自动化。**

---

## 适用场景

- 批量文件处理
- 自动化任务
- 定时执行脚本
- 日常工作效率

---

## 文件自动化

### 批量重命名

```python
import os
from pathlib import Path

def batch_rename(directory, pattern, replacement):
    for file in Path(directory).iterdir():
        if file.is_file():
            new_name = file.name.replace(pattern, replacement)
            file.rename(file.parent / new_name)
```

### 批量转换格式

```python
from PIL import Image
import os

def convert_images(input_dir, output_dir, format='png'):
    for f in os.listdir(input_dir):
        if f.endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(os.path.join(input_dir, f))
            name = os.path.splitext(f)[0]
            img.save(os.path.join(output_dir, f'{name}.{format}'))
```

### 文件整理

```python
import shutil
from pathlib import Path

def organize_files(directory):
    extensions = {
        'images': ['.jpg', '.png', '.gif'],
        'documents': ['.pdf', '.doc', '.txt'],
        'videos': ['.mp4', '.avi', '.mov'],
    }
    
    for file in Path(directory).iterdir():
        if file.is_file():
            for category, exts in extensions.items():
                if file.suffix.lower() in exts:
                    target_dir = Path(directory) / category
                    target_dir.mkdir(exist_ok=True)
                    shutil.move(str(file), str(target_dir / file.name))
```

---

## 系统自动化

### 执行命令

```python
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

# 执行命令
stdout, stderr = run_command('dir')
```

### 定时任务

```python
import schedule
import time

def job():
    print("执行任务...")

# 每天执行
schedule.every().day.at("09:00").do(job)

# 每小时执行
schedule.every().hour.do(job)

# 每分钟执行
schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 网络自动化

### 发送邮件

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = 'sender@example.com'
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

### 下载文件

```python
import requests

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
```

---

## Excel 自动化

```python
import openpyxl
from openpyxl.styles import Font, Alignment

def process_excel(input_file, output_file):
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active
    
    # 修改数据
    for row in ws.iter_rows(min_row=2):
        row[2].value = row[0].value * row[1].value  # 计算总价
    
    # 设置样式
    ws['A1'].font = Font(bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    wb.save(output_file)
```

---

## PDF 自动化

```python
from PyPDF2 import PdfMerger, PdfReader

# 合并PDF
def merge_pdfs(files, output):
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    merger.write(output)
    merger.close()

# 提取文本
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text
```

---

## 日志记录

```python
import logging
from datetime import datetime

logging.basicConfig(
    filename=f'automation_{datetime.now():%Y%m%d}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info('任务开始')
logging.error('发生错误')
```

---

## 异常处理

```python
def safe_execute(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except FileNotFoundError:
        logging.error(f'文件不存在: {args}')
    except PermissionError:
        logging.error(f'权限不足: {args}')
    except Exception as e:
        logging.error(f'未知错误: {e}')
    return None
```

---

## 注意事项

```
必须：
- 添加异常处理
- 记录执行日志
- 验证执行结果
- 保留原始文件

避免：
- 硬编码路径
- 忽略错误处理
- 过度消耗资源
- 删除未备份文件
```

---

## 相关技能

- `web-scraping` - 网络爬虫
- `file-organization` - 文件整理
- `scheduled-task` - 定时任务