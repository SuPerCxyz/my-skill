# OpenStack Baremetal Ironic

记录裸金属相关组件的部署情况。裸金属服务主体部署在 `ironic` namespace, 但 `nova-compute-ironic` 位于 `openstack` namespace。

后续环境可能继续扩展更多 ironic 或 baremetal 组件。

## Namespace 边界

| Namespace | 内容 |
|-----------|------|
| `ironic` | `ironic-api`, `ironic-conductor-default`, `ironic-dashboard`, `ironic-dashboard-api`, `ironic-pushgateway` 和相关初始化/清理 Job |
| `openstack` | `nova-compute-ironic` StatefulSet, 属于 Nova 与裸金属对接侧组件 |

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `ironic` | `ceph-ironic-config` | `ceph-7.0.1-alpha.85` | DEPLOYED |
| `ironic` | `ironic` | `ironic-5.0.1` | DEPLOYED |
| `openstack` | `nova` | `nova-7.0.1-alpha.126` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `ironic` | Deployment | `ironic-api` | 3/3 ready | ironic-api | init |
| `ironic` | Deployment | `ironic-dashboard` | 3/3 ready | ironic-dashboard | init |
| `ironic` | Deployment | `ironic-dashboard-api` | 3/3 ready | ironic-dashboard-api | - |
| `ironic` | Job | `ceph-namespace-client-key-generator-qjnh3` | succeeded=1, failed=0 | ceph-storage-keys-generator | - |
| `ironic` | Job | `ironic-bootstrap-6.3.1` | succeeded=1, failed=0 | ironic-bootstrap | init |
| `ironic` | Job | `ironic-db-init-6.3.1` | succeeded=1, failed=0 | ironic-db-init | init |
| `ironic` | Job | `ironic-db-sync-6.3.1` | succeeded=1, failed=0 | ironic-db-sync | init |
| `ironic` | Job | `ironic-ecpbackendcheck-1782196205` | succeeded=1, failed=0 | ironic-ecpbackendcheck | init |
| `ironic` | Job | `ironic-ks-endpoints-6.3.1` | succeeded=1, failed=0 | baremetal-ks-endpoints-admin<br>baremetal-ks-endpoints-internal<br>baremetal-ks-endpoints-public | init |
| `ironic` | Job | `ironic-ks-service-6.3.1` | succeeded=1, failed=0 | baremetal-ks-service-registration | init |
| `ironic` | Job | `ironic-ks-user-6.3.1` | succeeded=1, failed=0 | ironic-ks-user | init |
| `ironic` | Job | `pushgateway-data-cleaner-29707620` | succeeded=1, failed=0 | pushgateway-data-cleaner | init |
| `ironic` | Job | `pushgateway-data-cleaner-29707630` | succeeded=1, failed=0 | pushgateway-data-cleaner | init |
| `ironic` | Job | `pushgateway-data-cleaner-29707640` | succeeded=1, failed=0 | pushgateway-data-cleaner | init |
| `ironic` | StatefulSet | `ironic-conductor-default` | 1/1 ready | ironic-conductor<br>ironic-conductor-pxe<br>ironic-conductor-http | init<br>ironic-conductor-pxe-init<br>ironic-conductor-init<br>ironic-conductor-http-init |
| `ironic` | StatefulSet | `ironic-pushgateway` | 3/3 ready | ironic-pushgateway<br>ironic-pushgateway-http | init |
| `openstack` | StatefulSet | `nova-compute-ironic` | 3/3 ready | nova-compute-ironic | init<br>nova-compute-ironic-init |

## Container Details 容器详情

### ironic-api

- Namespace: `ironic`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ironic-api (hub.easystack.io/arm64v8/escloud-linux-source-ironic-api:7.0.1-alpha.4; /tmp/ironic-api.sh start)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-dashboard

