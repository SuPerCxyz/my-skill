# OpenStack extended-services

扩展服务 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `automation-crd` | `automation-crd-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `automation-operators` | `automation-operators-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `coaster` | `coaster-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `coaster-operator` | `coaster-operator-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `dota-agent` | `dota-agent-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `ecms` | `ecms-7.0.1-alpha.28` | DEPLOYED |
| `openstack` | `emla` | `emla-7.0.1-alpha.27` | DEPLOYED |
| `openstack` | `esguides` | `esguides-6.1.1` | DEPLOYED |
| `openstack` | `ess-automation` | `ess-automation-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `estack-cache` | `estack-cache-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `estack-dm` | `estack-dm-7.0.1-alpha.12` | DEPLOYED |
| `openstack` | `ota` | `ota-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `roller-dashboard` | `roller-dashboard-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `tag-crd` | `tag-crd-6.0.2` | DEPLOYED |
| `openstack` | `topology-operators` | `topology-operators-7.0.1-alpha.103` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `automation-operators` | 1/1 ready | automation-operators | - |
| `openstack` | Deployment | `easystack-cache` | 1/1 ready | easystack-cache | init |
| `openstack` | Deployment | `easystack-cache-api` | 3/3 ready | easystack-cache-api | init |
| `openstack` | Deployment | `emla-apiserver` | 3/3 ready | emla-apiserver | init |
| `openstack` | Deployment | `emla-controller-manager` | 3/3 ready | emla-controller-manager | init |
| `openstack` | Deployment | `emla-dashboard` | 3/3 ready | emla-dashboard | init |
| `openstack` | Deployment | `emla-grafana` | 3/3 ready | grafana | init |
| `openstack` | Deployment | `esdm-api` | 3/3 ready | esdm-api | - |
| `openstack` | Deployment | `esguides` | 3/3 ready | esguides | init |
| `openstack` | Deployment | `ess-automation` | 1/1 ready | ess-automation | - |
| `openstack` | Deployment | `gpu-api` | 3/3 ready | gpu-api | - |
| `openstack` | Deployment | `ota-dashboard` | 3/3 ready | ota-dashboard | init |
| `openstack` | Deployment | `roller-dashboard` | 3/3 ready | roller-dashboard | init |
| `openstack` | Deployment | `topology-operators` | 1/1 ready | topology-operators | - |
| `openstack` | Job | `automation-operators-bootstrap-xkx3p` | succeeded=1, failed=0 | automation-operators-bootstrap | - |
| `openstack` | Job | `coaster-data-migration` | succeeded=1, failed=0 | coaster-data-migration | - |
| `openstack` | Job | `coaster-db-init-v2` | succeeded=1, failed=0 | coaster-db-init | init |
| `openstack` | Job | `coaster-db-sync-7.0.1-alpha.103` | succeeded=1, failed=0 | coaster-db-sync | init |
| `openstack` | Job | `coaster-ks-endpoints-v2` | succeeded=1, failed=0 | coaster-ks-endpoints-admin<br>coaster-ks-endpoints-internal<br>coaster-ks-endpoints-public | init |
| `openstack` | Job | `coaster-ks-service-v2` | succeeded=1, failed=0 | coaster-ks-service-registration | init |
| `openstack` | Job | `coaster-ks-user-v2` | succeeded=1, failed=0 | coaster-ks-user | init |
| `openstack` | Job | `ecms-create-secret-etcd` | succeeded=1, failed=0 | ecms-create-secret-etcd | init |
| `openstack` | Job | `ecms-ecpbackendcheck-1782370700` | succeeded=1, failed=0 | ecms-ecpbackendcheck | init |
| `openstack` | Job | `ecms-ks-user` | succeeded=1, failed=0 | ecms-ks-user | init |
| `openstack` | Job | `ecms-restore-alerts` | succeeded=1, failed=0 | ecms-restore-alerts | init |
| `openstack` | Job | `emla-ecpbackendcheck-1782350086` | succeeded=1, failed=0 | emla-ecpbackendcheck | init |
| `openstack` | Job | `emla-ks-endpoints` | succeeded=1, failed=0 | emla-ks-endpoints-admin<br>emla-ks-endpoints-internal<br>emla-ks-endpoints-public | init |
| `openstack` | Job | `emla-ks-service` | succeeded=1, failed=0 | emla-ks-service-registration | init |
| `openstack` | Job | `esguides-ecpbackendcheck-1782334375` | succeeded=1, failed=0 | esguides-ecpbackendcheck | init |
| `openstack` | Job | `estack-cache-ecpbackendcheck-1782334509` | succeeded=1, failed=0 | estack-cache-ecpbackendcheck | init |
| `openstack` | Job | `estack-dm-ecpbackendcheck-1782334734` | succeeded=1, failed=0 | estack-dm-ecpbackendcheck | init |
| `openstack` | Job | `ota-ecpbackendcheck-1782332311` | succeeded=1, failed=0 | ota-ecpbackendcheck | init |
| `openstack` | Job | `ota-upload-platform-pack-1782332311` | succeeded=1, failed=0 | upload-pack | init |
| `openstack` | Job | `roller-cached-db-init` | succeeded=1, failed=0 | roller-cached-db-init | init |
| `openstack` | Job | `roller-restore` | succeeded=1, failed=0 | restore-main | - |
| `openstack` | Job | `tag-crd-ecpbackendcheck-1782346732` | succeeded=1, failed=0 | tag-crd-ecpbackendcheck | init |
| `openstack` | Job | `topology-bootstrap-gqzt3` | succeeded=1, failed=0 | craftman-bootstrap | - |
| `openstack` | StatefulSet | `coaster-all` | 1/1 ready | coaster-api<br>coaster-conductor<br>coaster-other | init |
| `openstack` | StatefulSet | `ota` | 1/1 ready | dota | - |
| `openstack` | StatefulSet | `ota-openapi` | 1/1 ready | nginx<br>openapi | - |

## Container Details 容器详情

### automation-operators

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - automation-operators (hub.easystack.io/production/escloud-linux-source-automation-operators:7.0.1-alpha.103;
    /tmp/automation-operators.sh start)
- Init containers:
  - -

### easystack-cache

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - easystack-cache (hub.easystack.io/production/escloud-linux-source-estack-cache:7.0.1-alpha.103; /tmp/easystack-cache.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### easystack-cache-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - easystack-cache-api (hub.easystack.io/production/escloud-linux-source-estack-cache:7.0.1-alpha.103;
    /tmp/easystack-cache-api.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-apiserver

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - emla-apiserver (hub.easystack.io/production/escloud-linux-source-emla-apiserver:7.0.1-alpha.27;
    /usr/local/bin/emla-apiserver --prometheus-endpoint http://thanos-query.openstack:10902 --prometheus-global-endpoint
    http://thanos-query-global.openstack:10902 --authentication-mode Keystone --authentication-alertmanager-webhook-path
    /apis/alerting/v1/ecms/alerts --authentication-alertmanager-bearer-token J06.ZjhMoAbboC.k --authorization-mode Keystone
    --alertmanager-endpoint http://alertmanager.openstack:9093 --alert-resolve-timeout 5m --alert-namespace openstack
    --quota-alerts=50000 --quota-custom-rules=5000 --quota-custom-groups=500 --quota-subscriptions=500
    --quota-subscription-terminals=2500 --grpc-client-timeout=10s --grpc-client-tls-cert=/etc/emla/certs/client/tls.crt
    --grpc-client-tls-key=/etc/emla/certs/client/tls.key --grpc-client-tls-server-ca=/etc/emla/certs/server/ca.crt)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-controller-manager

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - emla-controller-manager (hub.easystack.io/production/escloud-linux-source-emla-controller-manager:7.0.1-alpha.27;
    /usr/local/bin/emla-controller-manager --leader-elect=true --prometheus-endpoint http://thanos-query.openstack:10902
    --alertmanager-endpoint http://alertmanager.openstack:9093 --alert-resolve-timeout 5m --alert-namespace openstack
    --alert-save-mode quota --quota-alerts=50000 --quota-custom-rules=5000 --quota-custom-groups=500
    --quota-subscriptions=500 --quota-subscription-terminals=2500 --rsync-alert-period 15s --rsync-quota-period 10s)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - emla-dashboard (hub.easystack.io/production/escloud-linux-source-emla-dashboard:7.0.1-alpha.27; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-grafana

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - grafana (hub.easystack.io/production/escloud-linux-source-grafana:7.0.1-alpha.27; /tmp/grafana.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### esdm-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - esdm-api (hub.easystack.io/production/escloud-linux-source-estack-dm:7.0.1-alpha.12; /tmp/esdm-api.sh)
- Init containers:
  - -

### esguides

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - esguides (hub.easystack.io/production/escloud-linux-source-esguides:6.1.1; /tmp/esguides.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ess-automation

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - ess-automation (hub.easystack.io/production/escloud-linux-source-ess-automation:7.0.1-alpha.103; /tmp/ess-automation.sh
    start)
- Init containers:
  - -

### gpu-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - gpu-api (hub.easystack.io/production/escloud-linux-source-gpu-api:7.0.1-alpha.12; gpu-api server
    --config-file=/etc/gpu-api/config.toml)
- Init containers:
  - -

### ota-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ota-dashboard (hub.easystack.io/production/escloud-linux-source-ota-dashboard:7.0.1-alpha.103; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### roller-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - roller-dashboard (hub.easystack.io/production/escloud-linux-source-roller-dashboard:7.0.1-alpha.103;
    /tmp/roller-dashboard.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### topology-operators

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - topology-operators (hub.easystack.io/production/escloud-linux-source-topology-base:7.0.1-alpha.103;
    /tmp/topology-operators.sh start)
- Init containers:
  - -

### automation-operators-bootstrap-xkx3p

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - automation-operators-bootstrap (hub.easystack.io/production/escloud-linux-source-automation-operators:7.0.1-alpha.103;
    /tmp/bootstrap.sh)
- Init containers:
  - -

### coaster-data-migration

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-data-migration (hub.easystack.io/production/escloud-linux-source-coaster-other:latest; ionice -c3
    /tmp/migrate_coaster_data.sh)
- Init containers:
  - -

### coaster-db-init-v2

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### coaster-db-sync-7.0.1-alpha.103

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-db-sync (hub.easystack.io/production/escloud-linux-source-coaster-api:7.0.1-alpha.103; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### coaster-ks-endpoints-v2

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - coaster-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - coaster-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### coaster-ks-service-v2

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### coaster-ks-user-v2

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - coaster-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ecms-create-secret-etcd

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ecms-create-secret-etcd (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/create-secret-etcd.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ecms-ecpbackendcheck-1782370700

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ecms-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ecms-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ecms-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ecms-restore-alerts

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ecms-restore-alerts (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/restore-alerts.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-ecpbackendcheck-1782350086

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - emla-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - emla-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
  - emla-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - emla-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### emla-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - emla-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### esguides-ecpbackendcheck-1782334375

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - esguides-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### estack-cache-ecpbackendcheck-1782334509

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - estack-cache-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### estack-dm-ecpbackendcheck-1782334734

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - estack-dm-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.2.1; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ota-ecpbackendcheck-1782332311

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ota-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ota-openapi:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ota-upload-platform-pack-1782332311

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - upload-pack (hub.easystack.io/production/escloud-linux-source-ota-openapi:latest; /upload_pack.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### roller-cached-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - roller-cached-db-init (hub.easystack.io/production/escloud-linux-source-busybox:latest; /cached_db_init.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### roller-restore

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - restore-main (hub.easystack.io/production/escloud-linux-source-busybox:latest; /bin/bash -c pushd
    /var/lib/coaster/scripts && python -u roller_restore_agent.py)
- Init containers:
  - -

### tag-crd-ecpbackendcheck-1782346732

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - tag-crd-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### topology-bootstrap-gqzt3

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - craftman-bootstrap (hub.easystack.io/production/escloud-linux-source-topology-base:7.0.1-alpha.103; /tmp/bootstrap.sh)
- Init containers:
  - -

### coaster-all

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - coaster-api (hub.easystack.io/production/escloud-linux-source-coaster-api:7.0.1-alpha.103; /tmp/coaster-start.sh
    start_api)
  - coaster-conductor (hub.easystack.io/production/escloud-linux-source-coaster-conductor:7.0.1-alpha.103;
    /tmp/coaster-start.sh start_conductor)
  - coaster-other (hub.easystack.io/production/escloud-linux-source-coaster-other:7.0.1-alpha.103; /tmp/puppet-start.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ota

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - dota (hub.easystack.io/production/escloud-linux-source-dota-agent:7.0.1-alpha.103; /tmp/easystack-ota.sh)
- Init containers:
  - -

### ota-openapi

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - nginx (hub.easystack.io/production/nginx:stable; image default entrypoint)
  - openapi (hub.easystack.io/production/escloud-linux-source-ota-openapi:7.0.1-alpha.103; /ota-openapi)
- Init containers:
  - -
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `automation-operators` | ReplicaSet | 1 | Running:1 |
| `automation-operators-bootstrap-xkx3p` | Job | 1 | Succeeded:1 |
| `coaster-all` | StatefulSet | 1 | Running:1 |
| `coaster-data-migration` | Job | 1 | Succeeded:1 |
| `coaster-db-init-v2` | Job | 1 | Succeeded:1 |
| `coaster-db-sync-7.0.1-alpha.103` | Job | 1 | Succeeded:1 |
| `coaster-ks-endpoints-v2` | Job | 1 | Succeeded:1 |
| `coaster-ks-service-v2` | Job | 1 | Succeeded:1 |
| `coaster-ks-user-v2` | Job | 1 | Succeeded:1 |
| `easystack` | ReplicaSet | 1 | Running:1 |
| `easystack-cache-api` | ReplicaSet | 3 | Running:3 |
| `ecms-create-secret-etcd` | Job | 1 | Succeeded:1 |
| `ecms-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `ecms-ks-user` | Job | 1 | Succeeded:1 |
| `ecms-restore-alerts` | Job | 1 | Succeeded:1 |
| `emla-apiserver` | ReplicaSet | 3 | Running:3 |
| `emla-controller-manager` | ReplicaSet | 3 | Running:3 |
| `emla-dashboard` | ReplicaSet | 3 | Running:3 |
| `emla-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `emla-grafana` | ReplicaSet | 3 | Running:3 |
| `emla-ks-endpoints` | Job | 1 | Succeeded:1 |
| `emla-ks-service` | Job | 1 | Succeeded:1 |
| `esdm-api` | ReplicaSet | 3 | Running:3 |
| `esguides` | ReplicaSet | 3 | Running:3 |
| `esguides-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `ess-automation` | ReplicaSet | 1 | Running:1 |
| `estack-cache-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `estack-dm-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `gpu-api` | ReplicaSet | 3 | Running:3 |
| `ota` | StatefulSet | 1 | Running:1 |
| `ota-dashboard` | ReplicaSet | 3 | Running:3 |
| `ota-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `ota-openapi` | StatefulSet | 1 | Running:1 |
| `ota-upload-platform-pack` | Job | 1 | Succeeded:1 |
| `roller-cached-db-init` | Job | 1 | Succeeded:1 |
| `roller-dashboard` | ReplicaSet | 3 | Running:3 |
| `roller-restore` | Job | 1 | Succeeded:1 |
| `tag-crd-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `topology-bootstrap-gqzt3` | Job | 1 | Succeeded:1 |
| `topology-operators` | ReplicaSet | 1 | Running:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `automation-operators-metrics` | ClusterIP | 8383/TCP, 8686/TCP |
| `openstack` | `coaster` | ExternalName | 80/TCP |
| `openstack` | `coaster-all` | ClusterIP | 8001/TCP |
| `openstack` | `easystack-cache-api` | ClusterIP | 8013/TCP |
| `openstack` | `ecms-172-16-10-2` | ClusterIP | 443/TCP |
| `openstack` | `emla` | ExternalName | 80/TCP |
| `openstack` | `emla-172-16-10-2` | ClusterIP | 443/TCP |
| `openstack` | `emla-apiserver` | ClusterIP | 9090/TCP, 9091/TCP |
| `openstack` | `emla-controller-manager` | ClusterIP | 8080/TCP, 8443/TCP |
| `openstack` | `emla-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `esguides-int` | ClusterIP | 80/TCP |
| `openstack` | `gpu-api` | ClusterIP | 80/TCP |
| `openstack` | `ota-dashboard` | ExternalName | 80/TCP |
| `openstack` | `ota-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `ota-nginx-int` | ClusterIP | 8081/TCP |
| `openstack` | `ota-openapi-int` | ClusterIP | 80/TCP |
| `openstack` | `roller-dashboard` | ClusterIP | 80/TCP |
