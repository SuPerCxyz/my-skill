# EasyStack OSINOS 环境调试

通过统一访问脚本进入 K8s 环境, 对运行在 Kubernetes 上的 OpenStack 服务进行调试。适用于可访问的运行中环境; 询问异常原因、创建失败或挂载失败时优先查业务 pod 日志, 资源状态只做补充上下文。离线 `.eslog` 分析、仓库 CI 修复和 EasyStack Cloud Web UI E2E 分别使用对应 skill。

## 文件说明

完整文件索引以 [SKILL.md](SKILL.md) 的 Quick Reference 为准。常用入口:

| 入口 | 用途 |
|------|------|
| [access.md](access.md) | 环境后台访问和统一脚本入口 |
| [scenarios.md](scenarios.md) | 常见虚拟机、云硬盘、服务启动故障 |
| [logs.md](logs.md) | pod 当前日志和 fluentd 历史日志 |
| [auth.md](auth.md) | OpenStack CLI 认证和 busybox |
| [openstack/index.md](openstack/index.md) | OpenStack 组件详情索引 |
| [ceph/index.md](ceph/index.md) | Ceph 组件详情 |
| [k8s/index.md](k8s/index.md) | Kubernetes 组件详情 |
