# EasyStack OSINOS 环境调试

通过 SSH 访问 K8s 环境，对运行在 Kubernetes 上的 OpenStack 服务进行调试。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，快速参考 |
| [access.md](access.md) | 环境后台访问、直连/跳板/JumpServer 三种入口 |
| [auth.md](auth.md) | 认证与鉴权排查 |
| [code-debug.md](code-debug.md) | 授权后代码级调试指南(/opt mount) |
| [network.md](network.md) | 节点间网络排查、ARP 诊断、VLAN 子接口排查 |
| [logs.md](logs.md) | kubectl 日志查看、fluentd 历史搜索 |
| [nova-maintenance.md](nova-maintenance.md) | Nova maintenance pod 只读检查与授权门禁 |
| [pods.md](pods.md) | K8s Pod 诊断技巧 |
| [reference.md](reference.md) | 常用命令、环境常量速查 |
| [scenarios.md](scenarios.md) | 常见故障场景排查 |
| [scripts.md](scripts.md) | ConfigMap 结构、启动脚本只读查看 |
