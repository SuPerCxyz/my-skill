# OpenStack ceilometer

`ceilometer` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `ceilometer-compute` | ceilometer-compute |
| Deployment | `ceilometer-api` | ceilometer-api |
| Deployment | `ceilometer-central` | ceilometer-central |
| Deployment | `ceilometer-collector` | ceilometer-collector |
| Deployment | `ceilometer-notification` | ceilometer-notification |
| Job | `ceilometer-db-init` | ceilometer-db-init |
| Job | `ceilometer-db-init-mongodb` | ceilometer-db-init-mongodb |
| Job | `ceilometer-db-sync` | ceilometer-db-sync |
| Job | `ceilometer-ecpbackendcheck-1782347493` | ceilometer-ecpbackendcheck |
| Job | `ceilometer-ks-endpoints` | metering-ks-endpoints-admin<br>metering-ks-endpoints-internal<br>metering-ks-endpoints-public |
| Job | `ceilometer-ks-service` | metering-ks-service-registration |
| Job | `ceilometer-ks-user` | ceilometer-ks-user |
