# OpenStack gnocchi

`gnocchi` 组件 pod、启动方式和排查入口参考。

## Helm Release

当前文档未记录对应 Helm release。

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | DaemonSet | `gnocchi-metricd` | 3/3 ready | gnocchi-metricd | init<br>ceph-keyring-placement |
| `openstack` | DaemonSet | `gnocchi-statsd` | 3/3 ready | gnocchi-statsd | init<br>ceph-keyring-placement |
| `openstack` | Deployment | `gnocchi-api` | 3/3 ready | gnocchi-api | init<br>ceph-keyring-placement |
| `openstack` | Job | `gnocchi-db-init-indexer` | succeeded=1, failed=0 | gnocchi-db-init-indexer | init |
| `openstack` | Job | `gnocchi-db-init-keystone` | succeeded=1, failed=0 | keystone-db-init | init |
| `openstack` | Job | `gnocchi-db-sync` | succeeded=1, failed=0 | gnocchi-db-sync | init<br>ceph-keyring-placement |
| `openstack` | Job | `gnocchi-ks-endpoints` | succeeded=1, failed=0 | metric-ks-endpoints-admin<br>metric-ks-endpoints-internal<br>metric-ks-endpoints-public | init |
| `openstack` | Job | `gnocchi-ks-service` | succeeded=1, failed=0 | metric-ks-service-registration | init |
| `openstack` | Job | `gnocchi-ks-user` | succeeded=1, failed=0 | gnocchi-ks-user | init |
| `openstack` | Job | `gnocchi-storage-init-6.1.2` | succeeded=1, failed=0 | gnocchi-storage-init | init<br>ceph-keyring-placement |

## Container Details 容器详情

### gnocchi-metricd

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - gnocchi-metricd (hub.easystack.io/production/escloud-linux-source-gnocchi-metricd:7.0.1-alpha.8;
    /tmp/gnocchi-metricd.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-gnocchi-api:7.0.1-alpha.8)

### gnocchi-statsd

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - gnocchi-statsd (hub.easystack.io/production/escloud-linux-source-gnocchi-statsd:7.0.1-alpha.8; /tmp/gnocchi-statsd.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-gnocchi-api:7.0.1-alpha.8)

### gnocchi-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - gnocchi-api (hub.easystack.io/production/escloud-linux-source-gnocchi-api:7.0.1-alpha.8; /tmp/gnocchi-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-gnocchi-api:7.0.1-alpha.8)

### gnocchi-db-init-indexer

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - gnocchi-db-init-indexer (hub.easystack.io/production/escloud-linux-source-gnocchi-api:latest; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### gnocchi-db-init-keystone

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-db-init (hub.easystack.io/production/escloud-linux-source-gnocchi-api:latest; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### gnocchi-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - gnocchi-db-sync (hub.easystack.io/production/escloud-linux-source-gnocchi-api:latest; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-gnocchi-api:latest)

### gnocchi-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - metric-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
  - metric-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - metric-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### gnocchi-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - metric-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### gnocchi-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - gnocchi-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### gnocchi-storage-init-6.1.2

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - gnocchi-storage-init (hub.easystack.io/production/escloud-linux-ceph-daemon:14.2.22-14.es7_1; /tmp/storage-init.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-gnocchi-api:latest)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `gnocchi-api` | ReplicaSet | 3 | Running:3 |
| `gnocchi-db-init-indexer` | Job | 1 | Succeeded:1 |
| `gnocchi-db-init-keystone` | Job | 1 | Succeeded:1 |
| `gnocchi-db-sync` | Job | 1 | Succeeded:1 |
| `gnocchi-ks-endpoints` | Job | 1 | Succeeded:1 |
| `gnocchi-ks-service` | Job | 1 | Succeeded:1 |
| `gnocchi-ks-user` | Job | 1 | Succeeded:1 |
| `gnocchi-metricd` | DaemonSet | 3 | Running:3 |
| `gnocchi-statsd` | DaemonSet | 3 | Running:3 |
| `gnocchi-storage-init-6.1.2` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `gnocchi` | ExternalName | 80/TCP |
| `openstack` | `gnocchi-api` | ClusterIP | 8041/TCP |
| `openstack` | `gnocchi-statsd` | ClusterIP | 8125/TCP |
