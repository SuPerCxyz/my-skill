# OpenStack cinder

记录 `cinder` 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `cinder` | `cinder-7.0.1-alpha.30` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `cinder-api` | 3/3 ready | cinder-api | init |
| `openstack` | Deployment | `cinder-dashboard` | 3/3 ready | cinder-dashboard | init |
| `openstack` | Deployment | `cinder-golem` | 3/3 ready | golem | init |
| `openstack` | Deployment | `cinder-scheduler` | 3/3 ready | cinder-scheduler | init |
| `openstack` | Deployment | `cinder-volume` | 3/3 ready | cinder-volume | init<br>ceph-keyring-placement |
| `openstack` | Job | `cinder-bootstrap` | succeeded=1, failed=0 | cinder-bootstrap | init |
| `openstack` | Job | `cinder-db-init` | succeeded=1, failed=0 | cinder-db-init | init |
| `openstack` | Job | `cinder-db-sync` | succeeded=1, failed=0 | cinder-db-sync | init |
| `openstack` | Job | `cinder-domain-quota-allocated-sync` | succeeded=1, failed=0 | domain-quota-allocated-sync | init |
| `openstack` | Job | `cinder-ecpbackendcheck-1782347874` | succeeded=1, failed=0 | cinder-ecpbackendcheck | init |
| `openstack` | Job | `cinder-init-project-quotas` | succeeded=1, failed=0 | init-project-quotas | init |
| `openstack` | Job | `cinder-ks-endpoints` | succeeded=1, failed=0 | volumev2-ks-endpoints-admin<br>volumev2-ks-endpoints-internal<br>volumev2-ks-endpoints-public<br>volume-ks-endpoints-admin<br>volume-ks-endpoints-internal<br>volume-ks-endpoints-public<br>volumev3-ks-endpoints-admin<br>volumev3-ks-endpoints-internal<br>volumev3-ks-endpoints-public | init |
| `openstack` | Job | `cinder-ks-service` | succeeded=1, failed=0 | volumev2-ks-service-registration<br>volume-ks-service-registration<br>volumev3-ks-service-registration | init |
| `openstack` | Job | `cinder-ks-user` | succeeded=1, failed=0 | cinder-ks-user | init |
| `openstack` | Job | `cinder-storage-init-v1` | succeeded=1, failed=0 | cinder-storage-init | init<br>ceph-keyring-placement |

## Container Details 容器详情

### cinder-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - cinder-api (hub.easystack.io/production/escloud-linux-source-cinder-api:7.0.1-alpha.30; /tmp/cinder-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - cinder-dashboard (hub.easystack.io/production/escloud-linux-source-cinder-dashboard:7.0.1-alpha.30; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-golem

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - golem (hub.easystack.io/production/escloud-linux-source-cinder-golem:7.0.1-alpha.30; /tmp/golem.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-scheduler

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - cinder-scheduler (hub.easystack.io/production/escloud-linux-source-cinder-scheduler:7.0.1-alpha.30;
    /tmp/cinder-scheduler.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-volume

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - cinder-volume (hub.easystack.io/production/escloud-linux-source-cinder-volume:7.0.1-alpha.30; /tmp/cinder-volume.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-cinder-volume:7.0.1-alpha.30)

### cinder-bootstrap

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-bootstrap (hub.easystack.io/production/escloud-linux-source-cinder-bootstrap:latest; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-db-sync (hub.easystack.io/production/escloud-linux-source-cinder-api:latest; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-domain-quota-allocated-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - domain-quota-allocated-sync (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/domain-quota-allocated-sync.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-ecpbackendcheck-1782347874

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-init-project-quotas

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - init-project-quotas (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/init_project_quota.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - volumev2-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volumev2-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volumev2-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volume-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
  - volume-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volume-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volumev3-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volumev3-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - volumev3-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - volumev2-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
  - volume-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
  - volumev3-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### cinder-storage-init-v1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - cinder-storage-init (hub.easystack.io/production/escloud-linux-ceph-daemon:14.2.22-14.es7_1; /tmp/storage-init.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-ceph-daemon:14.2.22-14.es7_1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `cinder` | ReplicaSet | 3 | Running:3 |
| `cinder-api` | ReplicaSet | 3 | Running:3 |
| `cinder-bootstrap` | Job | 1 | Succeeded:1 |
| `cinder-dashboard` | ReplicaSet | 3 | Running:3 |
| `cinder-db-init` | Job | 1 | Succeeded:1 |
| `cinder-db-sync` | Job | 1 | Succeeded:1 |
| `cinder-domain-quota-allocated-sync` | Job | 1 | Succeeded:1 |
| `cinder-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `cinder-init-project-quotas` | Job | 1 | Succeeded:1 |
| `cinder-ks-endpoints` | Job | 1 | Succeeded:1 |
| `cinder-ks-service` | Job | 1 | Succeeded:1 |
| `cinder-ks-user` | Job | 1 | Succeeded:1 |
| `cinder-scheduler` | ReplicaSet | 3 | Running:3 |
| `cinder-storage-init-v1` | Job | 1 | Succeeded:1 |
| `cinder-volume` | ReplicaSet | 3 | Running:3 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `cinder` | ExternalName | 80/TCP |
| `openstack` | `cinder-api` | ClusterIP | 8776/TCP |
| `openstack` | `cinder-dashboard` | ExternalName | 80/TCP |
| `openstack` | `cinder-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `cinder-golem` | ClusterIP | 8192/TCP |

