---
name: report-generator
description: 当需要生成报告文档、制作分析报告、输出Markdown/PDF/Word报告时调用此技能。触发词：报告生成、文档生成、分析报告、Markdown报告、报告输出、报告模板、日报生成、周报生成。
---

# 报告文档生成

生成各类报告文档。

## 使用方式

```
/report-generator <type> [options]
```

**类型说明：**
- `markdown` - Markdown 格式
- `pdf` - PDF 文档
- `word` - Word 文档
- `html` - HTML 报告

## Markdown 报告

### 基础模板

```typescript
// utils/report/markdown.ts

interface ReportOptions {
  title: string
  subtitle?: string
  author?: string
  date?: Date
  sections: ReportSection[]
}

interface ReportSection {
  title: string
  content: string
  subsections?: ReportSection[]
}

export function generateMarkdownReport(options: ReportOptions): string {
  const lines: string[] = []

  // 标题
  lines.push(`# ${options.title}`)
  lines.push('')

  // 元信息
  if (options.subtitle) {
    lines.push(`**${options.subtitle}**`)
    lines.push('')
  }

  if (options.author || options.date) {
    const meta = []
    if (options.author) meta.push(`作者: ${options.author}`)
    if (options.date) meta.push(`日期: ${formatDate(options.date)}`)
    lines.push(meta.join(' | '))
    lines.push('')
  }

  lines.push('---')
  lines.push('')

  // 目录
  lines.push('## 目录')
  lines.push('')
  options.sections.forEach((section, i) => {
    lines.push(`${i + 1}. [${section.title}](#${slugify(section.title)})`)
  })
  lines.push('')

  // 正文
  options.sections.forEach((section) => {
    lines.push(renderSection(section))
  })

  // 页脚
  lines.push('---')
  lines.push('')
  lines.push(`*生成时间: ${formatDate(new Date())}*`)

  return lines.join('\n')
}

function renderSection(section: ReportSection, level = 2): string {
  const lines: string[] = []

  lines.push(`${'#'.repeat(level)} ${section.title}`)
  lines.push('')
  lines.push(section.content)
  lines.push('')

  if (section.subsections) {
    section.subsections.forEach((sub) => {
      lines.push(renderSection(sub, level + 1))
    })
  }

  return lines.join('\n')
}
```

### 数据表格

```typescript
// utils/report/tables.ts

interface TableData {
  headers: string[]
  rows: any[][]
}

export function renderMarkdownTable(data: TableData): string {
  const lines: string[] = []

  // 表头
  lines.push(`| ${data.headers.join(' | ')} |`)
  lines.push(`| ${data.headers.map(() => '---').join(' | ')} |`)

  // 数据行
  data.rows.forEach((row) => {
    lines.push(`| ${row.join(' | ')} |`)
  })

  return lines.join('\n')
}

// 使用示例
const table = renderMarkdownTable({
  headers: ['任务', '状态', '完成时间'],
  rows: [
    ['视频转码', '已完成', '2024-03-20 10:30'],
    ['图片压缩', '处理中', '-'],
    ['音频转换', '等待中', '-'],
  ],
})
```

## PDF 报告

### 使用 PDFKit

```typescript
// utils/report/pdf.ts
import PDFDocument from 'pdfkit'
import fs from 'fs'

interface PdfReportOptions {
  title: string
  subtitle?: string
  author?: string
  content: string
  outputPath: string
}

