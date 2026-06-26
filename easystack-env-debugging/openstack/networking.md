# OpenStack networking

记录 `networking` 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `ovn` | `ovn-7.0.1-alpha.591` | DEPLOYED |
| `openstack` | `proton` | `proton-7.0.1-alpha.1264` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | DaemonSet | `ovn-controller` | 4/4 ready | ovn-controller | init<br>ovn-controller-init |
| `openstack` | DaemonSet | `proton-insight-agent` | 4/4 ready | proton-insight-agent | init |
| `openstack` | DaemonSet | `proton-ovn-gateway-monitor-agent` | 3/3 ready | proton-ovn-gateway-monitor-agent | init |
| `openstack` | DaemonSet | `proton-ovn-l2-agent` | 0/0 ready | proton-ovn-l2-agent | init<br>proton-ovn-l2-agent-init |
| `openstack` | DaemonSet | `proton-ovn-l2gw-agent` | 3/3 ready | proton-ovn-l2gw-agent | init<br>proton-ovn-l2gw-agent-init |
| `openstack` | DaemonSet | `proton-ovn-metadata-agent` | 3/3 ready | proton-ovn-metadata-agent | - |
| `openstack` | DaemonSet | `proton-sriov-nic-agent` | 0/0 ready | proton-sriov-nic-agent | init |
| `openstack` | Deployment | `ovn-ovsdb-nb-relay` | 3/3 ready | ovn-ovsdb-nb-relay | init |
| `openstack` | Deployment | `ovn-ovsdb-sb-leader-relay` | 3/3 ready | ovn-ovsdb-sb-leader-relay | init |
| `openstack` | Deployment | `ovn-ovsdb-sb-relay` | 3/3 ready | ovn-ovsdb-sb-relay | init |
| `openstack` | Deployment | `proton-dashboard` | 3/3 ready | proton-dashboard | init |
| `openstack` | Deployment | `proton-dashboard-api` | 3/3 ready | proton-dashboard-api | init |
| `openstack` | Deployment | `proton-maintenance` | 1/1 ready | proton-maintenance | init |
| `openstack` | Deployment | `proton-server` | 3/3 ready | proton-server | init |
| `openstack` | Job | `ovn-backup-job-29706780` | succeeded=1, failed=0 | ovn-backup-job | - |
| `openstack` | Job | `ovn-ecpbackendcheck-1782334847` | succeeded=1, failed=0 | ovn-ecpbackendcheck | init |
| `openstack` | Job | `proton-bootstrap` | succeeded=1, failed=0 | proton-bootstrap | init |
| `openstack` | Job | `proton-db-init` | succeeded=1, failed=0 | proton-db-init | init |
| `openstack` | Job | `proton-db-sync-6.5.1` | succeeded=1, failed=0 | proton-db-sync | init |
| `openstack` | Job | `proton-ecpbackendcheck-1782350092` | succeeded=1, failed=0 | proton-ecpbackendcheck | init |
| `openstack` | Job | `proton-init-project-quotas` | succeeded=1, failed=0 | init-project-quotas | init |
| `openstack` | Job | `proton-ks-endpoints` | succeeded=1, failed=0 | network-ks-endpoints-admin<br>network-ks-endpoints-internal<br>network-ks-endpoints-public | init |
| `openstack` | Job | `proton-ks-service` | succeeded=1, failed=0 | network-ks-service-registration | init |
| `openstack` | Job | `proton-ks-user` | succeeded=1, failed=0 | proton-ks-user | init |
| `openstack` | Job | `proton-ovn-check-job-29706810` | succeeded=1, failed=0 | proton-ovn-check-job | - |
| `openstack` | StatefulSet | `ovn-northd` | 3/3 ready | ovn-northd | init |
| `openstack` | StatefulSet | `ovn-ovsdb-nb` | 3/3 ready | ovn-ovsdb-nb | init |
| `openstack` | StatefulSet | `ovn-ovsdb-sb` | 3/3 ready | ovn-ovsdb-sb | init |
| `openstack` | StatefulSet | `ovn-tool` | 1/1 ready | ovn-tool | init |
| `openstack` | StatefulSet | `proton-insight-controller` | 1/1 ready | proton-insight-controller | init |

## Container Details 容器详情

