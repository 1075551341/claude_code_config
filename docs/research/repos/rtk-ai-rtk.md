# rtk-ai/rtk v0.42.4

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub Releases + 官网 双源

## 核心价值

- Shell 命令 60–90% token 压缩
- pre-rtk-rewrite hook 透明重写
- 输入侧压缩（与 caveman 输出侧互补）
- RTK 别名/宏系统

## 证据

- [GitHub rtk-ai/rtk](https://github.com/rtk-ai/rtk)
- 本地 hook 已注册

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| shell_token | `hooks/pre-rtk-rewrite.py` |
| RTK 文档 | `RTK.md` |

## 吸收决策

**采纳** — hook 已注册；与 caveman 互斥（输入 vs 输出）。

## 互博检查

- vs caveman：`[shell_token, output_token]` excludes 互斥

## v10.1 增量

- v0.42.1 版本维持；hook 接线已验收

## v10.2.1 增量（双源刷新 2026-06-19）

- 稳定版 **v0.42.4**（dev-0.43.0-rc 跟踪）；MANIFEST 已对齐，无动作
- 范围提醒：hook 仅拦截 Bash 工具；Read/Grep/Glob 内置工具不经 RTK，需显式 `rtk read/grep/find`