export async function generatePdfReport(options: PdfReportOptions): Promise<void> {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: 'A4',
      margins: { top: 50, bottom: 50, left: 50, right: 50 },
    })

    const stream = fs.createWriteStream(options.outputPath)
    doc.pipe(stream)

    // 字体设置（支持中文）
    doc.registerFont('SourceHanSans', 'fonts/SourceHanSansCN-Regular.ttf')
    doc.font('SourceHanSans')

    // 标题
    doc.fontSize(24).text(options.title, { align: 'center' })
    doc.moveDown()

    // 副标题
    if (options.subtitle) {
      doc.fontSize(14).text(options.subtitle, { align: 'center' })
      doc.moveDown()
    }

    // 元信息
    const meta = []
    if (options.author) meta.push(`作者: ${options.author}`)
    meta.push(`日期: ${formatDate(new Date())}`)

    doc.fontSize(10).text(meta.join(' | '), { align: 'center' })
    doc.moveDown(2)

    // 分割线
    doc.moveTo(50, doc.y).lineTo(doc.page.width - 50, doc.y).stroke()
    doc.moveDown()

    // 正文
    doc.fontSize(12).text(options.content, {
      align: 'left',
      lineGap: 6,
    })

    // 页脚
    const pages = doc.bufferedPageRange()
    for (let i = 0; i < pages.count; i++) {
      doc.switchToPage(i)
      doc.fontSize(8)
        .text(
          `第 ${i + 1} 页 / 共 ${pages.count} 页`,
          50,
          doc.page.height - 30,
          { align: 'center' }
        )
    }

    doc.end()

    stream.on('finish', resolve)
    stream.on('error', reject)
  })
}
```

### 使用 Puppeteer（HTML 转 PDF）

```typescript
// utils/report/pdf-html.ts
import puppeteer from 'puppeteer'

export async function htmlToPdf(html: string, outputPath: string): Promise<void> {
  const browser = await puppeteer.launch()
  const page = await browser.newPage()

  await page.setContent(html, { waitUntil: 'networkidle0' })

  await page.pdf({
    path: outputPath,
    format: 'A4',
    margin: { top: '20mm', bottom: '20mm', left: '15mm', right: '15mm' },
    printBackground: true,
  })

  await browser.close()
}
```

## Word 报告

### 使用 docx

```bash
pnpm add docx
```

```typescript
// utils/report/word.ts
import { Document, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel } from 'docx'

interface WordReportOptions {
  title: string
  subtitle?: string
  author?: string
  sections: { title: string; content: string }[]
  tables?: TableData[]
}

export async function generateWordReport(options: WordReportOptions): Promise<Buffer> {
  const children: Paragraph[] = []

  // 标题
  children.push(
    new Paragraph({
      text: options.title,
      heading: HeadingLevel.TITLE,
      alignment: 'center',
    })
  )

  // 副标题
  if (options.subtitle) {
    children.push(
      new Paragraph({
        text: options.subtitle,
        alignment: 'center',
      })
    )
  }

  // 作者和日期
  children.push(
    new Paragraph({
      children: [
        new TextRun({ text: `作者: ${options.author || '系统生成'}` }),
        new TextRun({ text: '    ' }),
        new TextRun({ text: `日期: ${formatDate(new Date())}` }),
      ],
      alignment: 'center',
    })
  )

  children.push(new Paragraph({ text: '' })) // 空行

  // 各章节
  options.sections.forEach((section) => {
    children.push(
      new Paragraph({
        text: section.title,
        heading: HeadingLevel.HEADING_1,
      })
    )

    children.push(
      new Paragraph({
        text: section.content,
      })
    )

    children.push(new Paragraph({ text: '' }))
  })

  // 表格
  options.tables?.forEach((table) => {
    children.push(new Paragraph({ text: '' }))
    // 表格渲染逻辑...
  })

  const doc = new Document({
    sections: [{ children }],
  })

  return await doc.toBuffer()
}
```

## HTML 报告

### 模板引擎

```typescript
// utils/report/html.ts
import ejs from 'ejs'

interface HtmlReportOptions {
  title: string
  subtitle?: string
  data: any
  template: string
}

