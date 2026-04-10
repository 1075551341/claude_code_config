---
description: Go 开发规则
globs: ["*.go", "go.mod"]
---

# Go 开发规则

## 项目结构

- 遵循 Go 标准布局：cmd/、internal/、pkg/、api/、web/
- internal/ 禁止外部导入
- 单个 main.go 仅做初始化和启动
- 接口定义在使用方，不在实现方

## 错误处理

- 显式检查每个 error：`if err != nil`
- 错误包装：`fmt.Errorf("do something: %w", err)`
- 自定义错误用 `errors.Is` / `errors.As` 检查
- 不吞错误：不 `_ = someFunc()`
- 哨兵错误用 `errors.New` 或 `sentinel` 变量

## 并发

- goroutine 必须有退出机制（context / done channel）
- 共享状态用 channel 通信，不用 mutex（CSP 原则）
- sync.WaitGroup 等待所有 goroutine 完成
- context.Context 作为第一个参数传播
- 避免 goroutine 泄漏：确保所有路径都能退出

## 接口

- 小接口（1-3 方法）优于大接口
- 接口组合替代大接口
- 隐式满足：不需要 `implements` 声明
- 依赖接口不依赖实现

## 命名

- 包名：小写、单词、无下划线（`httputil` 非 `http_util`）
- 导出：PascalCase，未导出：camelCase
- 缩写全大写：`HTTP`, `URL`, `ID`（但 `httpClient` 非 `HTTPClient`）
- 接口名：方法名单词 + er（`Reader`, `Writer`, `Stringer`）

## 测试

- 测试文件：`*_test.go`，同包（白盒）或 `_test` 子包（黑盒）
- 表驱动测试：`[]struct{ name, input, want }`
- Benchmark：`func BenchmarkXxx(b *testing.B)`
- 竞态检测：`go test -race`
