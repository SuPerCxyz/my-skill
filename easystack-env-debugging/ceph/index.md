# Ceph Components

Ceph 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `ceph-mon` | ceph-mon |
| DaemonSet | `ceph-osd-0-node-4` | osd-create-pod |
| DaemonSet | `ceph-osd-1-node-4` | osd-create-pod |
| DaemonSet | `ceph-osd-2-node-5` | osd-create-pod |
| DaemonSet | `ceph-osd-3-node-5` | osd-create-pod |
| DaemonSet | `ceph-osd-4-node-6` | osd-create-pod |
| DaemonSet | `ceph-osd-5-node-6` | osd-create-pod |
| DaemonSet | `ceph-osd-isolation` | osd-auto-isolation |
| Deployment | `ceph-mgr` | ceph-mgr |
| Deployment | `ceph-operator` | essvc |
| Deployment | `ceph-rbdmirror` | ceph-rbdmirror |
| Deployment | `ceph-rgw` | ceph-rgw |
| Job | `ceph-commands-pokch` | ceph-commands |
| Job | `ceph-fstrim-rbd-29706900` | ceph-fstrim-rbd |
| Job | `ceph-mds-keyring-generator` | ceph-mds-keyring-generator |
| Job | `ceph-mgr-keyring-generator` | ceph-mgr-keyring-generator |
| Job | `ceph-mon-keyring-generator` | ceph-mon-keyring-generator |
| Job | `ceph-namespace-client-key-generator-xxpxx` | ceph-storage-keys-generator |
| Job | `ceph-osd-compact-29706840` | ceph-osd-compact |
| Job | `ceph-osd-keyring-generator` | ceph-osd-keyring-generator |
| Job | `ceph-ready` | ceph-ready |
| Job | `ceph-rgw-keyring-generator` | ceph-rgw-keyring-generator |
| Job | `ceph-set-reporters` | ceph-set-reporters |
| Job | `ceph-storage-keys-generator` | ceph-storage-keys-generator |
