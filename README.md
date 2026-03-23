# Claude Code Configuration

这个仓库包含了 Claude Code 的全局配置、自定义代理 (Agents)、技能 (Skills)、规则 (Rules) 以及各种钩子脚本 (Hooks)。

## 目录结构

*   **`agents/`**: 自定义的 AI 代理配置文件，用于不同角色的专业任务（如前端开发、后端开发、代码审查等）。
*   **`hooks/`**: 各种生命周期钩子脚本，用于在执行任务前后自动运行一些检查或操作。
*   **`rules/`**: 针对不同场景（前端、后端、核心）的代码和行为规范。
*   **`scripts/`**: 实用的 PowerShell 和 Shell 脚本，用于同步工具、健康检查等。
*   **`skills/`**: Claude 可以调用的具体技能定义。
*   **`.claude.json` / `config.json` / `settings.json`**: Claude Code 的核心配置文件。
*   **`CLAUDE.md`**: 全局行为规范说明。

## 忽略的目录说明 (Gitignore)

为了保持仓库干净，以下运行产生的临时文件和状态信息不会被追踪：

*   `cache/` 和 `plugins/cache/`: 插件和运行时的缓存文件。
*   `logs/`, `history/`, `daily_summary/`, `telemetry/`: 运行日志、历史记录和每日总结。
*   `sessions/`, `tasks/`, `ide/`, `projects/`, `plans/`: 具体任务的执行状态、会话记录和项目规划记录。
*   各种 `.lock` 文件和 Python 缓存。
