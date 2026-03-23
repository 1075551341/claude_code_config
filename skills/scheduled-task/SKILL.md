---
name: scheduled-task
description: 定时任务创建工具，支持 node-cron、node-schedule、Bull 队列调度
---

# 定时任务创建

生成定时任务和调度代码。

## 使用方式

```
/scheduled-task <type> [options]
```

**类型说明：**
- `cron` - Cron 表达式任务
- `interval` - 固定间隔任务
- `queue` - 队列调度任务

## node-cron 基础

### 安装

```bash
pnpm add node-cron
pnpm add @types/node-cron -D
```

### 基础用法

```typescript
// jobs/index.ts
import cron from 'node-cron'
import logger from '../utils/logger'

/**
 * Cron 表达式说明
 * ┌────────────── 秒 (可选)
 * │ ┌──────────── 分钟
 * │ │ ┌────────── 小时
 * │ │ │ ┌──────── 日期
 * │ │ │ │ ┌────── 月份
 * │ │ │ │ │ ┌──── 星期几
 * │ │ │ │ │ │
 * * * * * * *
 *
 * 示例:
 * 0 * * * *     - 每小时整点
 * 0 0 * * *     - 每天 0 点
 * 0 0 * * 0     - 每周日 0 点
 * 0 0 1 * *     - 每月 1 号 0 点
 * */5 * * * *   - 每 5 分钟
 * 0 9-17 * * *  - 每天 9-17 点整点
 */

// 存储任务引用
const jobs: Map<string, cron.ScheduledTask> = new Map()

/**
 * 注册定时任务
 */
export function registerJobs() {
  // 每天凌晨清理临时文件
  registerJob('cleanup-temp', '0 0 * * *', async () => {
    logger.info('开始清理临时文件...')
    await cleanupTempFiles()
  })

  // 每小时检查过期任务
  registerJob('check-expired', '0 * * * *', async () => {
    logger.info('检查过期任务...')
    await checkExpiredTasks()
  })

  // 每 5 分钟更新统计数据
  registerJob('update-stats', '*/5 * * * *', async () => {
    await updateStatistics()
  })

  // 每周一凌晨生成周报
  registerJob('weekly-report', '0 0 * * 1', async () => {
    logger.info('生成周报...')
    await generateWeeklyReport()
  })

  logger.info(`已注册 ${jobs.size} 个定时任务`)
}

/**
 * 注册单个任务
 */
function registerJob(name: string, schedule: string, handler: () => Promise<void>) {
  const task = cron.schedule(schedule, async () => {
    try {
      await handler()
    } catch (err) {
      logger.error(`任务执行失败: ${name}`, { error: (err as Error).message })
    }
  })

  jobs.set(name, task)
  logger.info(`注册定时任务: ${name} (${schedule})`)
}

/**
 * 停止任务
 */
export function stopJob(name: string) {
  const task = jobs.get(name)
  if (task) {
    task.stop()
    logger.info(`停止任务: ${name}`)
  }
}

/**
 * 启动任务
 */
export function startJob(name: string) {
  const task = jobs.get(name)
  if (task) {
    task.start()
    logger.info(`启动任务: ${name}`)
  }
}

/**
 * 停止所有任务
 */
export function stopAllJobs() {
  jobs.forEach((task, name) => {
    task.stop()
    logger.info(`停止任务: ${name}`)
  })
}
```

### 任务管理服务

