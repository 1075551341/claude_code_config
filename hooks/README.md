# Hooks

默认仅注册四个本端 hook；不自动刷新图谱、不拦截会话结束，也不全局自动格式化。

- PreToolUse shell：`pre-bash-guard.py`，5 秒，拦截明显危险命令和禁止 Agent 执行的 Git 写操作。支持 Bash / PowerShell；尽力而为，不代替工具原生权限与用户确认。 Git 全局选项支持等号、分隔和带空格引号路径；扫描真实命令替换，同时区分单引号字面文本及 Bash / PowerShell 的转义符。该检查不执行输入，也不声称完整解析动态 shell。
- PreToolUse 编辑：`pre-encoding-snapshot.py`，5 秒，保存当前会话、调用与文件的 BOM/EOL 快照。
- PostToolUse 编辑：`post-encoding-check.py`、`post-secret-detector.py`，各 10 秒，编码及密钥风险仅提醒；风险输出仅含编辑文件序号、行号和固定风险类型，不回显路径、源行或部分值。输入无效或适用文件不可读时给脱敏“检查未完成”提示，仍检查其余文件并保持非阻断。
- 编辑匹配覆盖原生工具和名称含写动词的 MCP 工具；读取工具不启动这些 hook。包装调用或未知工具不能据此声称受保护。

编码状态保存在本端 `.state/encoding/`；每项使用独立哈希文件原子替换，不再共享读改写 JSON。快照最多保留 24 小时、1000 项。原生 `session_id` 与 `tool_use_id` 用于前后配对；缺少调用标识时只能按会话和路径尽力配对。测试可用 `CLAUDE_HOOK_STATE_DIR` 指向临时目录。

## 可选格式化

`post-edit-format.py` 不在全局注册。要启用时在项目自己的 Claude settings 中注册 PostToolUse command，timeout 30 秒，再确认项目的 Prettier、Ruff/Black 或 rustfmt 配置存在。Go 项目另需 `.claude/format.json` 中 `{"gofmt": true}`。不下载工具；没有项目格式配置即跳过，即使全局安装了 formatter。执行失败返回非阻断错误并报告退出码；详细诊断由用户直接运行项目 formatter 查看，避免回显可能含密钥的源内容。

## 验证

运行 `python hooks/tests/test_hooks.py`。测试只在临时目录写入样例、状态和模拟 formatter，不改用户项目，不执行样例中的危险命令。

新增 hook 要同步本端设置及示例，并验证工具匹配、超时单位、放行/拦截与敏感输出。只有危险命令防护使用 exit 2；其余失败须可见，不能伪称成功。

Git alias 检查限定于真实 Git 调用；配置查询、搜索和字面数据可放行，含禁令的 alias 定义或临时展开会拦截。动态 shell 与已有外部 alias 仍有检查边界。

密钥模式支持 JSON 引号字段；只有实际匹配值为明确占位符或完整环境引用时豁免，不因邻近 sample / TODO / env 免责。测试文件等既有排除范围保留；模式检测不是完整 DLP 保证。
