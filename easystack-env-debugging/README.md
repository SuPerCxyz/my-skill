# EasyStack OSINOS 环境调试

通过统一访问脚本进入 K8s 环境, 对运行在 Kubernetes 上的 OpenStack 服务进行调试。
根因排查优先读取业务 pod 日志, 资源状态只补充上下文。故障时间超出在线日志时间窗
或用户明确要求结合本地 `.eslog` / `ecs.*` 时, 自动联合 `easystack-log-analysis`。

## Features 功能

- 通过统一脚本处理直连、跳板机和 JumpServer 环境访问
- 按当前 pod -> fluentd 历史日志顺序定位运行时故障
- 联合本地 `.eslog` / `ecs.*` 构建历史证据链
- 在用户明确授权后执行环境代码调试和新功能验证
- 使用无表格、可复制的问题分析结论格式

## Quick Start 快速开始

1. 提供目标环境名称或 IP, 以及故障时间、资源 UUID 或错误信息。
2. 历史故障需要离线日志时可提供 `.eslog` / `ecs.*` 路径; 未指定路径时只检查
   当前工作目录。
3. Agent 通过 `scripts/env-access.sh` 完成最小连接验证, 再按日志优先顺序排查。
4. 涉及环境变更时, Agent 先说明影响、回滚和验证方式并等待明确授权。

## 文件说明

完整文件索引以 [SKILL.md](SKILL.md) 的 Quick Reference 为准。常用入口:

| 入口 | 用途 |
|------|------|
| [access.md](access.md) | 环境后台访问和统一脚本入口 |
| [scenarios.md](scenarios.md) | 常见虚拟机、云硬盘、服务启动故障 |
| [logs.md](logs.md) | pod 当前日志和 fluentd 历史日志 |
| [report-format.md](report-format.md) | 无表格、可复制的问题分析结论格式 |
| [auth.md](auth.md) | OpenStack CLI 认证和 busybox |
| [code-debug.md](code-debug.md) | 授权后的环境代码 overlay 和新功能调试 |
| [openstack/index.md](openstack/index.md) | OpenStack 组件详情索引 |
| [ceph/index.md](ceph/index.md) | Ceph 组件详情 |
| [k8s/index.md](k8s/index.md) | Kubernetes 组件详情 |
