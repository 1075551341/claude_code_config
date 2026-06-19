# JuliusBrussee/caveman v1.9.0

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub + 官网 + npm 双源

## 核心价值

- 输出 ~75% token 压缩
- lite/full/ultra/wenyan 四档
- Agent 响应压缩（与 RTK 输入侧互补）
- caveman-compress skill 按需触发

## 证据

- [GitHub JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| output_token | `skills/caveman-compress/SKILL.md` |

## 吸收决策

**采纳** — skill 按需 L3；与 RTK hook 互斥。

## 互博检查

- vs RTK：`excludes: [hook/pre-rtk-rewrite]` 对称

## v10.1 增量

- v1.8.2 维持；无 breaking

## v10.2.1 增量（双源刷新 2026-06-19）

- **v1.9.0** (2026-06-12)；六档（lite/full/ultra + wenyan ×3）
- **F3**：`caveman-shrink` MCP 中间件可压缩任意 MCP server 工具描述 → 服务 x1xhlol 描述密度目标；**catalog 记录，不默认接入**（v10.3 backlog 评估）
- `caveman-compress` 压 CLAUDE.md 输入侧 ~46%（代码/URL/路径字节保留）
