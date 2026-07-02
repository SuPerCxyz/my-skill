# OpenStack glance

`glance` 组件 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `glance` | `glance-7.0.1-alpha.22` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `glance-dashboard` | 3/3 ready | glance-dashboard | init |
| `openstack` | Deployment | `glance-dashboard-api` | 3/3 ready | glance-dashboard-api | init |
| `openstack` | Job | `glance-bootstrap` | succeeded=1, failed=0 | glance-bootstrap | init |
| `openstack` | Job | `glance-db-init` | succeeded=1, failed=0 | glance-db-init | init |
| `openstack` | Job | `glance-db-sync` | succeeded=1, failed=0 | glance-db-sync | init |
| `openstack` | Job | `glance-ecpbackendcheck-1782349002` | succeeded=1, failed=0 | glance-ecpbackendcheck | init |
| `openstack` | Job | `glance-ks-endpoints` | succeeded=1, failed=0 | image-ks-endpoints-admin<br>image-ks-endpoints-internal<br>image-ks-endpoints-public | init |
| `openstack` | Job | `glance-ks-service` | succeeded=1, failed=0 | image-ks-service-registration | init |
| `openstack` | Job | `glance-ks-user` | succeeded=1, failed=0 | glance-ks-user | init |
| `openstack` | Job | `glance-scrubber-29706840` | succeeded=1, failed=0 | glance-scrubber | init<br>glance-perms<br>ceph-keyring-placement |
| `openstack` | Job | `glance-storage-init-v1` | succeeded=1, failed=0 | glance-storage-init | init<br>ceph-keyring-placement |
| `openstack` | StatefulSet | `glance-api` | 3/3 ready | glance-api<br>virt-v2v | init<br>glance-perms<br>ceph-keyring-placement |

## Container Details 容器详情

### glance-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - glance-dashboard (hub.easystack.io/production/escloud-linux-source-glance-dashboard:7.0.1-alpha.22; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-dashboard-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - glance-dashboard-api (hub.easystack.io/production/escloud-linux-source-glance-dashboard-api:7.0.1-alpha.22;
    /glance-dashboard-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-bootstrap

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-bootstrap (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-db-sync (hub.easystack.io/production/escloud-linux-source-glance-api:latest; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-ecpbackendcheck-1782349002

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - image-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
  - image-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - image-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - image-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### glance-scrubber-29706840

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-scrubber (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22; /tmp/glance-scrubber.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - glance-perms (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22)

### glance-storage-init-v1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - glance-storage-init (hub.easystack.io/production/escloud-linux-ceph-daemon:14.2.22-14.es7_1; /tmp/storage-init.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-glance-api:latest)

### glance-api

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - glance-api (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22; /tmp/glance-api.sh start)
  - virt-v2v (hub.easystack.io/production/virt-v2v:2.5.6; /tmp/glance-api-virt-v2v.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - glance-perms (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-glance-api:7.0.1-alpha.22)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `glance-api` | StatefulSet | 3 | Running:3 |
| `glance-bootstrap` | Job | 1 | Succeeded:1 |
| `glance-dashboard` | ReplicaSet | 3 | Running:3 |
| `glance-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `glance-db-init` | Job | 1 | Succeeded:1 |
| `glance-db-sync` | Job | 1 | Succeeded:1 |
| `glance-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `glance-ks-endpoints` | Job | 1 | Succeeded:1 |
| `glance-ks-service` | Job | 1 | Succeeded:1 |
| `glance-ks-user` | Job | 1 | Succeeded:1 |
| `glance-scrubber` | Job | 1 | Succeeded:1 |
| `glance-storage-init-v1` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `glance` | ExternalName | 80/TCP |
| `openstack` | `glance-api` | ClusterIP | 9292/TCP |
| `openstack` | `glance-dashboard` | ExternalName | 80/TCP |
| `openstack` | `glance-dashboard-api` | ClusterIP | 80/TCP |
| `openstack` | `glance-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `glance-storagepub-api` | ClusterIP | 9292/TCP |