### ovn-controller

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 4/4 ready
- Containers:
  - ovn-controller (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/ovn-controller.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - ovn-controller-init (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591)

### proton-insight-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 4/4 ready
- Containers:
  - proton-insight-agent (hub.easystack.io/production/escloud-linux-source-insight:7.0.1-alpha.1264;
    /usr/local/bin/insight-agent --config=/config.yaml)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ovn-gateway-monitor-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - proton-ovn-gateway-monitor-agent (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/neutron-ovn-gateway-monitor-agent.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ovn-l2-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 0/0 ready
- Containers:
  - proton-ovn-l2-agent (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/neutron-ovn-l2-agent.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - proton-ovn-l2-agent-init (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264)

### proton-ovn-l2gw-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - proton-ovn-l2gw-agent (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/neutron-ovn-l2gw-agent.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - proton-ovn-l2gw-agent-init (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264)

### proton-ovn-metadata-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - proton-ovn-metadata-agent (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/neutron-ovn-metadata-agent.sh)
- Init containers:
  - -

### proton-sriov-nic-agent

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 0/0 ready
- Containers:
  - proton-sriov-nic-agent (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/neutron-sriov-nic-agent.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-ovsdb-nb-relay

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ovn-ovsdb-nb-relay (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_nb_relay.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-ovsdb-sb-leader-relay

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ovn-ovsdb-sb-leader-relay (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591;
    /tmp/start_sb_leader_relay.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-ovsdb-sb-relay

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ovn-ovsdb-sb-relay (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_sb_relay.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-dashboard

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - proton-dashboard (hub.easystack.io/production/escloud-linux-source-proton-dashboard:7.0.1-alpha.1264; /nginx.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-dashboard-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - proton-dashboard-api (hub.easystack.io/production/escloud-linux-source-proton-dashboard-api:7.0.1-alpha.1264;
    /proton_dashboard_api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-maintenance

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - proton-maintenance (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/maintenance-worker.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-server

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - proton-server (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264; /tmp/neutron-server.sh
    start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-backup-job-29706780

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ovn-backup-job (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/cronjob_backup.sh)
- Init containers:
  - -

### ovn-ecpbackendcheck-1782334847

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ovn-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:6.1.1-lts; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-bootstrap

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-bootstrap (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-db-sync-6.5.1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-db-sync (hub.easystack.io/production/escloud-linux-source-proton-server:6.5.1; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ecpbackendcheck-1782350092

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-ecpbackendcheck (hub.easystack.io/production/escloud-linux-source-ems-dashboard-api:latest; echo done)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-init-project-quotas

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - init-project-quotas (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/init_project_quota.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ks-endpoints

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - network-ks-endpoints-admin (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/ks-endpoints.sh)
  - network-ks-endpoints-internal (hub.easystack.io/production/escloud-linux-source-heat-engine:latest;
    /tmp/ks-endpoints.sh)
  - network-ks-endpoints-public (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/ks-endpoints.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ks-service

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - network-ks-service-registration (hub.easystack.io/production/escloud-linux-source-heat-engine:latest;
    /tmp/ks-service.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ks-user

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-ks-user (hub.easystack.io/production/escloud-linux-source-heat-engine:latest; /tmp/ks-user.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-ovn-check-job-29706810

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - proton-ovn-check-job (hub.easystack.io/production/escloud-linux-source-proton-server:7.0.1-alpha.1264;
    /tmp/cronjob_check.sh)
- Init containers:
  - -

### ovn-northd

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - ovn-northd (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_northd.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-ovsdb-nb

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - ovn-ovsdb-nb (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_nb.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-ovsdb-sb

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - ovn-ovsdb-sb (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_sb.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### ovn-tool

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - ovn-tool (hub.easystack.io/production/escloud-linux-source-ovn:7.0.1-alpha.591; /tmp/start_ovn_tool.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### proton-insight-controller

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - proton-insight-controller (hub.easystack.io/production/escloud-linux-source-insight:7.0.1-alpha.1264;
    /usr/local/bin/insight-controller --config=/config.yaml)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `ovn-backup-job` | Job | 1 | Succeeded:1 |
| `ovn-controller` | DaemonSet | 4 | Running:4 |
| `ovn-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `ovn-northd` | StatefulSet | 3 | Running:3 |
| `ovn-ovsdb-nb` | ReplicaSet | 3 | Running:3 |
| `ovn-ovsdb-nb` | StatefulSet | 3 | Running:3 |
| `ovn-ovsdb-sb` | ReplicaSet | 3 | Running:3 |
| `ovn-ovsdb-sb` | StatefulSet | 3 | Running:3 |
| `ovn-ovsdb-sb-leader` | ReplicaSet | 3 | Running:3 |
| `ovn-tool` | StatefulSet | 1 | Running:1 |
| `proton-bootstrap` | Job | 1 | Succeeded:1 |
| `proton-dashboard` | ReplicaSet | 3 | Running:3 |
| `proton-dashboard-api` | ReplicaSet | 3 | Running:3 |
| `proton-db-init` | Job | 1 | Succeeded:1 |
| `proton-db-sync-6.5.1` | Job | 1 | Succeeded:1 |
| `proton-ecpbackendcheck` | Job | 1 | Succeeded:1 |
| `proton-init-project-quotas` | Job | 1 | Succeeded:1 |
| `proton-insight-agent` | DaemonSet | 4 | Running:4 |
| `proton-insight-controller` | StatefulSet | 1 | Running:1 |
| `proton-ks-endpoints` | Job | 1 | Succeeded:1 |
| `proton-ks-service` | Job | 1 | Succeeded:1 |
| `proton-ks-user` | Job | 1 | Succeeded:1 |
| `proton-maintenance` | ReplicaSet | 1 | Running:1 |
| `proton-ovn-check-job` | Job | 1 | Succeeded:1 |
| `proton-ovn-gateway-monitor-agent` | DaemonSet | 3 | Running:3 |
| `proton-ovn-l2gw-agent` | DaemonSet | 3 | Running:3 |
| `proton-ovn-metadata-agent` | DaemonSet | 3 | Running:3 |
| `proton-server` | ReplicaSet | 3 | Running:3 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `ovn-northd` | ClusterIP | - |
| `openstack` | `ovn-ovsdb-nb` | ClusterIP | 6641/TCP |
| `openstack` | `ovn-ovsdb-nb-discovery` | ClusterIP | 6641/TCP |
| `openstack` | `ovn-ovsdb-nb-relay` | ClusterIP | 6641/TCP |
| `openstack` | `ovn-ovsdb-sb` | ClusterIP | 6642/TCP |
| `openstack` | `ovn-ovsdb-sb-discovery` | ClusterIP | 6642/TCP |
| `openstack` | `ovn-ovsdb-sb-leader-relay` | ClusterIP | 6642/TCP |
| `openstack` | `ovn-ovsdb-sb-relay` | ClusterIP | 6642/TCP |
| `openstack` | `proton-dashboard` | ExternalName | 80/TCP |
| `openstack` | `proton-dashboard-api-int` | ClusterIP | 80/TCP |
| `openstack` | `proton-dashboard-int` | ClusterIP | 8080/TCP |
| `openstack` | `proton-insight-api-int` | ClusterIP | 8032/TCP |

