---
name: secure-deletion
description: 当需要安全删除文件、数据销毁、磁盘擦除、敏感数据清理时调用此技能。触发词：安全删除、文件销毁、数据擦除、安全擦除、磁盘擦除、敏感数据删除、彻底删除、数据销毁。
---

# 安全文件删除

## 核心能力

**安全删除文件、数据擦除、敏感数据清理。**

---

## 适用场景

- 敏感文件删除
- 数据销毁合规
- 磁盘擦除
- 安全清理

---

## 删除级别

| 级别 | 方法 | 适用场景 |
|------|------|----------|
| 基础 | 单次覆写 | 一般敏感数据 |
| 标准 | 3次覆写 | 敏感数据 |
| 高级 | 7次覆写 | 高敏感数据 |
| 军用 | DoD 5220.22-M | 机密数据 |

---

## 安全删除工具

### Linux

```bash
# shred 命令
shred -u file.txt              # 默认3次覆写
shred -n 7 -u file.txt         # 7次覆写
shred -vfz -n 5 /dev/sda       # 擦除整个磁盘

# wipe 命令
wipe -r folder/                # 递归删除目录
wipe -k file.txt               # 保留文件但擦除内容

# srm (secure-delete套件)
srm file.txt
srm -r folder/
```

### macOS

```bash
# 安全清空垃圾桶
rm -P file.txt                 # 覆写3次

# 磁盘工具安全擦除
diskutil secureErase freespace 0 /Volumes/Macintosh\ HD
```

### Windows

```powershell
# Cipher 命令（擦除空闲空间）
cipher /w:C:\

# SDelete工具
sdelete file.txt
sdelete -s folder\
sdelete -p 5 file.txt          # 5次覆写
```

---

## Python 实现

```python
import os
import random

def secure_delete(filepath, passes=3):
    """安全删除文件"""
    if not os.path.exists(filepath):
        return False
    
    filesize = os.path.getsize(filepath)
    
    with open(filepath, 'ba+') as f:
        for _ in range(passes):
            f.seek(0)
            # 随机数据覆写
            f.write(os.urandom(filesize))
            f.flush()
            os.fsync(f.fileno())
            
        # 最后用零覆写
        f.seek(0)
        f.write(b'\x00' * filesize)
        f.flush()
        os.fsync(f.fileno())
    
    # 删除文件
    os.remove(filepath)
    return True
```

---

## 磁盘擦除

### 完整擦除

```bash
# Linux
shred -vfz -n 3 /dev/sda

# macOS
diskutil secureErase 3 /dev/disk2

# Windows (需管理员权限)
format X: /P:3
```

### 空闲空间擦除

```bash
# Linux (创建大文件占满空间后删除)
dd if=/dev/urandom of=/zero_fill bs=1M
rm /zero_fill

# macOS
diskutil secureErase freespace 3 /Volumes/Macintosh\ HD

# Windows
cipher /w:C:\
```

---

## 注意事项

### 必须验证

```
删除后验证：
1. 文件是否真正消失
2. 使用恢复工具检查
3. 验证磁盘空间已清理
```

### 存储介质特性

| 类型 | 特性 | 建议 |
|------|------|------|
| HDD | 可覆写 | shred有效 |
| SSD | 磨损均衡 | 使用ATA Secure Erase |
| USB | 可能有缓存 | 多次确认 |
| 云存储 | 分布式 | 使用平台提供的安全删除 |

### SSD 特殊处理

```bash
# ATA Secure Erase
hdparm --user-master u --security-set-pass password /dev/sda
hdparm --user-master u --security-erase password /dev/sda
```

---

## 合规要求

```markdown
## 数据销毁记录

- 销毁时间：2024-01-15 10:00
- 操作人：张三
- 文件/设备：xxx
- 销毁方法：3次覆写
- 验证结果：成功恢复
- 见证人：李四
```

---

## 相关技能

- `security-forensics` - 安全取证
- `security-best-practices` - 安全实践