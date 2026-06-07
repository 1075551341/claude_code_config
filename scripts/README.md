# `.claude\scripts` 工具说明

本目录存放 Claude Code 环境维护与辅助脚本（PowerShell）。默认在 **Windows** 下通过 `powershell -ExecutionPolicy Bypass -File <脚本名>` 执行。

关闭claude和node进程
Get-Process | Where-Object { $_.Name -like "*claude*" } | Stop-Process -Force
Get-Process | Where-Object { $_.Name -like "_node_" } | Stop-Process -Force

---

## 同步与验证（多编辑器）

### 已同步的编辑器（按本机实际目录）

| 编辑器   | 用户目录示例              | 说明             |
| -------- | ------------------------- | ---------------- |
| Cursor   | `%USERPROFILE%\.cursor`   | 若存在则参与同步 |
| Trae     | `%USERPROFILE%\.trae`     | 若存在则参与同步 |
| Windsurf | `%USERPROFILE%\.windsurf` | 若存在则参与同步 |
| Qoder    | `%USERPROFILE%\.qoder`    | 若不存在则跳过   |

### 同步的配置组件（v14 双模式）

**索引模式（默认）**：

- **总纲**（7 文件软链接）：`CLAUDE.md`、`CLAUDE-ROUTER.mdc`、`SPEC.md`、`MANIFEST.yaml`、`*-INDEX.md`
- **资产**（目录联接）：`skills/`、`agents/`、`rules/` → `~\.claude\`

**全量模式（`-Full`）**：

- 以上全部 + `agents/` 联接
- **额外格式转换**：`rules/` → 编辑器原生 `.mdc`/`.md`；`skills/` → `skills-native/<name>/SKILL.md`

**永不同步（Claude Code 专用，仅保留在 `~/.claude`）**：`hooks/`、`scripts/`、`commands/`、`plugins/`、`.mcp.json`、`settings.json`

**索引模式资产**：
- `skills/`、`agents/` → 目录联接
- `rules/` → 编辑器实体目录：各 `.md` 单文件软链接 + `00-CLAUDE-ROUTER` 必加载副本（**不写回** `~/.claude/rules/`）

**复制/链接同步的文件**：
- 7 总纲文件 → 文件软链接（含 `CLAUDE-ROUTER.mdc`）

**不同步的配置（Claude Code 与编辑器隔离）**：

| 文件/目录 | 位置 | 说明 |
|-----------|------|------|
| `settings.json` | 仅 `~/.claude` | CLI hooks/permissions/model |
| `.mcp.json` | 仅 `~/.claude` | MCP 权威源 |
| `hooks/` | 仅 `~/.claude` | 生命周期钩子 |

> **`sync.ps1` 不改** 上述 Claude Code 配置。编辑器 `settings.json` 的 `env.CLAUDE_IN_EDITOR` 由 **`fix.ps1 -Fix`** 单独写入（Hook 环境哨兵，与内容同步无关）。

### 同步特点

- 单向：只读 `~/.claude`，写入各 `~/.<editor>/`
- 管理员用符号链接；非管理员目录用 Junction
- 强制重建：`sync.ps1 -Force`；预览：`sync.ps1 -DryRun`

### 同步后建议自测

1. 在各编辑器中确认配置可读、无报错
2. **确认字体、字号、颜色主题、缩放等未异常**（若 settings 为严格 JSON，仅合并 env；JSONC 时脚本会跳过写回）
3. 抽查技能、代理、规则是否生效
4. 确认 MCP 配置与本地服务一致
5. 确认不会在编辑器侧触发过长或循环 Hook

---

## 脚本一览

### `sync.ps1` — 将工具链同步到各编辑器（v14.0）

**索引模式（默认）**：

- 7 总纲文件 → 软链接
- `skills/`、`agents/` → 目录联接
- `rules/` → 编辑器实体目录（单文件链接 + 路由部署）
- 写入 `sync-mode.json`（`mode: index`）

**全量模式（`-Full`）**：

- 7 总纲 + `agents/` 联接
- `rules/` → 原生 `.mdc`/`.md`（`Sync-NativeRulesFiles`）
- `skills/` → `skills-native/` 原生 `SKILL.md`（`Sync-NativeSkillsFiles`）
- 写入 `sync-mode.json`（`mode: full`）

**切回索引**：`sync.ps1 -Force`（不带 `-Full`）

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File sync.ps1
powershell -ExecutionPolicy Bypass -File sync.ps1 -Full -Force
powershell -ExecutionPolicy Bypass -File sync.ps1 -DryRun
```

**参数**：

| 参数      | 说明                               |
| --------- | ---------------------------------- |
| `-Full`   | 全量模式（rules/skills 格式转换）  |
| `-Force`  | 强制重建链接/原生副本              |
| `-DryRun` | 仅预览，不写盘                     |

---

### `check.ps1` — 环境健康检查与评分（v3.2）

**作用**：检查目录结构、配置文件格式与安全、`~\.claude` 与各编辑器的链接状态、Hook 风险、Python/Node/Git/Docker 等运行时、（可选）MCP 相关依赖与连通性、工具箱统计，并输出得分与 `logs\check-YYYYMMDD.md` 报告。

**用法**：

```powershell
 powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\check.ps1
powershell -ExecutionPolicy Bypass -File check.ps1 -Quick   # 跳过 MCP 连通性相关检查，更快
```