- Namespace: `ironic`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ironic-dashboard (hub.easystack.io/arm64v8/escloud-linux-source-ironic-dashboard:7.0.1-alpha.4; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-dashboard-api

- Namespace: `ironic`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ironic-dashboard-api (hub.easystack.io/arm64v8/escloud-linux-source-ironic-dashboard-api:7.0.1-alpha.4;
    /ironic_dashboard_api.sh start)
- Init containers:
  - -

### ceph-namespace-client-key-generator-qjnh3

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-storage-keys-generator (hub.easystack.io/arm64v8/ceph-config-helper:latest; /opt/ceph/ceph-namespace-client-key.sh)
- Init containers:
  - -

### ironic-bootstrap-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ironic-bootstrap (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-db-init-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ironic-db-init (hub.easystack.io/arm64v8/escloud-linux-source-ironic-api:latest; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-db-sync-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ironic-db-sync (hub.easystack.io/arm64v8/escloud-linux-source-ironic-api:latest; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-ecpbackendcheck-1782196205

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ironic-ecpbackendcheck (hub.easystack.io/arm64v8/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-ks-endpoints-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - baremetal-ks-endpoints-admin (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-endpoints.sh)
  - baremetal-ks-endpoints-internal (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
  - baremetal-ks-endpoints-public (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-ks-service-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - baremetal-ks-service-registration (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-ks-user-6.3.1

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ironic-ks-user (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### pushgateway-data-cleaner-29707620

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - pushgateway-data-cleaner (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/pushgateway-data-cleaner.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### pushgateway-data-cleaner-29707630

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - pushgateway-data-cleaner (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/pushgateway-data-cleaner.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### pushgateway-data-cleaner-29707640

- Namespace: `ironic`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - pushgateway-data-cleaner (hub.easystack.io/arm64v8/escloud-linux-source-heat-engine:6.1.1-lts;
    /tmp/pushgateway-data-cleaner.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### ironic-conductor-default

- Namespace: `ironic`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - ironic-conductor (hub.easystack.io/arm64v8/escloud-linux-source-ironic-conductor:7.0.1-alpha.4;
    /tmp/ironic-conductor.sh)
  - ironic-conductor-pxe (hub.easystack.io/arm64v8/escloud-linux-source-ironic-pxe:7.0.1-alpha.4;
    /tmp/ironic-conductor-pxe.sh)
  - ironic-conductor-http (hub.easystack.io/arm64v8/nginx:1.13; /tmp/ironic-conductor-http.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)
  - ironic-conductor-pxe-init (hub.easystack.io/arm64v8/escloud-linux-source-ironic-pxe:7.0.1-alpha.4)
  - ironic-conductor-init (hub.easystack.io/arm64v8/escloud-linux-source-ironic-conductor:7.0.1-alpha.4)
  - ironic-conductor-http-init (hub.easystack.io/arm64v8/escloud-linux-source-ironic-conductor:7.0.1-alpha.4)

### ironic-pushgateway

- Namespace: `ironic`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - ironic-pushgateway (hub.easystack.io/arm64v8/escloud-linux-source-ironic-pushgateway:7.0.1-alpha.4;
    /tmp/ironic-pushgateway.sh)
  - ironic-pushgateway-http (hub.easystack.io/arm64v8/escloud-linux-source-ironic-pushgateway:7.0.1-alpha.4;
    /tmp/ironic-pushgateway-http.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)

### nova-compute-ironic

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - nova-compute-ironic (hub.easystack.io/arm64v8/escloud-linux-source-nova-compute-ironic:7.0.1-alpha.4;
    /tmp/nova-compute-ironic.sh)
- Init containers:
  - init (hub.easystack.io/arm64v8/kubernetes-entrypoint:v0.2.1)
  - nova-compute-ironic-init (hub.easystack.io/arm64v8/escloud-linux-source-nova-compute-ironic:7.0.1-alpha.4)
## Pod 分布

| Namespace | Pod 组 | Owner 类型 | 数量 | 状态 |
|-----------|--------|------------|------|------|
| `ironic` | `ironic-api` | ReplicaSet | 3 | Running:3 |
| `ironic` | `ironic-conductor-default` | StatefulSet | 1 | Running:1 |
| `ironic` | `ironic-dashboard` | ReplicaSet | 3 | Running:3 |
| `ironic` | `ironic-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `ironic` | `ironic-pushgateway` | StatefulSet | 3 | Running:3 |
| `ironic` | `pushgateway-data-cleaner` | Job | 3 | Succeeded:3 |
| `openstack` | `nova-compute-ironic` | StatefulSet | 3 | Running:3 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `ironic` | `ceph-rgw-ingress` | ExternalName | 80/TCP |
| `ironic` | `ironic` | ExternalName | 80/TCP |
| `ironic` | `ironic-api` | ClusterIP | 6385/TCP |
| `ironic` | `ironic-dashboard` | ExternalName | 80/TCP |
| `ironic` | `ironic-dashboard-api` | ClusterIP | 80/TCP |
| `ironic` | `ironic-dashboard-int` | ClusterIP | 8080/TCP |
| `ironic` | `ironic-pushgateway-0` | ClusterIP | 9091/TCP |
| `ironic` | `ironic-pushgateway-1` | ClusterIP | 9091/TCP |
| `ironic` | `ironic-pushgateway-2` | ClusterIP | 9091/TCP |
| `ironic` | `ironic-pushgateway-http` | NodePort | 8089/TCP |

