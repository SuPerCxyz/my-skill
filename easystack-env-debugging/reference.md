# Reference - Environment Constants and Namespaces

## Environment Constants 环境常量

```
Keystone Auth URL (busybox):  http://keystone-api.openstack.svc.cluster.local/v3
Keystone Public URL:          http://keystone-api.openstack.svc.cluster.local:80/v3
Keystone Public (APISIX):     http://keystone.openstack.svc.cluster.local:80/v3
Region:                       RegionOne
Interface for local client:   publicURL (APISIX only exposes port 80)
Interface for busybox:        adminURL
Python:                       python3 (in most pods)
OpenStack CLI (busybox):      /usr/bin/openstack
MySQL CLI (busybox):          /usr/bin/mysql
```

## Namespaces 命名空间

| Namespace | 用途 |
|-----------|---------|
| `openstack` | 核心 OpenStack 服务 |
| `ceph` | Ceph 存储(RGW for Swift) |
| `apisix` | API gateway |
| `ems` | 管理服务(peak) |
| `octavia` | 负载均衡 |
| `kube-system` | K8s 系统组件 |

## Node Inventory 节点清单

选择 SSH 目标节点、检查 pod 分布或做跨节点检查前, 先使用 Kubernetes node
名称作为环境节点清单。

```bash
kubectl get nodes -o name
```