**参数**：

| 参数     | 说明                |
| -------- | ------------------- |
| `-Quick` | 跳过 MCP 连通性测试 |

---

### `fix.ps1` — 修复编辑器内 Hook 超时/僵死（v5.0）

**作用**：部署 `~\.claude\hooks\_editor_hook_launcher.py`（**v2.0**），以 **GetConsoleWindow()** 为主判定：扩展宿主拉起的 Python **无控制台**时快速跳过，仅输出 `{"continue":true}`；**真实终端**下仍经 launcher **转调**原 Hook，逻辑完整执行。同时将 `~\.claude\settings.json` 中各 Python Hook 命令改为 `python ...\_editor_hook_launcher.py <原脚本>`。

**`-Fix` 还会做**：删除各 `~\.<editor>\hooks` 的**陈旧软链接**；在 **用户目录与 Roaming** 的 `settings.json` 中合并 `env.CLAUDE_IN_EDITOR`（若解析失败则**跳过写回**以免覆盖字体/主题等）；移除 `terminal.integrated.env.windows.CLAUDE_IN_EDITOR`；更新 `.<editor>ignore`。

**用法**：

```powershell
# 诊断（launcher、Hook 命令格式、CLAUDE_IN_EDITOR、陈旧 hooks 链接）
powershell -ExecutionPolicy Bypass -File fix.ps1

# 应用修复（部署 launcher、改写 Hook 命令、环境哨兵）
 powershell -ExecutionPolicy Bypass -File C:\Users\dell\.claude\scripts\fix.ps1 -Fix

# 撤销（Hook 恢复为直接 python，见脚本说明）
powershell -ExecutionPolicy Bypass -File fix.ps1 -Restore
```

**参数**：

| 参数       | 说明                                  |
| ---------- | ------------------------------------- |
| `-Fix`     | 应用修复                              |
| `-Restore` | 从 settings.json 中移除 launcher 包装 |

> **注意**：`-Fix` 后请**完全退出并重启**各编辑器。Hook 环境变量请用 `fix.ps1 -Fix` 维护，与 `sync.ps1` 内容同步无关。

---

### `collect-experience.ps1` — 开发经验收集

**作用**：从 Git 历史等抽取信息，在 `~\.claude\experiences` 下生成当日经验 Markdown 摘要。

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File collect-experience.ps1
powershell -ExecutionPolicy Bypass -File collect-experience.ps1 "D:\path\to\project"
```

---

### `search-github-tools.ps1` — GitHub 工具检索

**作用**：按分类搜索 GitHub 热门仓库并与本地 `skills` 等对比，可选保存报告。建议配置环境变量 `GITHUB_TOKEN` 提高 API 限额。

**用法**：

```powershell
powershell -ExecutionPolicy Bypass -File search-github-tools.ps1
powershell -ExecutionPolicy Bypass -File search-github-tools.ps1 -Category all -SaveReport
```

---

## 典型工作流

### 首次配置或修改后

```powershell
# 1. 修复 hooks（部署 launcher + 改写 settings 中 Hook 命令，防止编辑器内僵死）
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Fix

# 2. 重新同步（只同步 4 项：skills/ agents/ rules/ + CLAUDE.md）
powershell -ExecutionPolicy Bypass -File .claude\scripts\sync.ps1

# 3. 重启编辑器，验证不再僵死
```

### 日常维护

1. 修改 `~\.claude` 下技能、规则后执行 `sync.ps1`
2. 发现编辑器异常时先运行 `fix.ps1` 诊断
3. 定期执行 `check.ps1` 做环境体检

### 已验证现状

1. Cursor 会直接加载 `~\.claude\settings.json`（用户级 Claude 配置），因此执行日志里出现 `~\.claude\hooks\*.py` 属正常，**不代表** `sync.ps1` 把 `hooks/` 链到了编辑器目录。
2. **launcher v2.0** 以无控制台（编辑器）与有控制台（CLI）区分；IDE 侧成功跳过时 Hook 耗时多在 **约 30–60ms** 量级。
3. 若日志里**同一脚本**时而毫秒级、时而数秒，多为子进程环境差异；请对照 Cursor **Hooks 执行记录**，并确认 `%APPDATA%\Cursor\User\settings.json` 中 `env.CLAUDE_IN_EDITOR` 仍存在，且 `terminal.integrated.env.windows` 中**没有**残留同名变量。

### 如需撤销 launcher 包装

```powershell
powershell -ExecutionPolicy Bypass -File .claude\scripts\fix.ps1 -Restore
```

---

## 说明

- 脚本内注释与界面文案以中文为主；部分技术字段名（如 JSON 键名）保持英文。
- `sync.ps1`、`fix.ps1` 源文件使用 **UTF-8（含 BOM）** 保存，便于 Windows PowerShell 5.1 正确解析中文；若 CMD/旧控制台仍显示乱码，可改用 **Windows Terminal** 或先执行 `chcp 65001`。
- 历史文件 `SYNC_RESULT.md` 已合并进本文档，不再单独维护。
- **文档与脚本版本对齐**：`sync.ps1` **v11.0**，`fix.ps1` **v5.0**（launcher + GetConsoleWindow），`check.ps1` **v3.2**；升级脚本后若 README 未提新版本号，以各 `.ps1` 文件头注释为准。
