# OpenStack Service Map

本文件维护 OpenStack 组件速查信息, 便于和本目录下的组件详情一起检索。

## Core OpenStack Services 核心服务

| Service | Pod 前缀 | Admin 端口 | 说明 |
|---------|-----------|-----------|-------------|
| Keystone | `keystone-api-*` | cluster 内部访问 | Identity 服务 |
| Glance | `glance-api-0,1,2` | 9292 | Image 服务(StatefulSet) |
| Nova | `nova-api-osapi-*`, `nova-compute-*`, `nova-conductor-*`, `nova-scheduler-*`, `nova-maintenance-*` | 8774 | Compute 服务 |
| Cinder | `cinder-api-*`, `cinder-scheduler-*`, `cinder-volume-*` | 8776 | Block storage 服务 |
| Cinder Golem | `cinder-golem-*` | 8192 | Cinder dashboard 后端 API(端口 8192) |
| Ironic | `ironic-api-*`, `ironic-conductor-*`, `ironic-dashboard-*`, `ironic-dashboard-api-*` | 6385 | Baremetal 服务, 主要在 `ironic` namespace |
| Aodh | `aodh-api-*`, `aodh-evaluator-*`, `aodh-notifier-*` | 8042 | 告警服务 |
| Ceilometer | `ceilometer-api-*`, `ceilometer-collector-*` | 8777 | Telemetry 服务 |
| Gnocchi | `gnocchi-api-*`, `gnocchi-metricd-*` | - | Metrics storage 服务 |
| Horizon | `horizon-*` | 80 | OpenStack dashboard 服务 |

## Ironic Namespace 命名空间

Ironic services run in the independent `ironic` namespace. Do not assume they are
in `openstack`. The exception is `nova-compute-ironic`, which belongs to the
Nova side and may appear under the OpenStack deployment layout.

`ironic-api`, `ironic-conductor-default`, `ironic-dashboard`,
`ironic-dashboard-api`, `ironic-pushgateway` 位于 `ironic` namespace;
`nova-compute-ironic` 位于 `openstack` namespace。详细部署见
[baremetal-ironic.md](baremetal-ironic.md)。

## Networking (OVN Mode) 网络组件

没有独立的 `neutron-server` pod。网络由以下组件处理:

| Pod 模式 | 角色 |
|-------------|------|
| `ovn-controller-*` | 每个 compute 节点上的 OVN controller agent(DaemonSet) |
| `ovn-northd-0,1,2` | OVN Northd daemon(StatefulSet) |
| `ovn-ovsdb-nb-0,1,2` | OVN northbound 数据库 |
| `ovn-ovsdb-sb-0,1,2` | OVN southbound 数据库 |
| `ovn-ovsdb-nb-relay-*` / `ovn-ovsdb-sb-relay-*` | Database relay |
| `proton-ovn-gateway-monitor-agent-*` | Gateway monitoring |
| `proton-ovn-metadata-agent-*` | Metadata agent |
| `proton-ovn-l2gw-agent-*` | L2 gateway agent |

## Custom/Extended Services 扩展服务

| Service | Pod 前缀 | 说明 |
|---------|-----------|-------------|
| easystack-cache | `easystack-cache-api-*` | Cache 服务 |
| EMLA | `emla-apiserver-*`, `emla-controller-*` | 资源管理 |
| ESDM | `esdm-api-*` | 服务数据管理 |
| Proton | `proton-server-*`, `proton-dashboard-*` | 扩展网络服务 |
| Roller | `roller-dashboard-*` | 扩展 dashboard |
| OTA | `ota-openapi-*`, `ota-dashboard-*` | OTA 服务 |
| Coaster | `coaster-all-*` | 编排服务 |

## Infrastructure Pods 基础组件 Pod

| Pod | 说明 |
|-----|-------------|
| `mariadb-0,1,2` | 数据库(StatefulSet) |
| `rabbitmq-0,1,2` | 消息队列(StatefulSet) |
| `memcached-*` | Cache |
| `redis-*` | Redis |
| `mongodb-*` | MongoDB |
| `chartmuseum-*` | Helm chart 仓库 |
| `services/busybox` | 带 OpenStack CLI 的调试 pod(service selector, 不需要知道具体 pod 名) |
