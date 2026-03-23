# 国际化（i18n）最佳实践

## 描述
前端国际化技能，涵盖 i18next/vue-i18n 的配置、翻译文件管理、
动态语言切换、日期/数字格式化和 RTL 支持。

## 触发条件
当需要实现多语言支持、翻译管理、本地化功能时使用。

## 技术选型

| 框架 | 推荐方案 | 特点 |
|------|----------|------|
| React | react-i18next | 生态最大，Hooks 友好 |
| Vue | vue-i18n | Vue 官方推荐，Composition API 支持 |
| Next.js | next-intl | App Router 原生支持，SSR 友好 |
| 通用 | i18next | 框架无关，可在任何 JS 环境使用 |

## React + i18next 配置

```typescript
// i18n.ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import Backend from 'i18next-http-backend'
import LanguageDetector from 'i18next-browser-languagedetector'

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'zh-CN',
    supportedLngs: ['zh-CN', 'en', 'ja'],
    interpolation: { escapeValue: false },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  })

export default i18n
```

## 翻译文件结构

```
locales/
├── zh-CN/
│   ├── common.json    # 公共翻译
│   ├── auth.json      # 认证模块
│   └── dashboard.json # 仪表盘模块
├── en/
│   ├── common.json
│   ├── auth.json
│   └── dashboard.json
└── ja/
    └── ...
```

## 使用示例

```tsx
import { useTranslation } from 'react-i18next'

function Welcome() {
  const { t, i18n } = useTranslation('common')

  return (
    <div>
      <h1>{t('welcome', { name: '用户' })}</h1>
      <button onClick={() => i18n.changeLanguage('en')}>English</button>
      <button onClick={() => i18n.changeLanguage('zh-CN')}>中文</button>
    </div>
  )
}
```

## 最佳实践

1. **按模块拆分**：翻译文件按功能模块拆分，避免单文件过大
2. **Key 命名**：使用点分层级 `module.section.key`
3. **插值变量**：动态内容使用插值 `{{name}}`，不拼接字符串
4. **懒加载**：按语言和命名空间懒加载翻译文件
5. **类型安全**：使用 TypeScript 声明翻译 key 类型
6. **日期格式**：使用 Intl.DateTimeFormat 处理日期本地化
