# OpenStack gnocchi

`gnocchi` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `gnocchi-metricd` | gnocchi-metricd |
| DaemonSet | `gnocchi-statsd` | gnocchi-statsd |
| Deployment | `gnocchi-api` | gnocchi-api |
| Job | `gnocchi-db-init-indexer` | gnocchi-db-init-indexer |
| Job | `gnocchi-db-init-keystone` | keystone-db-init |
| Job | `gnocchi-db-sync` | gnocchi-db-sync |
| Job | `gnocchi-ks-endpoints` | metric-ks-endpoints-admin<br>metric-ks-endpoints-internal<br>metric-ks-endpoints-public |
| Job | `gnocchi-ks-service` | metric-ks-service-registration |
| Job | `gnocchi-ks-user` | gnocchi-ks-user |
| Job | `gnocchi-storage-init-6.1.2` | gnocchi-storage-init |
