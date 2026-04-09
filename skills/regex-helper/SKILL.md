---
name: regex-helper
description: 当需要编写正则表达式、匹配文本模式、解决正则匹配问题时调用此技能。触发词：正则表达式、Regex、正则匹配、模式匹配、文本匹配、正则验证、RegExp、正则替换、正则提取。
---

# 正则表达式助手

## 常用正则模式

### 身份证/证件

```regex
# 中国身份证（18位）
^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$

# 手机号（中国大陆）
^1[3-9]\d{9}$

# 邮箱
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

# 护照
^[EeGg]\d{8}$

# 统一社会信用代码
^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$
```

### 网络相关

```regex
# URL
^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$

# IPv4
^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$

# IPv6
^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$

# 域名
^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$

# MAC 地址
^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$
```

### 数字相关

```regex
# 整数
^-?\d+$

# 正整数
^[1-9]\d*$

# 浮点数
^-?\d+\.\d+$

# 金额（最多2位小数）
^\d+(\.\d{1,2})?$

# 科学计数法
^[+-]?\d+(\.\d+)?[Ee][+-]?\d+$

# 百分比
^(100|(\d{1,2}(\.\d{1,2})?))%$
```

### 文本处理

```regex
# 中文
^[\u4e00-\u9fa5]+$

# 中英文数字下划线
^[\u4e00-\u9fa5a-zA-Z0-9_]+$

# HTML 标签
<([a-z]+)([^<]+)*(?:>(.*)<\/\1>|\/?>)

# 匹配空白行
^\s*$

# 移除注释
\/\/.*$|\/\*[\s\S]*?\*\/

# 密码强度（至少8位，包含大小写字母和数字）
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$
```

### 日期时间

```regex
# 日期 YYYY-MM-DD
^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$

# 时间 HH:MM:SS
^([01]\d|2[0-3]):[0-5]\d:[0-5]\d$

# 日期时间
^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$

# ISO 8601
^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$
```

## 性能优化

### 避免灾难性回溯

```regex
# ❌ 危险：嵌套量词
(a+)+

# ✅ 优化：使用原子组或占有量词
(?>a+)+
a++
```

### 常见优化技巧

```regex
# 1. 使用非捕获组
(?:pattern)  # 不捕获，性能更好

# 2. 避免回溯：使用贪婪/懒惰量词
.*?   # 懒惰，匹配最少
.*    # 贪婪，匹配最多

# 3. 使用字符类代替分支
[abc]  # 比 (a|b|c) 更快

# 4. 锚点优化
^pattern$  # 快速失败

# 5. 原子组（防止回溯）
(?>pattern)
```

## 跨语言语法

### JavaScript

```javascript
// 创建正则
const regex = /pattern/gi
const regex = new RegExp('pattern', 'gi')

// 方法
regex.test(string)      // 布尔
regex.exec(string)      // 匹配结果数组
string.match(regex)     // 匹配结果数组
string.matchAll(regex)  // 迭代器
string.replace(regex, 'replacement')
string.split(regex)

// 命名捕获组（ES2018+）
const regex = /(?<year>\d{4})-(?<month>\d{2})/
const { groups: { year, month } } = regex.exec('2024-03')
```

### Python

```python
import re

# 创建正则
pattern = re.compile(r'pattern', re.IGNORECASE)

# 方法
re.match(pattern, string)      # 从头匹配
re.search(pattern, string)     # 搜索
re.findall(pattern, string)    # 所有匹配
re.sub(pattern, 'replacement', string)  # 替换
re.split(pattern, string)      # 分割

# 命名捕获组
match = re.search(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-03')
year = match.group('year')
```

### TypeScript 类型安全

```typescript
// 类型安全的正则匹配
function matchGroups<T extends Record<string, string>>(
  regex: RegExp,
  str: string
): T | null {
  const match = regex.exec(str)
  if (!match?.groups) return null
  return match.groups as T
}

// 使用
interface DateGroups {
  year: string
  month: string
  day: string
}

const dateRegex = /^(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})$/
const result = matchGroups<DateGroups>(dateRegex, '2024-03-19')
```

## 调试工具

### 在线工具

- [regex101.com](https://regex101.com) - 多语言支持，详细解释
- [regexr.com](https://regexr.com) - 可视化匹配
- [debuggex.com](https://debuggex.com) - 可视化流程图

### 调试技巧

```javascript
// 1. 分步测试
const parts = ['\\d{4}', '-', '\\d{2}', '-', '\\d{2}']
parts.forEach(part => console.log(part, new RegExp(part).test('2024-03-19')))

// 2. 查看匹配详情
const regex = /(\d{4})-(\d{2})-(\d{2})/g
let match
while ((match = regex.exec('2024-03-19 2025-01-01')) !== null) {
  console.log('Full:', match[0])
  console.log('Groups:', match.slice(1))
}
```

## 常见陷阱

| 陷阱 | 问题 | 解决 |
|------|------|------|
| 忘记转义 | `.` 匹配任意字符 | 使用 `\.` |
| 贪婪匹配 | `.*` 匹配过多 | 使用 `.*?` |
| 字符类错误 | `[a-z]` 范围 | 使用 `[a\-z]` 或 `[-a-z]` |
| 边界问题 | `\b` 单词边界 | 注意 Unicode 问题 |
| 性能问题 | 嵌套量词 | 使用原子组 |