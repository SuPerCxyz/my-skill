# Kubernetes Components

Kubernetes 控制面、网络、CSI、认证和系统组件参考。

## 节点

| Node | Roles | Kubelet version | Ready |
|------|-------|-----------------|-------|
| `node-1` | node | v1.35.3-es | True |
| `node-10` | node | v1.35.3-es | True |
| `node-2` | node | v1.35.3-es | True |
| `node-3` | node | v1.35.3-es | True |
| `node-4` | master, node | v1.35.3-es | True |
| `node-5` | master, node | v1.35.3-es | True |
| `node-6` | master, node | v1.35.3-es | True |
| `node-7` | node | v1.35.3-es | True |
| `node-8` | node | v1.35.3-es | True |
| `node-9` | node | v1.35.3-es | True |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `kube-system` | DaemonSet | `coredns` | 3/3 ready | coredns | - |
| `kube-system` | DaemonSet | `csi-rbdplugin` | 10/10 ready | driver-registrar<br>csi-rbdplugin<br>liveness-prometheus | - |
| `kube-system` | DaemonSet | `k8s-keystone-auth` | 3/3 ready | k8s-keystone-auth | - |
| `kube-system` | DaemonSet | `kube-flannel` | 10/10 ready | kube-flannel | install-cni-plugin<br>install-cni |
| `kube-system` | DaemonSet | `local-volume-provisioner` | 0/0 ready | provisioner<br>dir-provisioner | - |
| `kube-system` | DaemonSet | `openstack-cloud-controller-manager` | 3/3 ready | openstack-cloud-controller-manager | - |
| `kube-system` | Deployment | `csi-rbdplugin-provisioner` | 1/1 ready | csi-provisioner<br>csi-snapshotter<br>csi-attacher<br>csi-resizer<br>csi-rbdplugin<br>csi-rbdplugin-controller<br>liveness-prometheus | - |
| `kube-system` | Deployment | `heapster` | 1/1 ready | heapster | - |
| `kube-system` | Deployment | `ingress-error-pages` | 1/1 ready | ingress-error-pages | - |
| `kube-system` | Deployment | `metrics-server` | 2/2 ready | metrics-server | - |
| `kube-system` | Job | `kube-monitor-29707635` | succeeded=1, failed=0 | kube-monitor | - |
| `kube-system` | Job | `pod-clear-cronjob-29707635` | succeeded=1, failed=0 | clearer | - |

## Container Details 容器详情

### coredns

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - coredns (hub.easystack.io/captain/coredns:1.12.3; -conf /etc/coredns/Corefile)
- Init containers:
  - -

### csi-rbdplugin

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 10/10 ready
- Containers:
  - driver-registrar (hub.easystack.io/captain/csi-node-driver-registrar:v2.8.0; --v=1 --csi-address=/csi/csi.sock
    --kubelet-registration-path=/var/lib/kubelet/plugins/rbd.csi.ceph.com/csi.sock)
  - csi-rbdplugin (hub.easystack.io/captain/cephcsi:v3.9.0-es-ceph-1.16; --nodeid=$(NODE_ID)
    --pluginpath=/var/lib/kubelet/plugins --stagingpath=/var/lib/kubelet/plugins/kubernetes.io/csi/ --type=rbd
    --nodeserver=true --endpoint=$(CSI_ENDPOINT) --csi-addons-endpoint=$(CSI_ADDONS_ENDPOINT) --v=5
    --drivername=rbd.csi.ceph.com --enableprofiling=false)
  - liveness-prometheus (hub.easystack.io/captain/cephcsi:v3.9.0-es-ceph-1.16; --type=liveness --endpoint=$(CSI_ENDPOINT)
    --metricsport=8680 --metricspath=/metrics --polltime=60s --timeout=3s)
- Init containers:
  - -

