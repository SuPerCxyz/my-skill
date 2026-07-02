# EasyStack OSINOS 环境调试

通过 SSH 访问 K8s 环境，对运行在 Kubernetes 上的 OpenStack 服务进行调试。适用于可访问的运行中环境;离线 `.eslog` 分析、仓库 CI 修复和 EasyStack Cloud Web UI E2E 分别使用对应 skill。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，快速参考 |
| [access.md](access.md) | 环境后台访问、直连/跳板/BJ-xx SSH config 直达/JumpServer 入口 |
| [auth.md](auth.md) | 认证与鉴权排查 |
| [openstack/index.md](openstack/index.md) | OpenStack 组件部署、pod、启动方式详情 |
| [ceph/index.md](ceph/index.md) | Ceph 组件部署、pod、启动方式详情 |
| [k8s/index.md](k8s/index.md) | Kubernetes 组件部署、节点、pod、启动方式详情 |
| [code-debug.md](code-debug.md) | 授权后代码级调试指南(/opt mount) |
| [network.md](network.md) | 节点间网络排查、ARP 诊断、VLAN 子接口排查 |
| [logs.md](logs.md) | kubectl 日志查看、fluentd 历史搜索 |
| [special-operations.md](special-operations.md) | 组件级特殊操作、maintenance pod、授权门禁 |
| [pods.md](pods.md) | K8s Pod 诊断技巧 |
| [reference.md](reference.md) | 常用命令、环境常量速查 |
| [scenarios.md](scenarios.md) | 常见故障场景排查, 包括虚拟机异常和云硬盘异常 |
| [scripts.md](scripts.md) | ConfigMap 结构、启动脚本只读查看 |
| [scripts/jumpserver-env.sh](scripts/jumpserver-env.sh) | JumpServer 菜单 fallback 脚本, 需要用户指定资产 |

## 组件详情

| 文件 | 内容 |
|------|------|
| [openstack/service-map.md](openstack/service-map.md) | OpenStack 服务、Pod 前缀、namespace 速查 |
| [openstack/project-code-layout.md](openstack/project-code-layout.md) | OpenStack 组件代码仓库布局 |
| [openstack/nova.md](openstack/nova.md) | Nova 组件详情 |
| [openstack/cinder.md](openstack/cinder.md) | Cinder 组件详情 |
| [openstack/glance.md](openstack/glance.md) | Glance 组件详情 |
| [openstack/keystone.md](openstack/keystone.md) | Keystone 组件详情 |
| [openstack/barbican.md](openstack/barbican.md) | Barbican 组件详情 |
| [openstack/baremetal-ironic.md](openstack/baremetal-ironic.md) | Baremetal / Ironic 组件详情 |
| [openstack/networking.md](openstack/networking.md) | Networking / OVN / Proton 组件详情 |
| [openstack/aodh.md](openstack/aodh.md) | Aodh 组件详情 |
| [openstack/ceilometer.md](openstack/ceilometer.md) | Ceilometer 组件详情 |
| [openstack/gnocchi.md](openstack/gnocchi.md) | Gnocchi 组件详情 |
| [openstack/horizon.md](openstack/horizon.md) | Horizon 组件详情 |
| [openstack/infrastructure.md](openstack/infrastructure.md) | 基础服务组件详情 |
| [openstack/monitoring.md](openstack/monitoring.md) | 监控服务组件详情 |
| [openstack/extended-services.md](openstack/extended-services.md) | 扩展服务组件详情 |
