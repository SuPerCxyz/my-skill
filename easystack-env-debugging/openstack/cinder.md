# OpenStack cinder

`cinder` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `cinder-api` | cinder-api |
| Deployment | `cinder-dashboard` | cinder-dashboard |
| Deployment | `cinder-golem` | golem |
| Deployment | `cinder-scheduler` | cinder-scheduler |
| Deployment | `cinder-volume` | cinder-volume |
| Job | `cinder-bootstrap` | cinder-bootstrap |
| Job | `cinder-db-init` | cinder-db-init |
| Job | `cinder-db-sync` | cinder-db-sync |
| Job | `cinder-domain-quota-allocated-sync` | domain-quota-allocated-sync |
| Job | `cinder-ecpbackendcheck-1782347874` | cinder-ecpbackendcheck |
| Job | `cinder-init-project-quotas` | init-project-quotas |
| Job | `cinder-ks-endpoints` | volumev2-ks-endpoints-admin<br>volumev2-ks-endpoints-internal<br>volumev2-ks-endpoints-public<br>volume-ks-endpoints-admin<br>volume-ks-endpoints-internal<br>volume-ks-endpoints-public<br>volumev3-ks-endpoints-admin<br>volumev3-ks-endpoints-internal<br>volumev3-ks-endpoints-public |
| Job | `cinder-ks-service` | volumev2-ks-service-registration<br>volume-ks-service-registration<br>volumev3-ks-service-registration |
| Job | `cinder-ks-user` | cinder-ks-user |
| Job | `cinder-storage-init-v1` | cinder-storage-init |
