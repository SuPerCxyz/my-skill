# OpenStack Baremetal Ironic

记录裸金属相关组件的部署情况。裸金属服务主体部署在 `ironic` namespace, 但 `nova-compute-ironic` 位于 `openstack` namespace。

后续环境可能继续扩展更多 ironic 或 baremetal 组件。

## Namespace 边界

| Namespace | 内容 |
|-----------|------|
| `ironic` | `ironic-api`, `ironic-conductor-default`, `ironic-dashboard`, `ironic-dashboard-api`, `ironic-pushgateway` 和相关初始化/清理 Job |
| `openstack` | `nova-compute-ironic` StatefulSet, 属于 Nova 与裸金属对接侧组件 |

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `ironic-api` | ironic-api |
| Deployment | `ironic-dashboard` | ironic-dashboard |
| Deployment | `ironic-dashboard-api` | ironic-dashboard-api |
| Job | `ceph-namespace-client-key-generator-qjnh3` | ceph-storage-keys-generator |
| Job | `ironic-bootstrap-6.3.1` | ironic-bootstrap |
| Job | `ironic-db-init-6.3.1` | ironic-db-init |
| Job | `ironic-db-sync-6.3.1` | ironic-db-sync |
| Job | `ironic-ecpbackendcheck-1782196205` | ironic-ecpbackendcheck |
| Job | `ironic-ks-endpoints-6.3.1` | baremetal-ks-endpoints-admin<br>baremetal-ks-endpoints-internal<br>baremetal-ks-endpoints-public |
| Job | `ironic-ks-service-6.3.1` | baremetal-ks-service-registration |
| Job | `ironic-ks-user-6.3.1` | ironic-ks-user |
| Job | `pushgateway-data-cleaner-29707620` | pushgateway-data-cleaner |
| Job | `pushgateway-data-cleaner-29707630` | pushgateway-data-cleaner |
| Job | `pushgateway-data-cleaner-29707640` | pushgateway-data-cleaner |
| StatefulSet | `ironic-conductor-default` | ironic-conductor<br>ironic-conductor-pxe<br>ironic-conductor-http |
| StatefulSet | `ironic-pushgateway` | ironic-pushgateway<br>ironic-pushgateway-http |
| StatefulSet | `nova-compute-ironic` | nova-compute-ironic |
