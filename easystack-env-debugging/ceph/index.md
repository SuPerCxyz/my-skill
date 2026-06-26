# Ceph Components

记录 Ceph 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `ceph` | `ceph` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `ceph` | `ceph-operator` | `ceph-operator-6.0.1` | DEPLOYED |
| `ceph` | `rbdmirror` | `rbdmirror-7.0.1-alpha.103` | DEPLOYED |
| `container-registry` | `ceph-container-registry-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `devops` | `ceph-devops-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `eks-managed` | `ceph-eks-managed-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `ems` | `ceph-ems-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `glia` | `ceph-glia-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `ceph-openstack-config` | `ceph-7.0.1-alpha.103` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `ceph` | DaemonSet | `ceph-mon` | 3/3 ready | ceph-mon | init<br>hostnetwork-reg<br>ceph-init-dirs |
| `ceph` | DaemonSet | `ceph-osd-0-node-4` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-1-node-4` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-2-node-5` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-3-node-5` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-4-node-6` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-5-node-6` | 1/1 ready | osd-create-pod | init |
| `ceph` | DaemonSet | `ceph-osd-isolation` | 3/3 ready | osd-auto-isolation | - |
| `ceph` | Deployment | `ceph-mgr` | 3/3 ready | ceph-mgr | init<br>ceph-init-dirs |
| `ceph` | Deployment | `ceph-operator` | 1/1 ready | essvc | - |
| `ceph` | Deployment | `ceph-rbdmirror` | 0/0 ready | ceph-rbdmirror | init<br>ceph-init-dirs |
| `ceph` | Deployment | `ceph-rgw` | 3/3 ready | ceph-rgw | init<br>ceph-init-dirs<br>ceph-rgw-ks-init |
| `ceph` | Job | `ceph-commands-pokch` | succeeded=1, failed=0 | ceph-commands | init |
| `ceph` | Job | `ceph-fstrim-rbd-29706900` | succeeded=1, failed=0 | ceph-fstrim-rbd | init |
| `ceph` | Job | `ceph-mds-keyring-generator` | succeeded=1, failed=0 | ceph-mds-keyring-generator | - |
| `ceph` | Job | `ceph-mgr-keyring-generator` | succeeded=1, failed=0 | ceph-mgr-keyring-generator | - |
| `ceph` | Job | `ceph-mon-keyring-generator` | succeeded=1, failed=0 | ceph-mon-keyring-generator | - |
| `ceph` | Job | `ceph-namespace-client-key-generator-xxpxx` | succeeded=1, failed=0 | ceph-storage-keys-generator | - |
| `ceph` | Job | `ceph-osd-compact-29706840` | succeeded=1, failed=0 | ceph-osd-compact | init |
| `ceph` | Job | `ceph-osd-keyring-generator` | succeeded=1, failed=0 | ceph-osd-keyring-generator | - |
| `ceph` | Job | `ceph-ready` | succeeded=1, failed=0 | ceph-ready | init |
| `ceph` | Job | `ceph-rgw-keyring-generator` | succeeded=1, failed=0 | ceph-rgw-keyring-generator | - |
| `ceph` | Job | `ceph-set-reporters` | succeeded=1, failed=0 | ceph-set-reporters | - |
| `ceph` | Job | `ceph-storage-keys-generator` | succeeded=1, failed=0 | ceph-storage-keys-generator | - |

## Container Details 容器详情

### ceph-mon

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - ceph-mon (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_mon.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)
  - hostnetwork-reg (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)
  - ceph-init-dirs (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)

