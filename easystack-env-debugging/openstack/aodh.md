# OpenStack aodh

记录 `aodh` 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

当前文档未记录对应 Helm release。

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `aodh-api` | 3/3 ready | aodh-api | init |
| `openstack` | Deployment | `aodh-evaluator` | 1/1 ready | aodh-evaluator | init |
| `openstack` | Deployment | `aodh-listener` | 3/3 ready | aodh-listener | init |
| `openstack` | Deployment | `aodh-notifier` | 3/3 ready | aodh-notifier | init |
| `openstack` | Job | `aodh-db-init` | succeeded=1, failed=0 | aodh-db-init | init |
| `openstack` | Job | `aodh-db-sync` | succeeded=1, failed=0 | aodh-db-sync | init |
| `openstack` | Job | `aodh-ks-endpoints` | succeeded=1, failed=0 | alarming-ks-endpoints-admin<br>alarming-ks-endpoints-internal<br>alarming-ks-endpoints-public | init |
| `openstack` | Job | `aodh-ks-service` | succeeded=1, failed=0 | alarming-ks-service-registration | init |
| `openstack` | Job | `aodh-ks-user` | succeeded=1, failed=0 | aodh-ks-user | init |

## Container Details 容器详情

### aodh-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - aodh-api (hub.easystack.io/production/escloud-linux-source-aodh-api:7.0.1-alpha.8; /tmp/aodh-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-evaluator

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - aodh-evaluator (hub.easystack.io/production/escloud-linux-source-aodh-evaluator:7.0.1-alpha.8; /tmp/aodh-evaluator.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-listener

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - aodh-listener (hub.easystack.io/production/escloud-linux-source-aodh-listener:7.0.1-alpha.8; /tmp/aodh-listener.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-notifier

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - aodh-notifier (hub.easystack.io/production/escloud-linux-source-aodh-notifier:7.0.1-alpha.8; /tmp/aodh-notifier.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - aodh-db-init (hub.easystack.io/production/escloud-linux-source-aodh-api:latest; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - aodh-db-sync (hub.easystack.io/production/escloud-linux-source-aodh-api:latest; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - alarming-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - alarming-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - alarming-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - alarming-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### aodh-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - aodh-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `aodh-api` | ReplicaSet | 3 | Running:3 |
| `aodh-db-init` | Job | 1 | Succeeded:1 |
| `aodh-db-sync` | Job | 1 | Succeeded:1 |
| `aodh-evaluator` | ReplicaSet | 1 | Running:1 |
| `aodh-ks-endpoints` | Job | 1 | Succeeded:1 |
| `aodh-ks-service` | Job | 1 | Succeeded:1 |
| `aodh-ks-user` | Job | 1 | Succeeded:1 |
| `aodh-listener` | ReplicaSet | 3 | Running:3 |
| `aodh-notifier` | ReplicaSet | 3 | Running:3 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `aodh` | ExternalName | 80/TCP |
| `openstack` | `aodh-api` | ClusterIP | 8042/TCP |

