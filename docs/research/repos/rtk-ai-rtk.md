# rtk-ai/rtk v0.42.1

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-06-16

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
