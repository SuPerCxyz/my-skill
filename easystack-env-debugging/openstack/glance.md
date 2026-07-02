# OpenStack glance

`glance` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `glance-dashboard` | glance-dashboard |
| Deployment | `glance-dashboard-api` | glance-dashboard-api |
| Job | `glance-bootstrap` | glance-bootstrap |
| Job | `glance-db-init` | glance-db-init |
| Job | `glance-db-sync` | glance-db-sync |
| Job | `glance-ecpbackendcheck-1782349002` | glance-ecpbackendcheck |
| Job | `glance-ks-endpoints` | image-ks-endpoints-admin<br>image-ks-endpoints-internal<br>image-ks-endpoints-public |
| Job | `glance-ks-service` | image-ks-service-registration |
| Job | `glance-ks-user` | glance-ks-user |
| Job | `glance-scrubber-29706840` | glance-scrubber |
| Job | `glance-storage-init-v1` | glance-storage-init |
| StatefulSet | `glance-api` | glance-api<br>virt-v2v |