```typescript
// services/scheduler.ts
import cron from 'node-cron'
import { db } from '../db'
import logger from '../utils/logger'

interface ScheduledTask {
  id: string
  name: string
  schedule: string
  handler: string
  enabled: boolean
  lastRun?: Date
  nextRun?: Date
}

class SchedulerService {
  private tasks: Map<string, cron.ScheduledTask> = new Map()

  /**
   * 从数据库加载任务
   */
  async loadTasks() {
    const tasks = await db.scheduledTasks.findAll({ enabled: true })

    for (const task of tasks) {
      this.scheduleTask(task)
    }
  }

  /**
   * 调度任务
   */
  scheduleTask(task: ScheduledTask) {
    if (this.tasks.has(task.id)) {
      this.tasks.get(task.id)?.stop()
    }

    const scheduledTask = cron.schedule(
      task.schedule,
      async () => {
        await this.executeTask(task)
      },
      {
        scheduled: task.enabled,
      }
    )

    this.tasks.set(task.id, scheduledTask)
  }

  /**
   * 执行任务
   */
  private async executeTask(task: ScheduledTask) {
    const startTime = Date.now()
    logger.info(`开始执行任务: ${task.name}`)

    try {
      // 动态加载处理器
      const handler = await import(`../jobs/${task.handler}`)
      await handler.default()

      // 更新执行记录
      await db.scheduledTasks.update(task.id, {
        lastRun: new Date(),
        lastStatus: 'success',
        lastDuration: Date.now() - startTime,
      })
    } catch (err) {
      logger.error(`任务执行失败: ${task.name}`, { error: (err as Error).message })

      await db.scheduledTasks.update(task.id, {
        lastRun: new Date(),
        lastStatus: 'failed',
        lastError: (err as Error).message,
      })
    }
  }

  /**
   * 添加新任务
   */
  async addTask(task: Omit<ScheduledTask, 'id'>) {
    const id = generateId()
    const newTask = { ...task, id }

    await db.scheduledTasks.create(newTask)

    if (task.enabled) {
      this.scheduleTask(newTask)
    }

    return id
  }

  /**
   * 更新任务
   */
  async updateTask(id: string, updates: Partial<ScheduledTask>) {
    await db.scheduledTasks.update(id, updates)

    const task = await db.scheduledTasks.findById(id)
    if (task) {
      this.scheduleTask(task)
    }
  }

  /**
   * 删除任务
   */
  async deleteTask(id: string) {
    this.tasks.get(id)?.stop()
    this.tasks.delete(id)
    await db.scheduledTasks.delete(id)
  }

  /**
   * 获取下次执行时间
   */
  getNextRun(cronExpression: string): Date | null {
    const interval = cron.parseExpression(cronExpression)
    return interval.next().toDate()
  }
}

export const scheduler = new SchedulerService()
```

## Bull 队列调度

### 安装

```bash
pnpm add bull
```

### 重复任务

```typescript
// queue/scheduled.ts
import Queue from 'bull'
import { redis } from '../utils/redis'

// 创建队列
const scheduledQueue = new Queue('scheduled-tasks', {
  redis: {
    host: 'localhost',
    port: 6379,
  },
})

// 处理器
scheduledQueue.process(async (job) => {
  const { type, data } = job.data

  switch (type) {
    case 'cleanup':
      await cleanupHandler(data)
      break
    case 'report':
      await reportHandler(data)
      break
    default:
      throw new Error(`未知任务类型: ${type}`)
  }
})

/**
 * 添加重复任务
 */
export async function addRecurringJob(
  jobId: string,
  cron: string,
  type: string,
  data: any = {}
) {
  await scheduledQueue.add(
    { type, data },
    {
      jobId,
      repeat: { cron },
    }
  )
}

/**
 * 移除重复任务
 */
export async function removeRecurringJob(jobId: string) {
  const jobs = await scheduledQueue.getRepeatableJobs()
  const job = jobs.find((j) => j.id === jobId)

  if (job) {
    await scheduledQueue.removeRepeatable({
      jobId,
      cron: job.cron,
    })
  }
}

// 注册任务
export async function setupRecurringJobs() {
  // 每天凌晨清理
  await addRecurringJob('daily-cleanup', '0 0 * * *', 'cleanup', {
    type: 'temp',
  })

  // 每周生成报告
  await addRecurringJob('weekly-report', '0 0 * * 1', 'report', {
    type: 'weekly',
  })
}
```

## node-schedule（更灵活）

