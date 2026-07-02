# OpenStack nova

`nova` 组件 pod、启动方式和排查入口参考。

Nova maintenance、cell management、host maintenance、evacuation、migration debugging 等特殊操作说明统一见 [../special-operations.md](../special-operations.md#nova-maintenance-pod)。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `nova-compute` | nova-compute |
| Deployment | `nova-api-metadata` | nova-api |
| Deployment | `nova-api-osapi` | nova-osapi |
| Deployment | `nova-conductor` | nova-conductor |
| Deployment | `nova-dashboard` | nova-dashboard |
| Deployment | `nova-dashboard-api` | nova-dashboard-api |
| Deployment | `nova-maintenance` | nova-maintenance |
| Deployment | `nova-novncproxy` | nova-novncproxy |
| Deployment | `nova-operator` | nova-operator |
| Deployment | `nova-placement-api` | nova-placement-api |
| Deployment | `nova-scheduler` | nova-scheduler |
| Job | `nova-allocation-audit-heal-29706900` | allocation-audit-heal |
| Job | `nova-archive-deleted-rows-29706720` | nova-archive-deleted-rows |
| Job | `nova-bootstrap-v1-5.0.4` | nova-bootstrap |
| Job | `nova-cell-setup` | nova-cell-setup |
| Job | `nova-db-init` | nova-db-init<br>nova-db-init-api<br>nova-db-init-cell0<br>placement-db-init |
| Job | `nova-db-sync-7.0.1` | nova-db-sync<br>placement-db-sync |
| Job | `nova-domain-quota-allocated-sync-v1` | domain-quota-allocated-sync |
| Job | `nova-ecpbackendcheck-1782350084` | nova-ecpbackendcheck |
| Job | `nova-init-project-quotas-v1` | init-project-quotas |
| Job | `nova-ks-endpoints` | compute-ks-endpoints-admin<br>compute-ks-endpoints-internal<br>compute-ks-endpoints-public |
| Job | `nova-ks-service` | compute-ks-service-registration |
| Job | `nova-ks-user` | nova-ks-user |
| Job | `nova-service-cleaner-29706720` | heat-engine-cleaner |
