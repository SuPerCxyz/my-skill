# OpenStack horizon

`horizon` 组件 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `horizon` | `horizon-7.0.1-alpha.103` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `horizon` | 3/3 ready | nginx<br>horizon | init |
| `openstack` | Job | `horizon-cached-db-init-631` | succeeded=1, failed=0 | horizon-cached-db-init | init |
| `openstack` | Job | `horizon-ecpbackendcheck-1782348112` | succeeded=1, failed=0 | horizon-ecpbackendcheck | init |

## Container Details 容器详情

### horizon

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - nginx (hub.easystack.io/production/escloud-linux-source-horizon:7.0.1-alpha.103; /nginx.sh start)
  - horizon (hub.easystack.io/production/escloud-linux-source-horizon:7.0.1-alpha.103; /horizon.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### horizon-cached-db-init-631

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - horizon-cached-db-init (hub.easystack.io/production/escloud-linux-source-busybox:6.2.1; /cached_db_init.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### horizon-ecpbackendcheck-1782348112

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - horizon-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.2.1; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `horizon` | ReplicaSet | 3 | Running:3 |
| `horizon-cached-db-init` | Job | 1 | Succeeded:1 |
| `horizon-ecpbackendcheck` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `horizon` | ExternalName | 80/TCP |
| `openstack` | `horizon-int` | ClusterIP | 80/TCP |
| `openstack` | `horizon-static-int` | ClusterIP | 80/TCP |
