---
name: file-organization
description: 整理文件目录
triggers: [整理文件目录, 组织文件结构, 批量重命名, 文件分类归档]
---

# 文件整理与组织

## 核心能力

**文件分类整理、目录结构优化、批量重命名。**

---

## 适用场景

- 文件目录整理
- 批量文件操作
- 文件分类归档
- 目录结构优化

---

## 文件分类策略

### 按类型分类

```
project/
├── documents/     # 文档类
│   ├── pdf/
│   ├── doc/
│   └── txt/
├── images/        # 图片类
│   ├── jpg/
│   ├── png/
│   └── svg/
├── media/         # 媒体类
│   ├── video/
│   └── audio/
├── code/          # 代码类
│   ├── js/
│   ├── py/
│   └── ts/
└── archives/      # 压缩包
    ├── zip/
    └── rar/
```

### 按时间分类

```
project/
├── 2024/
│   ├── 01/
│   ├── 02/
│   └── 03/
└── 2023/
    ├── 12/
    └── 11/
```

### 按项目分类

```
workspace/
├── project-a/
│   ├── docs/
│   ├── src/
│   └── assets/
├── project-b/
└── shared/
    └── resources/
```

---

## 批量操作

### 批量重命名

```bash
# 使用 rename (Linux)
rename 's/old/new/' *.txt

# 使用 PowerShell
Get-ChildItem *.txt | Rename-Item -NewName { $_.Name -replace 'old','new' }

# 使用 Python
import os
for f in os.listdir('.'):
    if f.endswith('.txt'):
        os.rename(f, f.replace('old', 'new'))
```

### 批量移动

```bash
# 按扩展名移动
find . -name "*.jpg" -exec mv {} images/ \;

# 按日期移动
find . -type f -newermt "2024-01-01" -exec mv {} 2024/ \;
```

### 批量删除

```bash
# 删除空目录
find . -type d -empty -delete

# 删除临时文件
find . -name "*.tmp" -delete

# 删除旧文件
find . -mtime +30 -delete  # 30天前
```

---

## 清理策略

### 重复文件检测

```bash
# 使用 fdupes
fdupes -r .  # 查找重复
fdupes -rd . # 交互删除

# 使用 jdupes
jdupes --delete --recurse .
```

### 大文件查找

```bash
# 查找大文件
find . -size +100M -exec ls -lh {} \;

# 排序大小
du -h --max-depth=1 | sort -hr
```

### 临时文件清理

```bash
# 常见临时文件
- *.tmp
- *.temp
- *.log
- .DS_Store
- Thumbs.db
- ~$*
- *.bak
```

---

## 组织脚本示例

### Python 整理脚本

```python
import os
import shutil
from pathlib import Path

# 文件类型映射
FILE_TYPES = {
    'documents': ['.pdf', '.doc', '.docx', '.txt', '.md'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.svg'],
    'code': ['.js', '.py', '.ts', '.java', '.go'],
    'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
}

def organize_folder(folder_path):
    for file in Path(folder_path).iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            for category, extensions in FILE_TYPES.items():
                if ext in extensions:
                    target_dir = Path(folder_path) / category
                    target_dir.mkdir(exist_ok=True)
                    shutil.move(str(file), str(target_dir / file.name))
                    break

organize_folder('./downloads')
```

---

## 命名规范

### 文件命名

```
推荐格式：
- 项目_类型_日期_版本.ext
- 20240115_report_v1.pdf
- user_data_backup_20240115.zip

避免：
- 特殊字符（除 - 和 _）
- 空格（用下划线替代）
- 过长文件名
- 中文文件名（跨平台问题）
```

### 目录命名

```
推荐：
- 使用小写
- 单词用连字符连接
- 简洁有意义
- my-project/
- user-data/

避免：
- 空格
- 特殊字符
- 过深嵌套（最多3层）
```

---

## 注意事项

```
必须：
- 操作前备份
- 先测试小范围
- 记录操作日志

避免：
- 直接操作重要数据
- 忽略权限问题
- 批量删除无确认
```

---

## 相关技能

- `deploy-script` - 部署脚本
- `python-pro` agent - Python 脚本