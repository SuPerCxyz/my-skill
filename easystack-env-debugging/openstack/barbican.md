# OpenStack barbican

`barbican` 组件 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `barbican` | `barbican` | `barbican-7.0.1-alpha.412` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `barbican` | Deployment | `barbican-api` | 3/3 ready | barbican-api | init |
| `barbican` | Deployment | `barbican-dashboard` | 3/3 ready | barbican-dashboard | init |
| `barbican` | Deployment | `barbican-dashboard-api` | 3/3 ready | barbican-dashboard-api | init |
| `barbican` | Deployment | `barbican-kms` | 3/3 ready | barbican-kms | init |
| `barbican` | Deployment | `barbican-kms-dashboard-api` | 3/3 ready | barbican-kms-dashboard-api | init |
| `barbican` | Deployment | `barbican-openapi` | 3/3 ready | barbican-openapi | init |
| `barbican` | Job | `barbican-db-init-v1.2.1` | succeeded=1, failed=0 | barbican-db-init | init |
| `barbican` | Job | `barbican-db-sync-v1.2.1` | succeeded=1, failed=0 | barbican-db-sync | init |
| `barbican` | Job | `barbican-ecpbackendcheck-1782369558` | succeeded=1, failed=0 | barbican-ecpbackendcheck | init |
| `barbican` | Job | `barbican-ks-endpoints-v1.2.1` | succeeded=1, failed=0 | key-manager-ks-endpoints-admin<br>key-manager-ks-endpoints-internal<br>key-manager-ks-endpoints-public | init |
| `barbican` | Job | `barbican-ks-service-v1.2.1` | succeeded=1, failed=0 | key-manager-ks-service-registration | init |
| `barbican` | Job | `barbican-ks-user-v1.2.1` | succeeded=1, failed=0 | barbican-ks-user | init |
| `barbican` | Job | `clean-kms-db-tables-v1.2.1` | succeeded=1, failed=0 | kms-db-tables-clean | init |
| `barbican` | Job | `kms-db-init-v1.2.1` | succeeded=1, failed=0 | kms-db-init | init |
| `barbican` | Job | `kms-db-sync-v1.2.1` | succeeded=1, failed=0 | kms-db-sync | init |
| `barbican` | Job | `kms-schedule-delete-v1.2.1-29706720` | succeeded=1, failed=0 | kms-schedule-delete | init |

## Container Details 容器详情

### barbican-api

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-api (hub.easystack.io/production/escloud-linux-source-barbican-api:7.0.1-alpha.412; /tmp/barbican.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-dashboard

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-dashboard (hub.easystack.io/production/escloud-linux-source-barbican-dashboard:7.0.1-alpha.412; /nginx.sh
    start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-dashboard-api

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-dashboard-api (hub.easystack.io/production/escloud-linux-source-barbican-dashboard-api:7.0.1-alpha.412;
    /barbican_dashboard_api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-kms

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-kms (hub.easystack.io/production/escloud-linux-source-barbican-kms:7.0.1-alpha.412; /barbican_kms.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-kms-dashboard-api

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-kms-dashboard-api (hub.easystack.io/production/escloud-linux-source-barbican-kms-dashboard-api:7.0.1-alpha.412;
    /barbican_kms_dashboard_api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-openapi

- Namespace: `barbican`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - barbican-openapi (hub.easystack.io/production/escloud-linux-source-barbican-openapi:7.0.1-alpha.412; /barbican-openapi)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-db-init-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - barbican-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-db-sync-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - barbican-db-sync (hub.easystack.io/production/escloud-linux-source-barbican-api:7.0.1-alpha.412; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-ecpbackendcheck-1782369558

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - barbican-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-barbican-api:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-ks-endpoints-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - key-manager-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - key-manager-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - key-manager-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-ks-service-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - key-manager-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### barbican-ks-user-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - barbican-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### clean-kms-db-tables-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - kms-db-tables-clean (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts;
    /clean_kms_database_tables.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### kms-db-init-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - kms-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### kms-db-sync-v1.2.1

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - kms-db-sync (hub.easystack.io/production/escloud-linux-source-barbican-kms:7.0.1-alpha.412; /sync_kms_database.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### kms-schedule-delete-v1.2.1-29706720

- Namespace: `barbican`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - kms-schedule-delete (hub.easystack.io/production/escloud-linux-source-barbican-api:7.0.1-alpha.412;
    /schedule_delete_key.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `barbican-api` | ReplicaSet | 3 | Running:3 |
| `barbican-dashboard` | ReplicaSet | 3 | Running:3 |
| `barbican-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `barbican-db-init-v1.2.1` | Job | 1 | Succeeded:1 |
| `barbican-db-sync-v1.2.1` | Job | 1 | Succeeded:1 |
| `barbican-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `barbican-kms` | ReplicaSet | 3 | Running:3 |
| `barbican-kms-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `barbican-ks-endpoints-v1.2.1` | Job | 1 | Succeeded:1 |
| `barbican-ks-service-v1.2.1` | Job | 1 | Succeeded:1 |
| `barbican-ks-user-v1.2.1` | Job | 1 | Succeeded:1 |
| `barbican-openapi` | ReplicaSet | 3 | Running:3 |
| `clean-kms-db-tables-v1.2.1` | Job | 1 | Succeeded:1 |
| `kms-db-init-v1.2.1` | Job | 1 | Succeeded:1 |
| `kms-db-sync-v1.2.1` | Job | 1 | Succeeded:1 |
| `kms-schedule-delete-v1.2.1` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `barbican` | `barbican` | ExternalName | 80/TCP |
| `barbican` | `barbican-api` | ClusterIP | 9311/TCP |
| `barbican` | `barbican-dashboard` | ExternalName | 80/TCP |
| `barbican` | `barbican-dashboard-api-int` | ClusterIP | 80/TCP |
| `barbican` | `barbican-dashboard-int` | ClusterIP | 8080/TCP |
| `barbican` | `barbican-kms-dashboard-api-int` | ClusterIP | 80/TCP |
| `barbican` | `barbican-kms-int` | ClusterIP | 80/TCP |
| `barbican` | `barbican-openapi` | ExternalName | 80/TCP |
| `barbican` | `barbican-openapi-int` | ClusterIP | 80/TCP |
