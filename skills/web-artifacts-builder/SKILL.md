---
name: web-artifacts-builder
description: 当需要使用React+Tailwind构建复杂Web制品、创建多组件前端项目时调用此技能。触发词：Web制品、React制品、前端构建、Tailwind制品、shadcn/ui、多组件应用、React项目构建。
license: Complete terms in LICENSE.txt
---

# Web 制品构建

To build powerful frontend claude.ai artifacts, follow these steps:
1. Initialize the frontend repo
2. Develop your artifact by editing the generated code
3. Bundle all code into a single HTML file
4. Display artifact to user
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

VERY IMPORTANT: To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new React project:
```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

This creates a fully configured project with:
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS 3.4.1 with shadcn/ui theming system
- ✅ Path aliases (`@/`) configured
- ✅ 40+ shadcn/ui components pre-installed
- ✅ All Radix UI dependencies included
- ✅ Parcel configured for bundling

### Step 2: Develop Your Artifact

Edit the generated files.

### Step 3: Bundle to Single HTML File

```bash
bash scripts/bundle-artifact.sh
```

This creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined.

### Step 4: Share Artifact with User

Share the bundled HTML file in conversation.

### Step 5: Testing/Visualizing the Artifact (Optional)

Use available tools (including other Skills or built-in tools like Playwright or Puppeteer).

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components