export async function generateHtmlReport(options: HtmlReportOptions): Promise<string> {
  const template = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><%= title %></title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px 20px;
    }
    .header { text-align: center; margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
    .header h1 { font-size: 28px; margin-bottom: 10px; }
    .header .meta { color: #666; font-size: 14px; }
    .section { margin-bottom: 30px; }
    .section h2 { font-size: 20px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #1890ff; }
    .section p { margin-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
    th { background: #f5f5f5; font-weight: 600; }
    tr:hover { background: #fafafa; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px; }
    .chart { margin: 20px 0; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .badge-success { background: #f6ffed; color: #52c41a; }
    .badge-warning { background: #fffbe6; color: #faad14; }
    .badge-error { background: #fff2f0; color: #ff4d4f; }
  </style>
</head>
<body>
  <div class="header">
    <h1><%= title %></h1>
    <% if (subtitle) { %>
    <p><%= subtitle %></p>
    <% } %>
    <p class="meta">生成时间: <%= new Date().toLocaleString('zh-CN') %></p>
  </div>

  <% sections.forEach((section, index) => { %>
  <div class="section">
    <h2><%= index + 1 %>. <%= section.title %></h2>
    <%= section.content %>
  </div>
  <% }); %>

  <div class="footer">
    <p>此报告由系统自动生成</p>
  </div>
</body>
</html>
  `

  return ejs.render(template, options)
}
```

## 报告模板

### 任务统计报告

```typescript
// reports/task-stats.ts

interface TaskStatsReport {
  period: { start: Date; end: Date }
  tasks: Task[]
  stats: {
    total: number
    completed: number
    failed: number
    avgDuration: number
  }
}

export async function generateTaskStatsReport(data: TaskStatsReport): Promise<string> {
  const sections = [
    {
      title: '概览',
      content: renderMarkdownTable({
        headers: ['指标', '数值'],
        rows: [
          ['任务总数', data.stats.total],
          ['完成数', data.stats.completed],
          ['失败数', data.stats.failed],
          ['平均耗时', `${data.stats.avgDuration}ms`],
        ],
      }),
    },
    {
      title: '任务列表',
      content: renderMarkdownTable({
        headers: ['ID', '类型', '状态', '耗时'],
        rows: data.tasks.slice(0, 20).map((t) => [
          t.id.slice(0, 8),
          t.type,
          t.status,
          `${t.duration}ms`,
        ]),
      }),
    },
  ]

  return generateMarkdownReport({
    title: '任务统计报告',
    subtitle: `${formatDate(data.period.start)} - ${formatDate(data.period.end)}`,
    sections,
  })
}
```

### 性能分析报告

```typescript
// reports/performance.ts

export async function generatePerformanceReport(data: PerformanceData): Promise<string> {
  const html = await generateHtmlReport({
    title: '性能分析报告',
    subtitle: `分析周期: ${formatDate(data.period.start)} - ${formatDate(data.period.end)}`,
    sections: [
      {
        title: '响应时间分布',
        content: renderChart(data.responseTimes),
      },
      {
        title: '慢请求分析',
        content: renderMarkdownTable({
          headers: ['接口', '平均耗时', '调用次数', 'P99'],
          rows: data.slowApis.map((api) => [
            api.path,
            `${api.avgTime}ms`,
            api.count,
            `${api.p99}ms`,
          ]),
        }),
      },
      {
        title: '错误统计',
        content: renderMarkdownTable({
          headers: ['错误码', '次数', '占比'],
          rows: data.errors.map((e) => [e.code, e.count, `${e.percent}%`]),
        }),
      },
    ],
  })

  return html
}
```

## 图表嵌入

```typescript
// utils/report/charts.ts
import { ChartJSNodeCanvas } from 'chartjs-node-canvas'

export async function generatePieChart(data: { label: string; value: number }[]): Promise<Buffer> {
  const chartCanvas = new ChartJSNodeCanvas({ width: 400, height: 300 })

  const config = {
    type: 'pie',
    data: {
      labels: data.map((d) => d.label),
      datasets: [{
        data: data.map((d) => d.value),
        backgroundColor: ['#1890ff', '#52c41a', '#faad14', '#ff4d4f'],
      }],
    },
  }

  return chartCanvas.renderToBuffer(config)
}
```