### k8s-keystone-auth

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - k8s-keystone-auth (hub.easystack.io/captain/k8s-keystone-auth:v1.27.1; ./bin/k8s-keystone-auth --tls-cert-file
    /etc/kubernetes/ssl/apiserver.pem --tls-private-key-file /etc/kubernetes/ssl/apiserver-key.pem --keystone-url
    http://keystone-api.openstack.svc.cluster.local/identity/v3 --listen 0.0.0.0:4443)
- Init containers:
  - -

### kube-flannel

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 10/10 ready
- Containers:
  - kube-flannel (hub.easystack.io/captain/flannel:v0.26.4; /opt/bin/flanneld --ip-masq --kube-subnet-mgr --iface=br-mgmt)
- Init containers:
  - install-cni-plugin (hub.easystack.io/captain/flannel-cni:v1.1.2-es)
  - install-cni (hub.easystack.io/captain/flannel:v0.26.4)

### local-volume-provisioner

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 0/0 ready
- Containers:
  - provisioner (hub.easystack.io/captain/local-volume-provisioner:v2.4.0; image default entrypoint)
  - dir-provisioner (hub.easystack.io/captain/local-volume-provisioner:v2.4.0; /ensure_dir.sh)
- Init containers:
  - -

### openstack-cloud-controller-manager

- Namespace: `kube-system`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - openstack-cloud-controller-manager
    (hub.easystack.io/production/escloud-linux-source-cloud-provider-openstack:7.0.1-alpha.5301;
    /bin/openstack-cloud-controller-manager --v=1 --cluster-name=$(CLUSTER_NAME) --cloud-config=$(CLOUD_CONFIG)
    --cloud-provider=openstack --use-service-account-credentials=true --bind-address=127.0.0.1 --controllers=service
    --concurrent-service-syncs=3)
- Init containers:
  - -

### csi-rbdplugin-provisioner

- Namespace: `kube-system`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - csi-provisioner (hub.easystack.io/captain/csi-provisioner:v3.5.0; --csi-address=$(ADDRESS) --v=1 --timeout=150s
    --retry-interval-start=500ms --leader-election=true --feature-gates=Topology=false
    --feature-gates=HonorPVReclaimPolicy=true --prevent-volume-mode-conversion=true --default-fstype=ext4
    --extra-create-metadata=true)
  - csi-snapshotter (hub.easystack.io/captain/csi-snapshotter:v6.2.2; --csi-address=$(ADDRESS) --v=1 --timeout=150s
    --leader-election=true --extra-create-metadata=true)
  - csi-attacher (hub.easystack.io/captain/csi-attacher:v4.3.0; --v=1 --csi-address=$(ADDRESS) --leader-election=true
    --retry-interval-start=500ms --default-fstype=ext4)
  - csi-resizer (hub.easystack.io/captain/csi-resizer:v1.8.0; --csi-address=$(ADDRESS) --v=1 --timeout=150s
    --leader-election --retry-interval-start=500ms --handle-volume-inuse-error=false
    --feature-gates=RecoverVolumeExpansionFailure=true)
  - csi-rbdplugin (hub.easystack.io/captain/cephcsi:v3.9.0-es-ceph-1.16; --nodeid=$(NODE_ID) --type=rbd
    --controllerserver=true --endpoint=$(CSI_ENDPOINT) --csi-addons-endpoint=$(CSI_ADDONS_ENDPOINT) --v=5
    --drivername=rbd.csi.ceph.com --pidlimit=-1 --rbdhardmaxclonedepth=8 --rbdsoftmaxclonedepth=4 --enableprofiling=false
    --setmetadata=true)
  - csi-rbdplugin-controller (hub.easystack.io/captain/cephcsi:v3.9.0-es-ceph-1.16; --type=controller --v=5
    --drivername=rbd.csi.ceph.com --drivernamespace=$(DRIVER_NAMESPACE) --setmetadata=true)
  - liveness-prometheus (hub.easystack.io/captain/cephcsi:v3.9.0-es-ceph-1.16; --type=liveness --endpoint=$(CSI_ENDPOINT)
    --metricsport=8680 --metricspath=/metrics --polltime=60s --timeout=3s)
- Init containers:
  - -

### heapster

- Namespace: `kube-system`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - heapster (hub.easystack.io/captain/heapster:v1.6.0-es; /eventer --source=kubernetes --sink=log)
- Init containers:
  - -

### ingress-error-pages

- Namespace: `kube-system`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - ingress-error-pages (hub.easystack.io/captain/defaultbackend:1.3-es; image default entrypoint)
- Init containers:
  - -

### metrics-server

- Namespace: `kube-system`
- 启动方式: Deployment
- 状态: 2/2 ready
- Containers:
  - metrics-server (hub.easystack.io/captain/metrics-server:v0.7.2; /metrics-server --cert-dir=/tmp --secure-port=8443
    --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname --metric-resolution=60s --kubelet-use-node-status-port
    --kubelet-insecure-tls)
- Init containers:
  - -

### kube-monitor-29707635

- Namespace: `kube-system`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - kube-monitor (hub.easystack.io/captain/kube-es-monitor:latest; /tmp/monitor-sts.sh)
- Init containers:
  - -

### pod-clear-cronjob-29707635

- Namespace: `kube-system`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - clearer (hub.easystack.io/production/escloud-linux-source-openstack-base:6.1.1; /usr/local/bin/clear.sh)
- Init containers:
  - -
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `coredns` | DaemonSet | 3 | Running:3 |
| `csi-rbdplugin` | DaemonSet | 10 | Running:10 |
| `csi-rbdplugin-provisioner` | ReplicaSet | 1 | Running:1 |
| `heapster` | ReplicaSet | 1 | Running:1 |
| `ingress-error` | ReplicaSet | 1 | Running:1 |
| `k8s-keystone-auth` | DaemonSet | 3 | Running:3 |
| `kube-apiserver-node` | Node | 3 | Running:3 |
| `kube-controller-manager-node` | Node | 3 | Running:3 |
| `kube-flannel` | DaemonSet | 10 | Running:10 |
| `kube-monitor` | Job | 1 | Succeeded:1 |
| `kube-proxy-node` | Node | 10 | Running:10 |
| `kube-scheduler-node` | Node | 3 | Running:3 |
| `metrics-server` | ReplicaSet | 2 | Running:2 |
| `nginx-proxy-node` | Node | 7 | Running:7 |
| `openstack-cloud-controller-manager` | DaemonSet | 3 | Running:3 |
| `pod-clear-cronjob` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `kube-system` | `coredns` | ClusterIP | 53/UDP, 53/TCP, 9153/TCP |
| `kube-system` | `csi-metrics-rbdplugin` | ClusterIP | 8080/TCP |
| `kube-system` | `csi-rbdplugin-provisioner` | ClusterIP | 8080/TCP |
| `kube-system` | `etcd` | ClusterIP | 2379/TCP |
| `kube-system` | `ingress-error-pages` | ClusterIP | 80/TCP |
| `kube-system` | `k8s-keystone-auth` | ClusterIP | 4443/TCP |
| `kube-system` | `kube-controller-manager-discovery` | ClusterIP | 10252/TCP |
| `kube-system` | `kube-scheduler-discovery` | ClusterIP | 10251/TCP |
| `kube-system` | `kubelet` | ClusterIP | 10250/TCP, 10255/TCP, 4194/TCP |
| `kube-system` | `metrics-server` | ClusterIP | 443/TCP |
