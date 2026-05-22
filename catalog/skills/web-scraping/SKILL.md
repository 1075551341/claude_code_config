---
name: web-scraping
description: 爬取网页数据
triggers: [爬取网页数据, 采集网站信息, 提取网页内容, 自动化数据收集]
---

# 网络爬虫

## 核心能力

**网页数据爬取、信息提取、数据采集自动化。**

---

## 适用场景

- 网页数据采集
- 信息提取
- 数据监控
- 内容抓取

---

## Python 爬虫

### Requests + BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup

# 发送请求
headers = {'User-Agent': 'Mozilla/5.0 ...'}
response = requests.get('https://example.com', headers=headers)

# 解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 提取数据
titles = soup.find_all('h2', class_='title')
for title in titles:
    print(title.text.strip())
```

### Scrapy 框架

```python
import scrapy

class MySpider(scrapy.Spider):
    name = 'my_spider'
    start_urls = ['https://example.com']
    
    def parse(self, response):
        for item in response.css('.item'):
            yield {
                'title': item.css('h2::text').get(),
                'link': item.css('a::attr(href)').get(),
            }
        
        # 分页
        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

### Selenium

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://example.com')

# 等待加载
driver.implicitly_wait(10)

# 提取数据
elements = driver.find_elements(By.CSS_SELECTOR, '.item')
for el in elements:
    print(el.text)

driver.quit()
```

---

## Playwright 爬虫

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://example.com')
    
    # 等待元素
    page.wait_for_selector('.item')
    
    # 提取数据
    items = page.query_selector_all('.item')
    for item in items:
        title = item.inner_text()
        print(title)
    
    browser.close()
```

---

## 反爬处理

### 请求头设置

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://example.com',
}
```

### 代理设置

```python
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

response = requests.get(url, proxies=proxies)
```

### 延迟请求

```python
import time
import random

# 随机延迟
time.sleep(random.uniform(1, 3))
```

### Cookie 管理

```python
session = requests.Session()
session.get('https://example.com/login')
session.post('https://example.com/login', data=login_data)
response = session.get('https://example.com/data')
```

---

## 数据存储

### JSON

```python
import json

data = [{'title': 'A', 'url': '...'}, {'title': 'B', 'url': '...'}]
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### CSV

```python
import csv

with open('data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'url'])
    writer.writeheader()
    writer.writerows(data)
```

### SQLite

```python
import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        title TEXT,
        url TEXT
    )
''')
cursor.executemany('INSERT INTO items (title, url) VALUES (?, ?)', items)
conn.commit()
```

---

## 注意事项

```
必须：
- 遵守robots.txt
- 设置合理延迟
- 添加请求头
- 处理异常情况

避免：
- 过高请求频率
- 爬取敏感信息
- 忽略版权问题
- 泄露个人隐私
```

---

## 相关技能

- `data-analysis` - 数据分析
- `python-automation` - Python 自动化
- `deep-research` - 深度研究