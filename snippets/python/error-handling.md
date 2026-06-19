# 错误处理模板

> 遵守 R16：禁止裸 `except:pass`，异常必须传播或显式处理

## 标准模式

```python
class AppError(Exception):
    """自定义错误基类，携带机器可读 code"""
    def __init__(self, message: str, code: str, context: dict | None = None):
        self.code = code
        self.context = context or {}
        super().__init__(message)

# 已知错误 → 业务码 + 友好提示
try:
    result = risky_operation()
except ValueError as e:
    raise AppError(f"操作失败: {e}", code="INVALID_INPUT", context={"input": str(e)})

# 未知错误 → 完整日志 + 通用错误码
try:
    result = external_call()
except Exception as e:
    logger.error("external_call 未知错误", exc_info=True, extra={"op": "external_call"})
    raise AppError("服务暂时不可用", code="INTERNAL_ERROR")
```

## 异步操作（必须 try/catch）

```python
async def fetch_data(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise AppError(f"请求失败: {url}", code="HTTP_ERROR", context={"url": url, "error": str(e)})
```
