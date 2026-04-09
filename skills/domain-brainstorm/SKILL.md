---
name: domain-brainstorm
description: 当需要创意域名建议、域名命名、品牌域名选择时调用此技能。触发词：域名创意、域名推荐、域名命名、品牌域名、域名生成、域名选择、好域名。
---

# 域名创意

## 核心能力

**创意域名生成、品牌域名建议、域名可用性检查。**

---

## 适用场景

- 新项目域名选择
- 品牌域名规划
- 产品域名创意
- 域名投资评估

---

## 命名策略

### 命名原则

```markdown
好域名特征：
- 简短易记（5-10个字符最佳）
- 易拼写无歧义
- 与品牌/业务相关
- 避免连字符
- 避免数字混用
- 易于口头传播

顶级域名选择：
- .com - 最通用，首选
- .cn - 中国市场
- .io - 科技/创业
- .ai - 人工智能
- .co - 公司/创业
- .app - 应用程序
- .dev - 开发者
```

### 命名方法

```markdown
1. 品牌名直接使用
   - apple.com
   - google.com
   - 字节跳动 → bytedance.com

2. 关键词组合
   - 行业词+品牌词：cloudflare.com
   - 功能词+对象词：notion.so

3. 创意拼写
   - flickr.com (去掉e)
   - lyft.com (替代lift)

4. 缩写/首字母
   - baidu.com
   - tmall.com

5. 新造词
   - kodak.com
   - xerox.com

6. 组合词
   - facebook.com
   - wechat.com
```

---

## 创意生成

### 生成技巧

```markdown
词根变化：
- 添加前缀：un-, re-, in-, pre-
- 添加后缀：-ly, -ify, -io, -able
- 复合词：tech+hub=techhub

谐音替代：
- you → u
- for → 4
- to → 2
- are → r

拼写变化：
- 省略字母：flickr
- 替换字母：lyft
- 添加字母：storee

数字组合：
- 360（安全）
- 365（全年度）
- 99（长久）
```

### 分类生成

```markdown
科技类：
- tech, lab, hub, io, dev, code, cloud
- 示例：techlab.io, devhub.co

商业类：
- biz, corp, pro, plus, prime
- 示例：bizpro.com, primecorp.com

社交类：
- chat, talk, connect, meet, share
- 示例：quickchat.com, meetshare.com

内容类：
- blog, news, media, press, story
- 示例：storymedia.com, newsblog.io

工具类：
- tool, app, kit, box, helper
- 示例：toolbox.app, helperkit.io
```

---

## 域名生成器

### Python示例

```python
import itertools

def generate_domains(base_words, suffixes, tlds):
    """
    生成域名创意列表

    参数：
        base_words: 基础词列表
        suffixes: 后缀列表
        tlds: 顶级域名列表

    返回：
        list: 生成的域名
    """
    domains = []

    # 基础词组合
    for word in base_words:
        for suffix in suffixes:
            domains.append(f"{word}{suffix}")

    # 两词组合
    for combo in itertools.combinations(base_words, 2):
        domains.append(''.join(combo))

    # 添加顶级域名
    results = []
    for domain in domains:
        for tld in tlds:
            results.append(f"{domain}.{tld}")

    return results

# 使用示例
base_words = ['tech', 'cloud', 'data', 'smart', 'ai']
suffixes = ['hub', 'lab', 'ify', 'io', 'ly']
tlds = ['com', 'io', 'ai', 'co']

suggestions = generate_domains(base_words, suffixes, tlds)
for d in suggestions[:20]:
    print(d)
```

---

## 域名评估

### 评估维度

```markdown
1. 记忆度（1-10分）
   - 长度：越短越好
   - 拼写：是否易拼写
   - 发音：是否易发音

2. 相关性（1-10分）
   - 与品牌关联度
   - 与业务关联度
   - 与行业关联度

3. 商业价值（1-10分）
   - 市场需求
   - 投资价值
   - 品牌潜力

4. 技术因素
   - 可用性（是否被注册）
   - 价格（注册/购买费用）
   - 历史记录（是否有不良记录）
```

### 评分模板

```markdown
| 域名 | 长度 | 记忆度 | 相关性 | 可用性 | 总分 |
|------|------|--------|--------|--------|------|
| techhub.io | 7 | 8 | 9 | ✓ | 17 |
| smartai.com | 7 | 8 | 9 | ✓ | 17 |
| cloudly.co | 8 | 7 | 8 | ✓ | 15 |

推荐优先级：
1. 技术可行性（必须可用）
2. 品牌相关性
3. 记忆传播性
4. 投资价值
```

---

## 域名查询

### 查询渠道

```markdown
域名注册商：
- 阿里云（万网）
- 腾讯云
- GoDaddy
- Namecheap
- Google Domains

WHOIS查询：
- whois.com
- whois.aliyun.com
- icann.org/lookup

批量查询工具：
- instantdomainsearch.com
- leandomainsearch.com
- namechk.com
```

### 查询脚本

```python
import whois

def check_domain_availability(domain):
    """
    检查域名可用性

    参数：
        domain: 域名字符串

    返回：
        bool: True表示可用
    """
    try:
        w = whois.whois(domain)
        # 如果有注册信息，说明已被注册
        return w.registrar is None
    except Exception:
        # 查询失败，可能可用
        return True

def batch_check(domains):
    """
    批量检查域名
    """
    available = []
    for domain in domains:
        if check_domain_availability(domain):
            available.append(domain)
            print(f"✓ {domain} 可用")
        else:
            print(f"✗ {domain} 已注册")
    return available
```

---

## 品牌域名策略

### 多域名保护

```markdown
核心域名：
- 主域名：brand.com
- 本地域名：brand.cn, brand.com.cn

防御注册：
- 常见拼写错误：branb.com
- 其他顶级域名：brand.net, brand.org
- 负面词汇：brandsucks.com

子域名规划：
- www.brand.com - 官网
- app.brand.com - 应用
- api.brand.com - API
- docs.brand.com - 文档
```

### 国际化域名

```markdown
多语言策略：
- 英语：globalbrand.com
- 中文：品牌.com（punycode）
- 本地化：brand.jp, brand.de

注意事项：
- punycode域名在部分场景显示异常
- 考虑本地法律合规
- 域名争议处理机制
```

---

## 域名创意报告模板

```markdown
# 域名创意报告

## 项目背景
- 品牌/产品名称
- 业务领域
- 目标市场

## 创意方案

### 方案一：主推方案
- 域名：______
- 含义：______
- 优势：______
- 可用性：______

### 方案二：备选方案
- 域名：______
- 含义：______
- 优势：______
- 可用性：______

### 方案三：创新方案
- 域名：______
- 含义：______
- 优势：______
- 可用性：______

## 对比评估
| 维度 | 方案一 | 方案二 | 方案三 |
|------|--------|--------|--------|
| 记忆度 | ★★★★★ | ★★★★ | ★★★ |
| 相关性 | ★★★★★ | ★★★★ | ★★★★★ |
| 可用性 | ✓ | ✓ | ✓ |
| 价格 | ¥55/年 | ¥68/年 | ¥199/年 |

## 推荐建议
首选：方案一
理由：简短易记，品牌关联度高，价格合理
```

---

## 注意事项

```
建议：
- 提前注册保护
- 考虑商标冲突
- 检查历史记录
- 续费提醒设置

避免：
- 侵犯他人商标
- 使用敏感词汇
- 忽略国际化需求
- 选择难拼写的域名
```

---

## 相关技能

- `brand-guidelines` - 品牌指南
- `design-brainstorming` - 设计头脑风暴
- `market-research` - 市场调研