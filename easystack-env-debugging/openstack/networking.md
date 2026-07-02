# OpenStack networking

网络组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `ovn-controller` | ovn-controller |
| DaemonSet | `proton-insight-agent` | proton-insight-agent |
| DaemonSet | `proton-ovn-gateway-monitor-agent` | proton-ovn-gateway-monitor-agent |
| DaemonSet | `proton-ovn-l2-agent` | proton-ovn-l2-agent |
| DaemonSet | `proton-ovn-l2gw-agent` | proton-ovn-l2gw-agent |
| DaemonSet | `proton-ovn-metadata-agent` | proton-ovn-metadata-agent |
| DaemonSet | `proton-sriov-nic-agent` | proton-sriov-nic-agent |
| Deployment | `ovn-ovsdb-nb-relay` | ovn-ovsdb-nb-relay |
| Deployment | `ovn-ovsdb-sb-leader-relay` | ovn-ovsdb-sb-leader-relay |
| Deployment | `ovn-ovsdb-sb-relay` | ovn-ovsdb-sb-relay |
| Deployment | `proton-dashboard` | proton-dashboard |
| Deployment | `proton-dashboard-api` | proton-dashboard-api |
| Deployment | `proton-maintenance` | proton-maintenance |
| Deployment | `proton-server` | proton-server |
| Job | `ovn-backup-job-29706780` | ovn-backup-job |
| Job | `ovn-ecpbackendcheck-1782334847` | ovn-ecpbackendcheck |
| Job | `proton-bootstrap` | proton-bootstrap |
| Job | `proton-db-init` | proton-db-init |
| Job | `proton-db-sync-6.5.1` | proton-db-sync |
| Job | `proton-ecpbackendcheck-1782350092` | proton-ecpbackendcheck |
| Job | `proton-init-project-quotas` | init-project-quotas |
| Job | `proton-ks-endpoints` | network-ks-endpoints-admin<br>network-ks-endpoints-internal<br>network-ks-endpoints-public |
| Job | `proton-ks-service` | network-ks-service-registration |
| Job | `proton-ks-user` | proton-ks-user |
| Job | `proton-ovn-check-job-29706810` | proton-ovn-check-job |
| StatefulSet | `ovn-northd` | ovn-northd |
| StatefulSet | `ovn-ovsdb-nb` | ovn-ovsdb-nb |
| StatefulSet | `ovn-ovsdb-sb` | ovn-ovsdb-sb |
| StatefulSet | `ovn-tool` | ovn-tool |
| StatefulSet | `proton-insight-controller` | proton-insight-controller |
