---
name: theme-config
description: 当需要配置主题样式、设计暗色模式、配置Ant Design/Element Plus主题时调用此技能。触发词：主题配置、暗色模式、Dark Mode、主题定制、Ant Design主题、Element Plus主题、Tailwind主题、颜色主题、UI主题。
---

# 主题配置生成

生成前端主题配置文件。

## 使用方式

```
/theme-config <framework> [options]
```

**框架支持：**
- `antd` - Ant Design Vue/React
- `element` - Element Plus
- `tailwind` - Tailwind CSS
- `css` - 原生 CSS 变量

## Ant Design 主题

### Vue 3 配置

```typescript
// src/theme/antd.ts
import type { ThemeConfig } from 'ant-design-vue/es/config-provider/context'

export const lightTheme: ThemeConfig = {
  token: {
    // 品牌色
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',

    // 字体
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial',
    fontSize: 14,

    // 圆角
    borderRadius: 6,

    // 线框风格
    wireframe: false,
  },
  components: {
    Button: {
      borderRadius: 6,
      controlHeight: 36,
    },
    Input: {
      borderRadius: 6,
    },
    Card: {
      borderRadiusLG: 8,
    },
    Table: {
      headerBg: '#fafafa',
    },
  },
}

export const darkTheme: ThemeConfig = {
  token: {
    colorPrimary: '#177ddc',
    colorBgContainer: '#141414',
    colorBgElevated: '#1f1f1f',
    colorBorder: '#434343',
    colorText: 'rgba(255, 255, 255, 0.85)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
  },
  algorithm: theme.darkAlgorithm,
}
```

### 动态主题切换

```vue
<!-- App.vue -->
<template>
  <a-config-provider :theme="currentTheme">
    <router-view />
  </a-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { theme } from 'ant-design-vue'
import { useThemeStore } from '@/stores/theme'
import { lightTheme, darkTheme } from '@/theme/antd'

const themeStore = useThemeStore()

const currentTheme = computed(() => {
  return themeStore.isDark ? darkTheme : lightTheme
})

// 监听系统主题
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
mediaQuery.addEventListener('change', (e) => {
  themeStore.setTheme(e.matches ? 'dark' : 'light')
})
</script>
```

### 主题 Store

```typescript
// stores/theme.ts
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  // 切换主题
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  // 设置主题
  const setTheme = (theme: 'light' | 'dark') => {
    isDark.value = theme === 'dark'
  }

  // 持久化
  watch(isDark, (val) => {
    localStorage.setItem('theme', val ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', val)
  }, { immediate: true })

  return { isDark, toggleTheme, setTheme }
})
```

## Element Plus 主题

### SCSS 变量覆盖

```scss
// styles/element-variables.scss
@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  $colors: (
    'primary': (
      'base': #409eff,
    ),
    'success': (
      'base': #67c23a,
    ),
    'warning': (
      'base': #e6a23c,
    ),
    'danger': (
      'base': #f56c6c,
    ),
  ),
  $button: (
    'border-radius': 4px,
  ),
  $card: (
    'border-radius': 8px,
  ),
);

@use "element-plus/theme-chalk/src/index.scss" as *;
```

### CSS 变量方式

```typescript
// src/theme/element.ts
import { useDark, useToggle } from '@vueuse/core'

export const useElementTheme = () => {
  const isDark = useDark({
    selector: 'html',
    attribute: 'class',
    valueDark: 'dark',
    valueLight: 'light',
  })

  const toggleDark = useToggle(isDark)

  // 设置 CSS 变量
  const setCSSVariables = (vars: Record<string, string>) => {
    const root = document.documentElement
    Object.entries(vars).forEach(([key, value]) => {
      root.style.setProperty(`--el-${key}`, value)
    })
  }

  return { isDark, toggleDark, setCSSVariables }
}
```

## Tailwind CSS 主题

### 配置文件

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      // 品牌色
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },

      // 字体
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },

      // 圆角
      borderRadius: {
        '4xl': '2rem',
      },

      // 阴影
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
      },

      // 动画
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### 主题预设

```typescript
// src/theme/presets.ts
export const themePresets = {
  // 默认蓝色主题
  default: {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  },

  // 紫色主题
  purple: {
    primary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  },

  // 绿色主题
  green: {
    primary: '#10b981',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
  },

  // 暗色主题
  dark: {
    primary: '#6366f1',
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f8fafc',
  },
}
```

## 原生 CSS 变量主题

```css
/* styles/theme.css */
:root {
  /* 颜色 */
  --color-primary: #3b82f6;
  --color-primary-light: #60a5fa;
  --color-primary-dark: #2563eb;

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* 背景 */
  --color-bg: #ffffff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;

  /* 文字 */
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;

  /* 边框 */
  --color-border: #e2e8f0;
  --color-border-light: #f1f5f9;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* 字体 */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "Fira Code", monospace;

  /* 字号 */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 18px;
  --text-xl: 20px;

  /* 动画 */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}

/* 暗色主题 */
.dark {
  --color-bg: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;

  --color-text: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;

  --color-border: #334155;
  --color-border-light: #1e293b;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}
```

## 主题工具函数

```typescript
// utils/theme.ts
import Color from 'colorjs.io'

/**
 * 生成主题色变体
 */
export function generateColorVariants(baseColor: string) {
  const color = new Color(baseColor)

  return {
    50: color.lighten(0.9).toString(),
    100: color.lighten(0.8).toString(),
    200: color.lighten(0.6).toString(),
    300: color.lighten(0.4).toString(),
    400: color.lighten(0.2).toString(),
    500: baseColor,
    600: color.darken(0.1).toString(),
    700: color.darken(0.2).toString(),
    800: color.darken(0.3).toString(),
    900: color.darken(0.4).toString(),
  }
}

/**
 * 计算对比色
 */
export function getContrastColor(bgColor: string): string {
  const color = new Color(bgColor)
  const luminance = color.luminance
  return luminance > 0.5 ? '#000000' : '#ffffff'
}

/**
 * 混合颜色
 */
export function mixColors(color1: string, color2: string, ratio: number): string {
  const c1 = new Color(color1)
  const c2 = new Color(color2)
  return c1.mix(c2, ratio).toString()
}
```