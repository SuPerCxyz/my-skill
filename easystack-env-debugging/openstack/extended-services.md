# OpenStack extended-services

扩展服务 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `automation-operators` | automation-operators |
| Deployment | `easystack-cache` | easystack-cache |
| Deployment | `easystack-cache-api` | easystack-cache-api |
| Deployment | `emla-apiserver` | emla-apiserver |
| Deployment | `emla-controller-manager` | emla-controller-manager |
| Deployment | `emla-dashboard` | emla-dashboard |
| Deployment | `emla-grafana` | grafana |
| Deployment | `esdm-api` | esdm-api |
| Deployment | `esguides` | esguides |
| Deployment | `ess-automation` | ess-automation |
| Deployment | `gpu-api` | gpu-api |
| Deployment | `ota-dashboard` | ota-dashboard |
| Deployment | `roller-dashboard` | roller-dashboard |
| Deployment | `topology-operators` | topology-operators |
| Job | `automation-operators-bootstrap-xkx3p` | automation-operators-bootstrap |
| Job | `coaster-data-migration` | coaster-data-migration |
| Job | `coaster-db-init-v2` | coaster-db-init |
| Job | `coaster-db-sync-7.0.1-alpha.103` | coaster-db-sync |
| Job | `coaster-ks-endpoints-v2` | coaster-ks-endpoints-admin<br>coaster-ks-endpoints-internal<br>coaster-ks-endpoints-public |
| Job | `coaster-ks-service-v2` | coaster-ks-service-registration |
| Job | `coaster-ks-user-v2` | coaster-ks-user |
| Job | `ecms-create-secret-etcd` | ecms-create-secret-etcd |
| Job | `ecms-ecpbackendcheck-1782370700` | ecms-ecpbackendcheck |
| Job | `ecms-ks-user` | ecms-ks-user |
| Job | `ecms-restore-alerts` | ecms-restore-alerts |
| Job | `emla-ecpbackendcheck-1782350086` | emla-ecpbackendcheck |
| Job | `emla-ks-endpoints` | emla-ks-endpoints-admin<br>emla-ks-endpoints-internal<br>emla-ks-endpoints-public |
| Job | `emla-ks-service` | emla-ks-service-registration |
| Job | `esguides-ecpbackendcheck-1782334375` | esguides-ecpbackendcheck |
| Job | `estack-cache-ecpbackendcheck-1782334509` | estack-cache-ecpbackendcheck |
| Job | `estack-dm-ecpbackendcheck-1782334734` | estack-dm-ecpbackendcheck |
| Job | `ota-ecpbackendcheck-1782332311` | ota-ecpbackendcheck |
| Job | `ota-upload-platform-pack-1782332311` | upload-pack |
| Job | `roller-cached-db-init` | roller-cached-db-init |
| Job | `roller-restore` | restore-main |
| Job | `tag-crd-ecpbackendcheck-1782346732` | tag-crd-ecpbackendcheck |
| Job | `topology-bootstrap-gqzt3` | craftman-bootstrap |
| StatefulSet | `coaster-all` | coaster-api<br>coaster-conductor<br>coaster-other |
| StatefulSet | `ota` | dota |
| StatefulSet | `ota-openapi` | nginx<br>openapi |
