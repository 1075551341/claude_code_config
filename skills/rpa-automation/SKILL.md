---
name: rpa-automation
description: 当需要实现RPA机器人流程自动化、自动化UI操作、自动化办公流程时调用此技能。触发词：RPA、流程自动化、UI自动化、机器人自动化、自动化办公、RPA开发、机器人流程。
---

# RPA 流程自动化

## 核心能力

**UI自动化、业务流程自动化、办公自动化。**

---

## 适用场景

- UI 自动化操作
- 业务流程自动化
- 数据录入自动化
- 办公效率提升

---

## Python RPA

### PyAutoGUI 鼠标键盘

```python
import pyautogui
import time

# 鼠标操作
pyautogui.moveTo(100, 100, duration=1)  # 移动
pyautogui.click()                        # 点击
pyautogui.doubleClick()                  # 双击
pyautogui.rightClick()                   # 右键
pyautogui.drag(100, 100, duration=1)     # 拖拽

# 键盘操作
pyautogui.write('Hello', interval=0.1)   # 输入文字
pyautogui.press('enter')                 # 按键
pyautogui.hotkey('ctrl', 'c')            # 组合键

# 截图
screenshot = pyautogui.screenshot()
location = pyautogui.locateOnScreen('button.png')
```

### Pywinauto Windows自动化

```python
from pywinauto import Application

# 启动应用
app = Application().start('notepad.exe')

# 连接已有应用
app = Application().connect(title='记事本')

# 操作窗口
window = app.window(title='无标题 - 记事本')
window.Edit.type_keys('Hello World', with_spaces=True)
window.MenuSelect('File->Save')
```

---

## Playwright 自动化

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # 导航
    page.goto('https://example.com')
    
    # 填写表单
    page.fill('#username', 'user')
    page.fill('#password', 'pass')
    page.click('#submit')
    
    # 等待
    page.wait_for_selector('.result')
    
    # 截图
    page.screenshot(path='screenshot.png')
    
    browser.close()
```

---

## 常见自动化场景

### Excel 自动化

```python
import openpyxl
from openpyxl.styles import Font

def fill_excel_template(template_path, data, output_path):
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    
    row = 2
    for item in data:
        ws.cell(row=row, column=1, value=item['name'])
        ws.cell(row=row, column=2, value=item['value'])
        row += 1
    
    wb.save(output_path)
```

### 邮件自动化

```python
import win32com.client

def send_outlook_email(to, subject, body, attachment=None):
    outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subject
    mail.Body = body
    if attachment:
        mail.Attachments.Add(attachment)
    mail.Send()
```

### 浏览器自动化

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get('https://example.com')

# 登录
driver.find_element(By.ID, 'username').send_keys('user')
driver.find_element(By.ID, 'password').send_keys('pass')
driver.find_element(By.ID, 'login').click()

# 等待页面加载
driver.implicitly_wait(10)

# 截图
driver.save_screenshot('page.png')

driver.quit()
```

---

## 错误处理

```python
import pyautogui
import time
import logging

def safe_click(image_path, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateOnScreen(image_path)
            if location:
                pyautogui.click(pyautogui.center(location))
                return True
        except Exception as e:
            logging.warning(f'查找失败: {e}')
        time.sleep(1)
    return False
```

---

## 流程编排

```python
class Workflow:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, action):
        self.steps.append({'name': name, 'action': action})
    
    def run(self):
        for step in self.steps:
            logging.info(f'执行: {step["name"]}')
            try:
                step['action']()
                logging.info(f'完成: {step["name"]}')
            except Exception as e:
                logging.error(f'失败: {step["name"]}, 错误: {e}')
                raise

# 使用
workflow = Workflow()
workflow.add_step('打开应用', lambda: pyautogui.doubleClick(100, 100))
workflow.add_step('输入数据', lambda: pyautogui.write('data'))
workflow.run()
```

---

## 注意事项

```
必须：
- 添加等待机制
- 处理异常情况
- 记录执行日志
- 保存截图证据

避免：
- 固定等待时间
- 忽略弹窗处理
- 缺少错误恢复
- 过快操作
```

---

## 相关技能

- `python-automation` - Python 自动化
- `web-testing` - Web 测试
- `scheduled-task` - 定时任务