```typescript
// jobs/scheduler.ts
import schedule from 'node-schedule'
import logger from '../utils/logger'

/**
 * node-schedule 支持更灵活的规则:
 *
 * 1. Cron 风格: '0 0 * * *'
 * 2. 对象风格:
 *    - { hour: 0, minute: 0 }  // 每天 0 点
 *    - { dayOfWeek: 1, hour: 9 }  // 周一 9 点
 * 3. 递归规则:
 *    const rule = new schedule.RecurrenceRule()
 *    rule.dayOfWeek = [0, new schedule.Range(0, 6)]
 *    rule.hour = 9
 *    rule.minute = 0
 */

// 存储任务
const jobs: Map<string, schedule.Job> = new Map()

/**
 * 创建一次性任务
 */
export function scheduleOnce(
  name: string,
  date: Date,
  handler: () => Promise<void>
) {
  const job = schedule.scheduleJob(date, async () => {
    try {
      await handler()
      logger.info(`一次性任务完成: ${name}`)
    } catch (err) {
      logger.error(`任务失败: ${name}`, { error: (err as Error).message })
    } finally {
      jobs.delete(name)
    }
  })

  jobs.set(name, job)
  return job
}

/**
 * 创建周期任务
 */
export function scheduleRecurring(
  name: string,
  rule: schedule.RecurrenceRule | string | Date,
  handler: () => Promise<void>
) {
  const job = schedule.scheduleJob(rule, async () => {
    try {
      await handler()
    } catch (err) {
      logger.error(`任务失败: ${name}`, { error: (err as Error).message })
    }
  })

  jobs.set(name, job)
  return job
}

/**
 * 取消任务
 */
export function cancelJob(name: string) {
  const job = jobs.get(name)
  if (job) {
    job.cancel()
    jobs.delete(name)
    logger.info(`取消任务: ${name}`)
  }
}

/**
 * 获取下次执行时间
 */
export function getNextInvocation(name: string): Date | null {
  const job = jobs.get(name)
  return job?.nextInvocation() || null
}
```

## 任务持久化

```typescript
// jobs/persistence.ts
import { db } from '../db'
import logger from '../utils/logger'

interface JobRecord {
  id: string
  name: string
  schedule: string
  type: 'cron' | 'once'
  payload: any
  enabled: boolean
  lastRun: Date | null
  nextRun: Date | null
  status: 'idle' | 'running' | 'failed'
  error: string | null
}

/**
 * 保存任务到数据库
 */
export async function saveJob(job: Omit<JobRecord, 'id'>) {
  return db.jobs.create({
    ...job,
    id: generateId(),
    lastRun: null,
    status: 'idle',
    error: null,
  })
}

/**
 * 更新任务状态
 */
export async function updateJobStatus(
  id: string,
  status: JobRecord['status'],
  error?: string
) {
  await db.jobs.update(id, {
    status,
    error: error || null,
    lastRun: status === 'idle' ? new Date() : undefined,
  })
}

/**
 * 记录执行日志
 */
export async function logExecution(
  jobId: string,
  duration: number,
  success: boolean,
  error?: string
) {
  await db.jobLogs.create({
    jobId,
    executedAt: new Date(),
    duration,
    success,
    error,
  })
}
```

## 常用任务示例

```typescript
// jobs/handlers/cleanup.ts
import fs from 'fs/promises'
import path from 'path'
import logger from '../../utils/logger'

/**
 * 清理临时文件
 */
export async function cleanupTempFiles() {
  const tempDir = path.join(process.cwd(), 'temp')
  const files = await fs.readdir(tempDir)
  const now = Date.now()
  const maxAge = 24 * 60 * 60 * 1000 // 24 小时

  let cleaned = 0

  for (const file of files) {
    const filePath = path.join(tempDir, file)
    const stat = await fs.stat(filePath)

    if (now - stat.mtimeMs > maxAge) {
      await fs.rm(filePath, { recursive: true })
      cleaned++
    }
  }

  logger.info(`清理临时文件完成: ${cleaned} 个`)
}

// jobs/handlers/report.ts
/**
 * 生成周报
 */
export async function generateWeeklyReport() {
  const weekStart = getWeekStart(new Date())
  const weekEnd = getWeekEnd(new Date())

  // 统计数据
  const stats = await db.tasks.aggregate({
    completed: { count: { status: 'completed' } },
    failed: { count: { status: 'failed' } },
    total: { count: {} },
  })

  // 生成报告
  const report = {
    period: { start: weekStart, end: weekEnd },
    stats,
    generatedAt: new Date(),
  }

  // 发送邮件
  await sendEmail({
    to: 'admin@example.com',
    subject: '周报',
    template: 'weekly-report',
    data: report,
  })
}
```