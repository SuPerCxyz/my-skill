# OpenStack ceilometer

`ceilometer` 组件 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `ceilometer` | `ceilometer-7.0.1-alpha.8` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | DaemonSet | `ceilometer-compute` | 3/3 ready | ceilometer-compute | init |
| `openstack` | Deployment | `ceilometer-api` | 3/3 ready | ceilometer-api | init |
| `openstack` | Deployment | `ceilometer-central` | 1/1 ready | ceilometer-central | init |
| `openstack` | Deployment | `ceilometer-collector` | 3/3 ready | ceilometer-collector | init |
| `openstack` | Deployment | `ceilometer-notification` | 3/3 ready | ceilometer-notification | init |
| `openstack` | Job | `ceilometer-db-init` | succeeded=1, failed=0 | ceilometer-db-init | init |
| `openstack` | Job | `ceilometer-db-init-mongodb` | succeeded=1, failed=0 | ceilometer-db-init-mongodb | init |
| `openstack` | Job | `ceilometer-db-sync` | succeeded=1, failed=0 | ceilometer-db-sync | init |
| `openstack` | Job | `ceilometer-ecpbackendcheck-1782347493` | succeeded=1, failed=0 | ceilometer-ecpbackendcheck | init |
| `openstack` | Job | `ceilometer-ks-endpoints` | succeeded=1, failed=0 | metering-ks-endpoints-admin<br>metering-ks-endpoints-internal<br>metering-ks-endpoints-public | init |
| `openstack` | Job | `ceilometer-ks-service` | succeeded=1, failed=0 | metering-ks-service-registration | init |
| `openstack` | Job | `ceilometer-ks-user` | succeeded=1, failed=0 | ceilometer-ks-user | init |

## Container Details 容器详情

### ceilometer-compute

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - ceilometer-compute (hub.easystack.io/production/escloud-linux-source-ceilometer-compute:7.0.1-alpha.8;
    /tmp/ceilometer-compute.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ceilometer-api (hub.easystack.io/production/escloud-linux-source-ceilometer-api:7.0.1-alpha.8; /tmp/ceilometer-api.sh
    start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-central

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - ceilometer-central (hub.easystack.io/production/escloud-linux-source-ceilometer-central:7.0.1-alpha.8;
    /tmp/ceilometer-central.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-collector

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ceilometer-collector (hub.easystack.io/production/escloud-linux-source-ceilometer-collector:7.0.1-alpha.8;
    /tmp/ceilometer-collector.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-notification

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ceilometer-notification (hub.easystack.io/production/escloud-linux-source-ceilometer-notification:7.0.1-alpha.8;
    /tmp/ceilometer-notification.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceilometer-db-init (hub.easystack.io/production/escloud-linux-source-ceilometer-api:6.1.3-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-db-init-mongodb

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceilometer-db-init-mongodb (hub.easystack.io/production/mongodb:8.0.13-ubuntu2204-es; /tmp/db-init-mongodb.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceilometer-db-sync (hub.easystack.io/production/escloud-linux-source-ceilometer-api:6.1.3-lts; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-ecpbackendcheck-1782347493

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceilometer-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - metering-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - metering-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - metering-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - metering-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ceilometer-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceilometer-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `ceilometer-api` | ReplicaSet | 3 | Running:3 |
| `ceilometer-central` | ReplicaSet | 1 | Running:1 |
| `ceilometer-collector` | ReplicaSet | 3 | Running:3 |
| `ceilometer-compute` | DaemonSet | 3 | Running:3 |
| `ceilometer-db-init` | Job | 1 | Succeeded:1 |
| `ceilometer-db-init-mongodb` | Job | 1 | Succeeded:1 |
| `ceilometer-db-sync` | Job | 1 | Succeeded:1 |
| `ceilometer-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `ceilometer-ks-endpoints` | Job | 1 | Succeeded:1 |
| `ceilometer-ks-service` | Job | 1 | Succeeded:1 |
| `ceilometer-ks-user` | Job | 1 | Succeeded:1 |
| `ceilometer-notification` | ReplicaSet | 3 | Running:3 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `ceilometer` | ExternalName | 80/TCP |
| `openstack` | `ceilometer-api` | ClusterIP | 8777/TCP |
