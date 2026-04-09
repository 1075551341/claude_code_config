---
name: google-workspace
description: 当需要操作Google Workspace服务、Gmail API、Google Drive、Google Sheets、Google Docs、Google Calendar时调用此技能。触发词：Google Workspace、Gmail、Google Drive、Google Sheets、Google Docs、Google Calendar、G Suite、谷歌办公套件。
---

# Google Workspace

## 核心能力

**Gmail、Drive、Sheets、Docs、Calendar API 操作与自动化。**

---

## 适用场景

- Gmail 自动化
- Google Drive 文件管理
- Google Sheets 数据处理
- Google Docs 文档生成
- Google Calendar 日程管理
- Workspace 集成开发

---

## API 认证

### OAuth 2.0

```javascript
const { google } = require('googleapis');

const auth = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI
);

auth.setCredentials({
  access_token: ACCESS_TOKEN,
  refresh_token: REFRESH_TOKEN
});
```

### Service Account

```python
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
  'service-account.json',
  scopes=['https://www.googleapis.com/auth/drive']
)
```

---

## Gmail API

### 发送邮件

```python
from googleapiclient.discovery import build

service = build('gmail', 'v1', credentials=creds)

message = {
  'raw': base64.urlsafe_b64encode(msg_bytes).decode()
}

service.users().messages().send(
  userId='me',
  body=message
).execute()
```

### 搜索邮件

```python
results = service.users().messages().list(
  userId='me',
  q='from:sender@example.com'
).execute()

messages = results.get('messages', [])
```

---

## Google Drive API

### 上传文件

```python
from googleapiclient.http import MediaFileUpload

media = MediaFileUpload('file.pdf', mimetype='application/pdf')

file = service.files().create(
  body={'name': 'file.pdf'},
  media_body=media
).execute()
```

### 下载文件

```python
request = service.files().get_media(fileId=file_id)
with open('local_file', 'wb') as f:
  f.write(request.execute())
```

### 搜索文件

```python
results = service.files().list(
  q="name contains 'report'",
  spaces='drive'
).execute()
```

---

## Google Sheets API

### 读取数据

```python
sheet = service.spreadsheets()

result = sheet.values().get(
  spreadsheetId=spreadsheet_id,
  range='Sheet1!A1:D10'
).execute()

values = result.get('values', [])
```

### 写入数据

```python
sheet.values().update(
  spreadsheetId=spreadsheet_id,
  range='Sheet1!A1',
  valueInputOption='RAW',
  body={'values': [['A1', 'B1', 'C1']]}
).execute()
```

### 批量更新

```python
requests = [
  {
    'updateCells': {
      'range': {'sheetId': 0},
      'rows': [{'values': [{'userEnteredValue': {'stringValue': 'value'}}]}]
    }
  }
]

service.spreadsheets().batchUpdate(
  spreadsheetId=id,
  body={'requests': requests}
).execute()
```

---

## Google Docs API

### 创建文档

```python
doc = service.documents().create(
  body={'title': 'New Document'}
).execute()

document_id = doc['documentId']
```

### 插入内容

```python
requests = [
  {
    'insertText': {
      'location': {'index': 1},
      'text': 'Hello World'
    }
  }
]

service.documents().batchUpdate(
  documentId=document_id,
  body={'requests': requests}
).execute()
```

---

## Google Calendar API

### 创建事件

```python
event = {
  'summary': 'Meeting',
  'start': {'dateTime': '2024-01-01T10:00:00'},
  'end': {'dateTime': '2024-01-01T11:00:00'}
}

service.events().insert(
  calendarId='primary',
  body=event
).execute()
```

### 查询事件

```python
events = service.events().list(
  calendarId='primary',
  timeMin='2024-01-01T00:00:00Z',
  maxResults=10
).execute()
```

---

## 注意事项

```
必须：
- 使用 OAuth 或 Service Account
- 处理 token 过期
- 限制 API 调用频率
- 处理分页结果

避免：
- 硬编码凭证
- 无限制调用（有配额）
- 忽略错误响应
- 单线程批量操作
```

---

## 相关技能

- `xlsx` - Excel 操作
- `docx` - Word 文档
- `report-generator` - 报告生成
- `api-development` - API 开发