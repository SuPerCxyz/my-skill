# Kubernetes Components

Kubernetes 控制面、网络、CSI、认证和系统组件参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `coredns` | coredns |
| DaemonSet | `csi-rbdplugin` | driver-registrar<br>csi-rbdplugin<br>liveness-prometheus |
| DaemonSet | `k8s-keystone-auth` | k8s-keystone-auth |
| DaemonSet | `kube-flannel` | kube-flannel |
| DaemonSet | `local-volume-provisioner` | provisioner<br>dir-provisioner |
| DaemonSet | `openstack-cloud-controller-manager` | openstack-cloud-controller-manager |
| Deployment | `csi-rbdplugin-provisioner` | csi-provisioner<br>csi-snapshotter<br>csi-attacher<br>csi-resizer<br>csi-rbdplugin<br>csi-rbdplugin-controller<br>liveness-prometheus |
| Deployment | `heapster` | heapster |
| Deployment | `ingress-error-pages` | ingress-error-pages |
| Deployment | `metrics-server` | metrics-server |
| Job | `kube-monitor-29707635` | kube-monitor |
| Job | `pod-clear-cronjob-29707635` | clearer |
