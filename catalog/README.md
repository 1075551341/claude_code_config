# Catalog — 领域能力库

> 不全局加载；按需 `migrate-from-legacy.py --skill|--agent|--rule` 复制到项目 `.claude/`

## 规模

| 目录 | 数量 | 策略 |
|------|------|------|
| skills/ | 97 | 全栈 + 办公 + 移动端/3D 保留 |
| agents/ | 38 | 领域专家 + 语言 reviewer |
| rules/ | 15 | 语言/领域 lazy-load |

## 分层

```
P0 全局（../skills/ ../agents/ ../rules/）  ← 始终可用
P1 全栈（api/db/docker/frontend/backend/...）
P2 办公（docx/pdf/pptx/xlsx/google-workspace/...）
P3 移动端/3D（mini-program, uniapp, capacitor, d3-visualization, flutter, react-native...）
```

## 移动端/微信/3D 保留清单

mini-program, uniapp-development, capacitor-app, ios-simulator, android-development, flutter-development, react-native, mobile-ui, mobile-performance, mobile-deployment, d3-visualization

## 已删记录

见 `experiences/rejected/deletion-candidates.md`
