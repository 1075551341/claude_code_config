---
description: Java/Spring 开发规则
globs: ["*.java", "*.kt", "pom.xml", "build.gradle", "*.properties", "*.yml"]
---

# Java/Spring 开发规则

## 项目结构

- 分层架构：controller / service / repository / model / config
- 配置外部化：application-{profile}.yml，禁止硬编码
- 单一职责：每个类一个明确职责

## 编码规范

- 命名：类 PascalCase、方法/字段 camelCase、常量 UPPER_SNAKE
- Optional：替代 null 返回值，链式调用避免嵌套
- 异常：业务异常继承 RuntimeException，禁止吞异常
- 泛型：优先泛型而非 Object + 强转
- 不可变：DTO/VO 用 record（Java 17+）或 final 字段

## Spring 约定

- 依赖注入：构造注入优于 @Autowired 字段注入
- @Transactional：仅用于 Service 层，只读方法标记 readOnly
- 配置类：用 @ConfigurationProperties 替代 @Value
- 异常处理：@RestControllerAdvice 全局处理
- 分层校验：Controller @Valid → Service 业务校验

## 并发安全

- 线程安全集合：ConcurrentHashMap、CopyOnWriteArrayList
- CompletableFuture：异常处理用 exceptionally/handle
- 线程池：禁止 Executors.newFixedThreadPool（无边界队列），用 ThreadPoolExecutor
- 锁：优先 java.util.concurrent.locks，避免 synchronized

## 测试

- 单元测试：JUnit 5 + Mockito，覆盖率 ≥ 80%
- 集成测试：@SpringBootTest + Testcontainers
- 测试命名：method_scenario_expectedResult

## 时间处理

- 禁止 new Date() / Calendar，用 java.time（LocalDateTime/Instant）
- 通过 Clock 注入实现可测试性
- 时区：存储用 UTC，展示用用户时区