### ceph-osd-0-node-4

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-1-node-4

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-2-node-5

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-3-node-5

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-4-node-6

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-5-node-6

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 1/1 ready
- Containers:
  - osd-create-pod (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_osd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-isolation

- Namespace: `ceph`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - osd-auto-isolation (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /osd_auto_isolation.py)
- Init containers:
  - -

### ceph-mgr

- Namespace: `ceph`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ceph-mgr (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_mgr.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)
  - ceph-init-dirs (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)

### ceph-operator

- Namespace: `ceph`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - essvc (hub.easystack.io/production/ceph-operator:6.0.1; /ceph-operator -logtostderr -v 3)
- Init containers:
  - -

### ceph-rbdmirror

- Namespace: `ceph`
- 启动方式: Deployment
- 状态: 0/0 ready
- Containers:
  - ceph-rbdmirror (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_rbdmirror.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)
  - ceph-init-dirs (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)

### ceph-rgw

- Namespace: `ceph`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - ceph-rgw (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /start_rgw.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)
  - ceph-init-dirs (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)
  - ceph-rgw-ks-init (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2)

### ceph-commands-pokch

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-commands (hub.easystack.io/production/ceph-config-helper:latest; /exec_ceph_commands.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-fstrim-rbd-29706900

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-fstrim-rbd (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /fstrim_rbd.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-mds-keyring-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-mds-keyring-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-key.sh)
- Init containers:
  - -

### ceph-mgr-keyring-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-mgr-keyring-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-key.sh)
- Init containers:
  - -

### ceph-mon-keyring-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-mon-keyring-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-key.sh)
- Init containers:
  - -

### ceph-namespace-client-key-generator-xxpxx

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-storage-keys-generator (hub.easystack.io/production/ceph-config-helper:latest;
    /opt/ceph/ceph-namespace-client-key.sh)
- Init containers:
  - -

### ceph-osd-compact-29706840

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-osd-compact (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /ceph_osd_compact.py)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-osd-keyring-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-osd-keyring-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-key.sh)
- Init containers:
  - -

### ceph-ready

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-ready (hub.easystack.io/production/escloud-linux-ceph-daemon:16.2.15-14.es8_2; /ceph_ready.sh)
- Init containers:
  - init (hub.easystack.io/production/ubuntu-source-kubernetes-entrypoint:4.0.0)

### ceph-rgw-keyring-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-rgw-keyring-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-key.sh)
- Init containers:
  - -

### ceph-set-reporters

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-set-reporters (hub.easystack.io/production/ceph-config-helper:latest; /ceph_set_reporters.sh)
- Init containers:
  - -

### ceph-storage-keys-generator

- Namespace: `ceph`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - ceph-storage-keys-generator (hub.easystack.io/production/ceph-config-helper:latest; /opt/ceph/ceph-storage-key.sh)
- Init containers:
  - -
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `ceph-commands-pokch` | Job | 1 | Succeeded:1 |
| `ceph-fstrim-rbd` | Job | 1 | Succeeded:1 |
| `ceph-mds-keyring-generator` | Job | 1 | Succeeded:1 |
| `ceph-mgr` | ReplicaSet | 3 | Running:3 |
| `ceph-mgr-keyring-generator` | Job | 1 | Succeeded:1 |
| `ceph-mon` | DaemonSet | 3 | Running:3 |
| `ceph-mon-keyring-generator` | Job | 1 | Succeeded:1 |
| `ceph-namespace-client-key-generator-xxpxx` | Job | 1 | Succeeded:1 |
| `ceph-operator` | ReplicaSet | 1 | Running:1 |
| `ceph-osd-0-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-1-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-2-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-3-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-4-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-5-node` | DaemonSet | 1 | Running:1 |
| `ceph-osd-compact` | Job | 1 | Succeeded:1 |
| `ceph-osd-isolation` | DaemonSet | 3 | Running:3 |
| `ceph-osd-keyring-generator` | Job | 1 | Succeeded:1 |
| `ceph-ready` | Job | 1 | Succeeded:1 |
| `ceph-rgw` | ReplicaSet | 3 | Running:3 |
| `ceph-rgw-keyring-generator` | Job | 1 | Succeeded:1 |
| `ceph-set-reporters` | Job | 1 | Succeeded:1 |
| `ceph-storage-keys-generator` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `ceph` | `ceph-mon` | ClusterIP | 6789/TCP |
| `ceph` | `ceph-operator` | ClusterIP | 80/TCP |
| `ceph` | `ceph-rgw` | ClusterIP | 8088/TCP |
| `ceph` | `ceph-rgw-ingress` | ExternalName | 80/TCP |

