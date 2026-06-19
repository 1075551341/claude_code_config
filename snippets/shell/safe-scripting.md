# 安全脚本模板

## 最小原则

```bash
#!/usr/bin/env bash
set -euo pipefail  # 严格模式：错误即退出，未定义变量报错，管道失败报错

# 避免：curl | bash（需用户确认）
# 避免：硬编码路径
# 使用：环境变量 + 参数化输入
```
