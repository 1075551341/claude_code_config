# Cursor local plugin — Claude Config Rules

> SSOT 源：`~/.claude/rules/*.md` + `CLAUDE-ROUTER.mdc` + Guard `CURSOR-EDITOR.mdc`
> 安装位置：`~/.cursor/plugins/local/claude-config`（**实体目录 + 实体 .mdc**，由 `sync.ps1` 从 SSOT 复制）
> **不写入业务项目**。

## 为何必须是实体文件

Cursor 插件质量门禁要求规则路径留在插件目录内，禁止外链/`..`。
Settings → User 也不枚举 `~/.cursor/rules` 文件；全局 `.mdc` 的可见通道是 **已安装插件规则**（与 `exa-awareness` 同级）。

因此：skills/agents 仍可 Junction；**插件 rules 必须 Copy**。

## 验证

1. `dir ~/.cursor/plugins/local/claude-config/rules` → 14 个真实 `.mdc`（非 SYMLINK）
2. `plugin.json` 含 `"rules": "./rules/"`
3. **完全退出 Cursor 再打开**（仅 Reload 有时不重新扫描 local plugins）→ Settings → Rules → User 应出现 CORE / ROUTER / …
