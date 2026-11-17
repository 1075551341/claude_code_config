# 本端脚本与可选工具

- `check-config.py`：只读检查技能元数据、内部引用、入口、hook 工具覆盖/超时/示例一致性及可选 MCP 定义。数量只报告，不代表实际可用。
- `python-mcp.ps1`：本端 Python MCP 启动器，仅在选择相应可选定义时使用。

运行 `python scripts/check-config.py` 与 `python hooks/tests/test_hooks.py`。

默认项目 `.mcp.json` 和用户级 server map 均不启用增强服务。公共可选定义在本端 `mcp-configs/development.json`、debug / ops / fsaccess profiles；例如从项目目录使用 `claude --mcp-config <本端配置绝对路径> --strict-mcp-config`。先确认服务版本、实际依赖、工作目录、环境变量与授权，启动后核对 MCP 工具列表。按需选择一个相同能力的入口，不与插件重复启用。浏览器 UI 工具仅在用户显式要求后使用。

原有用户级 MCP 定义完整保存在 `mcp-configs/user-servers.private.json`（被 Git 忽略），其中包含旧记录及可能的认证环境变量；这是恢复资料，不能未经检查整份启用。缺 launcher 等异常条目先修正或选择单个服务。不要输出私有文件内容。项目级 scopes 与账号状态没有改动。

插件以 `claude plugin list` 的实际状态为准；本轮观察到登记的 18 项均禁用，部分文件路径已失效。保留登记供按需修复，不修改安装清单冒充安装成功。重叠流程插件在本端设置显式禁用，领域与工具插件需要时再核验可用性。

自检不访问其他工具的目录，不是运行验收。实际使用需在新原生会话中确认规则、技能、hooks 和所选工具的加载来源。
