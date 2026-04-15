---
name: api-testing
description: 测试API接口、执行接口测试、验证API响应
triggers: [API测试, 接口测试, API调试, Postman, curl测试, 接口验证]
---

# API 测试

## 核心能力

**API接口测试、请求调试、响应验证。**

---

## 适用场景

- API 接口测试
- 接口调试
- 响应验证
- 接口文档验证

---

## HTTP 方法

| 方法 | 用途 | 幂等性 |
|------|------|--------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 全量更新 | 是 |
| PATCH | 部分更新 | 否 |
| DELETE | 删除资源 | 是 |

---

## curl 命令

### 基本请求

```bash
# GET
curl https://api.example.com/users

# POST
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

# PUT
curl -X PUT https://api.example.com/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'

# DELETE
curl -X DELETE https://api.example.com/users/1
```

### 常用选项

```bash
# 添加请求头
-H "Authorization: Bearer token"

# 发送数据
-d '{"key": "value"}'

# 显示响应头
-i 或 --include

# 显示详细信息
-v 或 --verbose

# 保存输出
-o output.json

# 跟随重定向
-L

# 超时设置
--max-time 30
```

---

## Postman 使用

### 请求配置

```
1. 选择方法 (GET/POST/PUT/DELETE)
2. 输入URL
3. 设置Headers
4. 配置Body (JSON/Form/RAW)
5. 设置认证方式
6. 发送请求
```

### 环境变量

```javascript
// 设置变量
pm.environment.set("token", "xxx");

// 获取变量
const token = pm.environment.get("token");

// 动态变量
{{$guid}}       // GUID
{{$timestamp}}  // 时间戳
{{$randomInt}}  // 随机数
```

### 测试脚本

```javascript
// 状态码验证
pm.test("状态码为200", function () {
    pm.response.to.have.status(200);
});

// 响应时间验证
pm.test("响应时间小于200ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(200);
});

// JSON验证
pm.test("返回正确数据", function () {
    const json = pm.response.json();
    pm.expect(json.success).to.be.true;
});

// 自动提取token
const json = pm.response.json();
pm.environment.set("token", json.data.token);
```

---

## Python 测试

### requests 库

```python
import requests

# GET
response = requests.get('https://api.example.com/users', 
    headers={'Authorization': 'Bearer token'}
)

# POST
response = requests.post('https://api.example.com/users',
    json={'name': 'John'},
    headers={'Content-Type': 'application/json'}
)

# 检查响应
assert response.status_code == 200
data = response.json()
```

### pytest 测试用例

```python
import pytest
import requests

BASE_URL = 'https://api.example.com'

class TestUserAPI:
    def test_get_users(self):
        response = requests.get(f'{BASE_URL}/users')
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_create_user(self):
        data = {'name': 'Test', 'email': 'test@example.com'}
        response = requests.post(f'{BASE_URL}/users', json=data)
        assert response.status_code == 201
        assert response.json()['name'] == 'Test'
    
    def test_update_user(self):
        data = {'name': 'Updated'}
        response = requests.put(f'{BASE_URL}/users/1', json=data)
        assert response.status_code == 200
```

---

## 响应验证

### 状态码检查

| 状态码 | 含义 | 验证点 |
|--------|------|--------|
| 200 | 成功 | 响应正确 |
| 201 | 创建成功 | 资源已创建 |
| 400 | 请求错误 | 参数校验 |
| 401 | 未授权 | 认证失败 |
| 403 | 禁止访问 | 权限校验 |
| 404 | 未找到 | 资源不存在 |
| 500 | 服务器错误 | 异常处理 |

### 响应结构验证

```javascript
// 字段存在性
pm.test("包含必要字段", function () {
    const json = pm.response.json();
    pm.expect(json).to.have.property('data');
    pm.expect(json.data).to.have.property('id');
});

// 数据类型验证
pm.test("数据类型正确", function () {
    const json = pm.response.json();
    pm.expect(json.id).to.be.a('number');
    pm.expect(json.name).to.be.a('string');
});
```

---

## 注意事项

```
必须:
- 测试边界情况
- 验证错误处理
- 检查响应时间
- 测试认证授权

避免:
- 只测试成功场景
- 忽略错误响应
- 硬编码测试数据
- 遗漏参数校验
```

---

## 相关技能

- `api-development` - API 开发
- `testing-standards` - 测试规范
- `web-testing` - Web 测试