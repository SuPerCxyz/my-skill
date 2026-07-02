# OpenStack monitoring

监控组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `blackbox-exporter` | blackbox-exporter |
| Deployment | `kube-state-metrics-shard-0` | kube-state-metrics |
| Deployment | `mysqld-exporter` | mysqld-exporter |
| Deployment | `openstack-exporter` | openstack-metrics |
| Deployment | `prometheus-operator` | prometheus-operator |
| Deployment | `thanos-query-ecms` | thanos-query |
| Deployment | `thanos-query-ecms-global` | thanos-query-global |
| StatefulSet | `alertmanager-ecms` | alertmanager<br>config-reloader |
| StatefulSet | `prometheus-ecms` | prometheus<br>config-reloader<br>thanos-sidecar |
| StatefulSet | `prometheus-vmm` | prometheus<br>config-reloader<br>thanos-sidecar |
| StatefulSet | `thanos-ruler-ecms` | thanos-ruler<br>config-reloader |
| StatefulSet | `thanos-ruler-vmm` | thanos-ruler<br>config-reloader |
