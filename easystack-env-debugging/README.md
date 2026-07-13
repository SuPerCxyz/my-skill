# EasyStack OSINOS 环境调试

通过统一访问脚本进入 K8s 环境, 对运行在 Kubernetes 上的 OpenStack 服务进行问题
调查或授权代码调试。问题调查优先读取业务 pod 日志; 代码调试可直接用于运行时代码
overlay、patch 和新功能验证, 不要求先完成根因排查。历史故障需要本地日志时自动联合
`easystack-log-analysis`。

## Features 功能

- 通过统一脚本处理直连、跳板机和 JumpServer 环境访问
- 按当前 pod -> fluentd 历史日志顺序定位运行时故障
- 联合本地 `.eslog` / `ecs.*` 构建历史证据链
- 在用户明确授权后执行环境代码调试和新功能验证
- 使用无表格、行首安全且含一句话总结的问题分析结论格式

## Quick Start 快速开始

1. 先说明目标是问题调查、代码调试, 还是通过代码改动验证故障假设。
2. 问题调查提供故障时间、资源 UUID 或错误信息; 代码调试提供目标服务、文件、预期
   改动、验证方式和回滚要求。
3. 历史故障需要离线日志时可提供 `.eslog` / `ecs.*` 路径; 未指定路径时只检查
   当前工作目录。
4. Agent 通过 `scripts/env-access.sh` 完成最小连接验证, 再进入对应模式。
5. 涉及环境变更时, Agent 先说明影响、回滚和验证方式并等待明确授权。

## 文件说明

完整文件索引以 [SKILL.md](SKILL.md) 的 Quick Reference 为准。常用入口:

| 入口 | 用途 |
|------|------|
| [access.md](access.md) | 环境后台访问和统一脚本入口 |
| [scenarios.md](scenarios.md) | 常见虚拟机、云硬盘、服务启动故障 |
| [logs.md](logs.md) | pod 当前日志和 fluentd 历史日志 |
| [report-format.md](report-format.md) | 无表格、行首安全且含一句话总结的结论格式 |
| [auth.md](auth.md) | OpenStack CLI 认证和 busybox |
| [code-debug.md](code-debug.md) | 授权后的环境代码 overlay 和新功能调试 |
| [openstack/index.md](openstack/index.md) | OpenStack 组件详情索引 |
| [ceph/index.md](ceph/index.md) | Ceph 组件详情 |
| [k8s/index.md](k8s/index.md) | Kubernetes 组件详情 |
