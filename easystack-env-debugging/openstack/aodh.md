# OpenStack aodh

`aodh` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `aodh-api` | aodh-api |
| Deployment | `aodh-evaluator` | aodh-evaluator |
| Deployment | `aodh-listener` | aodh-listener |
| Deployment | `aodh-notifier` | aodh-notifier |
| Job | `aodh-db-init` | aodh-db-init |
| Job | `aodh-db-sync` | aodh-db-sync |
| Job | `aodh-ks-endpoints` | alarming-ks-endpoints-admin<br>alarming-ks-endpoints-internal<br>alarming-ks-endpoints-public |
| Job | `aodh-ks-service` | alarming-ks-service-registration |
| Job | `aodh-ks-user` | aodh-ks-user |
