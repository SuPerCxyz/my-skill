# OpenStack nova

`nova` 组件 pod、启动方式和排查入口参考。

Nova maintenance、cell management、host maintenance、evacuation、migration debugging 等特殊操作说明统一见 [../special-operations.md](../special-operations.md#nova-maintenance-pod)。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `nova` | `nova-7.0.1-alpha.127` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | DaemonSet | `nova-compute` | 3/3 ready | nova-compute | init<br>nova-compute-init<br>ceph-keyring-placement<br>nova-compute-vnc-init |
| `openstack` | Deployment | `nova-api-metadata` | 3/3 ready | nova-api | init<br>nova-api-metadata-init |
| `openstack` | Deployment | `nova-api-osapi` | 3/3 ready | nova-osapi | init |
| `openstack` | Deployment | `nova-conductor` | 3/3 ready | nova-conductor | init |
| `openstack` | Deployment | `nova-dashboard` | 3/3 ready | nova-dashboard | init |
| `openstack` | Deployment | `nova-dashboard-api` | 3/3 ready | nova-dashboard-api | init |
| `openstack` | Deployment | `nova-maintenance` | 1/1 ready | nova-maintenance | - |
| `openstack` | Deployment | `nova-novncproxy` | 3/3 ready | nova-novncproxy | init<br>nova-novncproxy-init<br>nova-novncproxy-init-assets |
| `openstack` | Deployment | `nova-operator` | 1/1 ready | nova-operator | - |
| `openstack` | Deployment | `nova-placement-api` | 3/3 ready | nova-placement-api | init |
| `openstack` | Deployment | `nova-scheduler` | 3/3 ready | nova-scheduler | init |
| `openstack` | Job | `nova-allocation-audit-heal-29706900` | succeeded=1, failed=0 | allocation-audit-heal | init |
| `openstack` | Job | `nova-archive-deleted-rows-29706720` | succeeded=1, failed=0 | nova-archive-deleted-rows | init |
| `openstack` | Job | `nova-bootstrap-v1-5.0.4` | succeeded=1, failed=0 | nova-bootstrap | init |
| `openstack` | Job | `nova-cell-setup` | succeeded=1, failed=0 | nova-cell-setup | init |
| `openstack` | Job | `nova-db-init` | succeeded=1, failed=0 | nova-db-init<br>nova-db-init-api<br>nova-db-init-cell0<br>placement-db-init | init |
| `openstack` | Job | `nova-db-sync-7.0.1` | succeeded=1, failed=0 | nova-db-sync<br>placement-db-sync | init |
| `openstack` | Job | `nova-domain-quota-allocated-sync-v1` | succeeded=1, failed=0 | domain-quota-allocated-sync | init |
| `openstack` | Job | `nova-ecpbackendcheck-1782350084` | succeeded=1, failed=0 | nova-ecpbackendcheck | init |
| `openstack` | Job | `nova-init-project-quotas-v1` | succeeded=1, failed=0 | init-project-quotas | init |
| `openstack` | Job | `nova-ks-endpoints` | succeeded=1, failed=0 | compute-ks-endpoints-admin<br>compute-ks-endpoints-internal<br>compute-ks-endpoints-public | init |
| `openstack` | Job | `nova-ks-service` | succeeded=1, failed=0 | compute-ks-service-registration | init |
| `openstack` | Job | `nova-ks-user` | succeeded=1, failed=0 | nova-ks-user | init |
| `openstack` | Job | `nova-service-cleaner-29706720` | succeeded=1, failed=0 | heat-engine-cleaner | init |

## Container Details 容器详情

### nova-compute

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - nova-compute (hub.easystack.io/production/escloud-linux-source-nova-compute:7.0.1-alpha.127; /tmp/nova-compute.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - nova-compute-init (hub.easystack.io/production/escloud-linux-source-nova-compute:7.0.1-alpha.127)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-nova-compute:7.0.1-alpha.127)
  - nova-compute-vnc-init (hub.easystack.io/production/escloud-linux-source-nova-compute:7.0.1-alpha.127)

### nova-api-metadata

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-api (hub.easystack.io/production/escloud-linux-source-nova-api:7.0.1-alpha.127; /tmp/nova-api-metadata.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - nova-api-metadata-init (hub.easystack.io/production/escloud-linux-source-nova-api:7.0.1-alpha.127)

### nova-api-osapi

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-osapi (hub.easystack.io/production/escloud-linux-source-nova-api:7.0.1-alpha.127; /tmp/nova-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-conductor

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-conductor (hub.easystack.io/production/escloud-linux-source-nova-conductor:7.0.1-alpha.127; /tmp/nova-conductor.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-dashboard (hub.easystack.io/production/escloud-linux-source-nova-dashboard:7.0.1-alpha.127; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-dashboard-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-dashboard-api (hub.easystack.io/production/escloud-linux-source-nova-dashboard-api:7.0.1-alpha.127;
    /nova-dashboard-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-maintenance

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - nova-maintenance (hub.easystack.io/production/escloud-linux-source-nova-api:7.0.1-alpha.127; /tmp/maintenance-worker.sh)
- Init containers:
  - -

### nova-novncproxy

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-novncproxy (hub.easystack.io/production/escloud-linux-source-nova-novncproxy:7.0.1-alpha.127;
    /tmp/nova-novncproxy.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - nova-novncproxy-init (hub.easystack.io/production/escloud-linux-source-nova-novncproxy:7.0.1-alpha.127)
  - nova-novncproxy-init-assets (hub.easystack.io/production/escloud-linux-source-nova-novncproxy:7.0.1-alpha.127)

### nova-operator

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - nova-operator (hub.easystack.io/production/escloud-linux-source-nova-operator:7.0.1-alpha.127; /tmp/nova-operator.sh)
- Init containers:
  - -

### nova-placement-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-placement-api (hub.easystack.io/production/escloud-linux-source-nova-placement-api:7.0.1-alpha.127;
    /tmp/nova-placement-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-scheduler

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nova-scheduler (hub.easystack.io/production/escloud-linux-source-nova-scheduler:7.0.1-alpha.127; /tmp/nova-scheduler.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-allocation-audit-heal-29706900

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - allocation-audit-heal (hub.easystack.io/production/escloud-linux-source-nova-api:7.0.1-alpha.127;
    /tmp/allocation-audit-heal.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-archive-deleted-rows-29706720

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-archive-deleted-rows (hub.easystack.io/production/escloud-linux-source-nova-conductor:7.0.1-alpha.127;
    /tmp/nova-archive-deleted-rows.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-bootstrap-v1-5.0.4

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-bootstrap (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-cell-setup

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-cell-setup (hub.easystack.io/production/escloud-linux-source-nova-api:latest; /tmp/cell-setup.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
  - nova-db-init-api (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
  - nova-db-init-cell0 (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
  - placement-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-db-sync-7.0.1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-db-sync (hub.easystack.io/production/escloud-linux-source-nova-api:latest; /tmp/db-sync.sh)
  - placement-db-sync (hub.easystack.io/production/escloud-linux-source-nova-placement-api:latest;
    /tmp/db-sync-placement.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-domain-quota-allocated-sync-v1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - domain-quota-allocated-sync (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/domain-quota-allocated-sync.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-ecpbackendcheck-1782350084

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-init-project-quotas-v1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - init-project-quotas (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/init_project_quota.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - compute-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - compute-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - compute-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - compute-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - nova-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### nova-service-cleaner-29706720

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - heat-engine-cleaner (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/nova-service-cleaner.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `nova-allocation-audit-heal` | Job | 1 | Succeeded:1 |
| `nova-api` | ReplicaSet | 3 | Running:3 |
| `nova-api-metadata` | ReplicaSet | 3 | Running:3 |
| `nova-archive-deleted-rows` | Job | 1 | Succeeded:1 |
| `nova-bootstrap-v1-5.0.4` | Job | 1 | Succeeded:1 |
| `nova-cell-setup` | Job | 1 | Succeeded:1 |
| `nova-compute` | DaemonSet | 3 | Running:3 |
| `nova-conductor` | ReplicaSet | 3 | Running:3 |
| `nova-dashboard` | ReplicaSet | 3 | Running:3 |
| `nova-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `nova-db-init` | Job | 1 | Succeeded:1 |
| `nova-db-sync-7.0.1` | Job | 1 | Succeeded:1 |
| `nova-domain-quota-allocated-sync-v1` | Job | 1 | Succeeded:1 |
| `nova-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `nova-init-project-quotas-v1` | Job | 1 | Succeeded:1 |
| `nova-ks-endpoints` | Job | 1 | Succeeded:1 |
| `nova-ks-service` | Job | 1 | Succeeded:1 |
| `nova-ks-user` | Job | 1 | Succeeded:1 |
| `nova-maintenance` | ReplicaSet | 1 | Running:1 |
| `nova-novncproxy` | ReplicaSet | 3 | Running:3 |
| `nova-operator` | ReplicaSet | 1 | Running:1 |
| `nova-placement-api` | ReplicaSet | 3 | Running:3 |
| `nova-scheduler` | ReplicaSet | 3 | Running:3 |
| `nova-service-cleaner` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `nova` | ExternalName | 80/TCP |
| `openstack` | `nova-api` | ClusterIP | 8774/TCP |
| `openstack` | `nova-dashboard` | ExternalName | 80/TCP |
| `openstack` | `nova-dashboard-api` | ClusterIP | 80/TCP |
| `openstack` | `nova-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `nova-metadata` | ClusterIP | 8775/TCP |
| `openstack` | `nova-novncproxy` | ClusterIP | 6080/TCP |
