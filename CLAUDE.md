# Claude 开发入口

@AGENTS.md

本目录只维护 Claude 本端配置。技能、角色和手动命令由 Claude 的原生机制发现。
不通过本目录向其他工具提供适配、软链接、启动器或同步服务。

- 用户规则正文在本端 `AGENTS.md`；按需参考不放进自动加载的 `rules/`。
- 本端 hooks 及启用状态以 `settings.json` 和实际加载结果为准。
- 用户级 MCP 与项目级 `.mcp.json` 是不同作用域，不把后者当全局登记。
- 增强工具按需启用；插件登记不等于实际安装或可用，核验原生列表和工具调用。
- 运行说明见 `docs/runtime.md`；自检不替代实际会话加载与行为验证。

本目录验证命令：

```text
python scripts/check-config.py
python hooks/tests/test_hooks.py
```
