/**
 * @描述 ESLint 9 flat config 模板 — 仅代码质量，不含风格规则
 * @原则 prettier 管格式，eslint 管质量，互不混淆
 * @范围 JS/TS 基线 + 预设注释（React hooks / Vue essential / Angular）
 * @使用 拷贝到项目根目录 → 安装依赖 → 按需取消注释框架段
 *
 * @依赖基线（必装）
 *   pnpm add -D eslint @eslint/js typescript-eslint eslint-config-prettier globals
 *
 * @依赖 React（取消注释前安装）
 *   pnpm add -D eslint-plugin-react-hooks
 *
 * @依赖 Vue（取消注释前安装）
 *   pnpm add -D eslint-plugin-vue
 *
 * @依赖 Angular（取消注释前安装）
 *   pnpm add -D @angular-eslint/eslint-plugin
 */

import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettierConfig from 'eslint-config-prettier';
import globals from 'globals';

export default tseslint.config(
  // ─── 全局忽略 ───
  {
    ignores: [
      'node_modules/',
      'dist/',
      'build/',
      'out/',
      'coverage/',
      '*.min.js',
      '*.min.mjs',
      '.next/',
      '.nuxt/',
      '.output/',
      '.turbo/',
    ],
  },

  // ─── 基线推荐（仅 bug-catching，无风格规则）───
  js.configs.recommended,
  ...tseslint.configs.recommended,

  // ─── Prettier 兼容（关闭所有冲突规则）───
  prettierConfig,

  // ─── JS/TS 通用规则 ───
  {
    files: ['**/*.{js,mjs,cjs,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2022,
      },
    },
    rules: {
      // ── 影响代码运行的规则（error 级）──
      'no-undef': 'error',
      'no-cond-assign': 'error',
      'no-constant-condition': 'error',
      'no-dupe-keys': 'error',
      'no-duplicate-case': 'error',
      'no-empty': ['error', { allowEmptyCatch: true }],
      'no-ex-assign': 'error',
      'no-irregular-whitespace': 'error',
      'no-sparse-arrays': 'error',
      'no-unreachable': 'error',
      'use-isnan': 'error',
      'valid-typeof': 'error',

      // ── TS 接管（关闭原生，启用 TS 版）──
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      'no-redeclare': 'off',
      '@typescript-eslint/no-redeclare': 'error',

      // ── 仅警告（不阻断构建）──
      'no-debugger': 'warn',
      'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],

      // ── 关闭风格规则（交给 prettier）──
      'no-mixed-spaces-and-tabs': 'off',
      'no-multi-spaces': 'off',
      'no-trailing-spaces': 'off',
      'no-multiple-empty-lines': 'off',
      'quotes': 'off',
      'semi': 'off',
      'indent': 'off',
      'comma-dangle': 'off',
      'object-curly-spacing': 'off',
      'arrow-parens': 'off',
      'operator-linebreak': 'off',
    },
  },

  // ─── React hooks（启用步骤）───
  // 1. 顶部添加: import reactHooks from 'eslint-plugin-react-hooks';
  // 2. 安装依赖: pnpm add -D eslint-plugin-react-hooks
  // 3. 取消下方注释
  // {
  //   files: ['**/*.{jsx,tsx}'],
  //   plugins: {
  //     'react-hooks': reactHooks,
  //   },
  //   rules: {
  //     'react-hooks/rules-of-hooks': 'error',
  //     'react-hooks/exhaustive-deps': 'warn',
  //   },
  // },

  // ─── Vue essential（启用步骤）───
  // 1. 顶部添加: import vuePlugin from 'eslint-plugin-vue';
  // 2. 安装依赖: pnpm add -D eslint-plugin-vue
  // 3. 取消下方注释
  // ...vuePlugin.configs['flat/essential'],
  // {
  //   files: ['**/*.vue'],
  //   rules: {
  //     'vue/no-undef-components': 'error',
  //     'vue/no-template-syntax-error': 'error',
  //     'vue/no-syntax-error': 'error',
  //   },
  // },

  // ─── Angular（启用步骤）───
  // 1. 顶部添加: import angular from '@angular-eslint/eslint-plugin';
  // 2. 安装依赖: pnpm add -D @angular-eslint/eslint-plugin
  // 3. 取消下方注释
  // {
  //   files: ['**/*.ts'],
  //   plugins: {
  //     '@angular-eslint': angular,
  //   },
  //   rules: {
  //     '@angular-eslint/no-undecorated-base-class': 'error',
  //     '@angular-eslint/use-lifecycle-interface': 'warn',
  //   },
  // },
);
