# OpenStack barbican

`barbican` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `barbican-api` | barbican-api |
| Deployment | `barbican-dashboard` | barbican-dashboard |
| Deployment | `barbican-dashboard-api` | barbican-dashboard-api |
| Deployment | `barbican-kms` | barbican-kms |
| Deployment | `barbican-kms-dashboard-api` | barbican-kms-dashboard-api |
| Deployment | `barbican-openapi` | barbican-openapi |
| Job | `barbican-db-init-v1.2.1` | barbican-db-init |
| Job | `barbican-db-sync-v1.2.1` | barbican-db-sync |
| Job | `barbican-ecpbackendcheck-1782369558` | barbican-ecpbackendcheck |
| Job | `barbican-ks-endpoints-v1.2.1` | key-manager-ks-endpoints-admin<br>key-manager-ks-endpoints-internal<br>key-manager-ks-endpoints-public |
| Job | `barbican-ks-service-v1.2.1` | key-manager-ks-service-registration |
| Job | `barbican-ks-user-v1.2.1` | barbican-ks-user |
| Job | `clean-kms-db-tables-v1.2.1` | kms-db-tables-clean |
| Job | `kms-db-init-v1.2.1` | kms-db-init |
| Job | `kms-db-sync-v1.2.1` | kms-db-sync |
| Job | `kms-schedule-delete-v1.2.1-29706720` | kms-schedule-delete |
