# 可选项目隔离

参考 [Trail of Bits devcontainer](https://github.com/trailofbits/claude-code-devcontainer)，在需要隔离不可信代码或复现环境时评估容器方案。

先检查挂载、网络、用户权限和持久化范围；只提供项目必需配置与凭据，不把整个用户配置目录挂入容器。
容器本身不证明安全，也不构成跳过宿主权限的授权。默认不启用 bypassPermissions 或等价选项。

工具运行配置由容器内各工具独立维护；不依赖宿主其他工具目录。依据项目需求验证构建、测试和恢复路径。
