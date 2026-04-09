---
name: message-queue
description: 当需要实现消息队列、处理异步任务、使用BullMQ/RabbitMQ/Kafka时调用此技能。触发词：消息队列、BullMQ、RabbitMQ、Kafka、异步任务、延迟队列、发布订阅、消息中间件、任务调度。
---

# 消息队列

## 描述
异步任务与消息队列方案，涵盖 BullMQ、RabbitMQ、Redis Streams 等消息中间件。

## 触发条件
当用户提到：消息队列、MQ、BullMQ、RabbitMQ、Kafka、Redis Streams、异步任务、任务队列、延迟队列、死信队列、发布订阅、事件驱动、后台任务 时使用此技能。

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| Node.js 异步任务 | BullMQ（Redis） | 邮件/导出/图片处理等后台任务 |
| 轻量发布订阅 | Redis Pub/Sub | 实时通知、缓存失效广播 |
| 可靠消息传递 | RabbitMQ | 订单/支付等关键业务 |
| 高吞吐流式处理 | Kafka / Redis Streams | 日志采集、事件溯源 |
| Python 异步任务 | Celery + Redis/RabbitMQ | Django/FastAPI 后台任务 |
| 简单延迟任务 | BullMQ delay / Redis ZSET | 定时提醒、延迟重试 |

## 核心代码示例

### TypeScript - BullMQ 任务队列
```typescript
import { Queue, Worker, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';

const connection = new IORedis(process.env.REDIS_URL, { maxRetriesPerRequest: null });

// 定义队列
const emailQueue = new Queue('email', {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: { count: 1000 },
    removeOnFail: { count: 5000 },
  },
});

/**
 * @描述 添加邮件发送任务到队列
 * @参数 to - 收件人
 * @参数 subject - 邮件主题
 * @参数 delay - 延迟发送（毫秒）
 */
async function enqueueEmail(to: string, subject: string, body: string, delay?: number) {
  await emailQueue.add('send', { to, subject, body }, {
    delay,
    priority: subject.includes('验证码') ? 1 : 5,
  });
}

// Worker 消费者
const worker = new Worker('email', async (job) => {
  const { to, subject, body } = job.data;
  await sendEmail(to, subject, body);
  return { sentAt: new Date().toISOString() };
}, {
  connection,
  concurrency: 5,
  limiter: { max: 100, duration: 60_000 },
});

worker.on('completed', (job) => {
  console.log(`任务 ${job.id} 完成`);
});

worker.on('failed', (job, err) => {
  console.error(`任务 ${job?.id} 失败: ${err.message}`);
});
```

### TypeScript - Redis Streams 事件流
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

// 生产者：发布事件
async function publishEvent(stream: string, event: Record<string, string>) {
  await redis.xadd(stream, '*', ...Object.entries(event).flat());
}

// 消费者组
async function setupConsumerGroup(stream: string, group: string) {
  try {
    await redis.xgroup('CREATE', stream, group, '0', 'MKSTREAM');
  } catch { /* 组已存在 */ }
}

async function consumeEvents(stream: string, group: string, consumer: string) {
  while (true) {
    const results = await redis.xreadgroup(
      'GROUP', group, consumer,
      'COUNT', 10, 'BLOCK', 5000,
      'STREAMS', stream, '>'
    );
    if (!results) continue;
    for (const [, messages] of results) {
      for (const [id, fields] of messages) {
        const data = Object.fromEntries(
          fields.reduce<[string, string][]>((acc, v, i, arr) =>
            i % 2 === 0 ? [...acc, [v, arr[i + 1]]] : acc, [])
        );
        await processEvent(data);
        await redis.xack(stream, group, id);
      }
    }
  }
}
```

### Python - Celery 异步任务
```python
from celery import Celery
from celery.schedules import crontab

app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

app.conf.update(
    task_serializer="json",
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification(self, user_id: int, message: str):
    """
    描述：异步发送通知，失败自动重试
    参数：
        user_id: 用户 ID
        message: 通知内容
    注意：最多重试 3 次，间隔 60 秒
    """
    try:
        notify_user(user_id, message)
    except ConnectionError as exc:
        raise self.retry(exc=exc)

# 延迟任务
send_notification.apply_async(args=[1, "欢迎注册"], countdown=300)

# 定时任务配置
app.conf.beat_schedule = {
    "daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),
    },
}
```

## 最佳实践

1. **幂等消费** → 消费者必须幂等，相同消息重复处理结果一致
2. **死信队列** → 多次失败的消息转入死信队列，人工排查
3. **重试策略** → 指数退避（2s → 4s → 8s），设置最大重试次数
4. **积压监控** → 队列长度超阈值告警，及时扩容消费者
5. **有序性** → 需严格顺序时使用单分区/单消费者，否则允许并发
6. **消息大小** → 消息体只传 ID/引用，不传大体量数据
7. **优雅关停** → Worker 关闭前完成当前任务，不丢消息
