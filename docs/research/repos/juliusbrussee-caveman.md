# JuliusBrussee/caveman v1.8.2

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-06-16

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
