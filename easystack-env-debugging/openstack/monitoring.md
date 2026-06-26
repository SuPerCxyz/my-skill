# OpenStack monitoring

记录 `monitoring` 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

当前文档未记录对应 Helm release。

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `blackbox-exporter` | 3/3 ready | blackbox-exporter | init |
| `openstack` | Deployment | `kube-state-metrics-shard-0` | 2/2 ready | kube-state-metrics | init |
| `openstack` | Deployment | `mysqld-exporter` | 3/3 ready | mysqld-exporter | init |
| `openstack` | Deployment | `openstack-exporter` | 3/3 ready | openstack-metrics | init |
| `openstack` | Deployment | `prometheus-operator` | 1/1 ready | prometheus-operator | - |
| `openstack` | Deployment | `thanos-query-ecms` | 3/3 ready | thanos-query | - |
| `openstack` | Deployment | `thanos-query-ecms-global` | 3/3 ready | thanos-query-global | - |
| `openstack` | StatefulSet | `alertmanager-ecms` | 2/2 ready | alertmanager<br>config-reloader | init-config-reloader |
| `openstack` | StatefulSet | `prometheus-ecms` | 2/2 ready | prometheus<br>config-reloader<br>thanos-sidecar | init-config-reloader |
| `openstack` | StatefulSet | `prometheus-vmm` | 2/2 ready | prometheus<br>config-reloader<br>thanos-sidecar | init-config-reloader |
| `openstack` | StatefulSet | `thanos-ruler-ecms` | 2/2 ready | thanos-ruler<br>config-reloader | - |
| `openstack` | StatefulSet | `thanos-ruler-vmm` | 2/2 ready | thanos-ruler<br>config-reloader | - |

## Container Details 容器详情

### blackbox-exporter

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - blackbox-exporter (hub.easystack.io/production/blackbox-exporter:v0.28.0; /tmp/blackbox-exporter.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### kube-state-metrics-shard-0

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 2/2 ready
- Containers:
  - kube-state-metrics (hub.easystack.io/production/kube-state-metrics:v2.16.0;
    --resources=certificatesigningrequests,configmaps,cronjobs,daemonsets,deployments,endpoints,horizontalpodautoscalers,ingresses,jobs,leases,limitranges,mutatingwebhookconfigurations,namespaces,networkpolicies,nodes,persistentvolumeclaims,persistentvolumes,poddisruptionbudgets,pods,replicasets,replicationcontrollers,resourcequotas,secrets,services,statefulsets,storageclasses,validatingwebhookconfigurations,volumeattachments
    --metric-annotations-allowlist=namespaces=[*] --metric-labels-allowlist=*=[*] --use-apiserver-cache --shard=0
    --total-shards=1 --server-read-timeout=30s --server-write-timeout=30s --auto-gomemlimit --auto-gomemlimit-ratio=0.9)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### mysqld-exporter

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - mysqld-exporter (hub.easystack.io/production/mysqld-exporter:v0.18.0;
    --mysqld.address=mariadb.openstack.svc.cluster.local:3306 --mysqld.username=root)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### openstack-exporter

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - openstack-metrics (hub.easystack.io/production/escloud-linux-source-openstack-exporter:7.0.1-alpha.28;
    /tmp/openstack-exporter.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### prometheus-operator

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - prometheus-operator (hub.easystack.io/production/prometheus-operator:v0.78.2-es; --kubelet-service=kube-system/kubelet
    --prometheus-config-reloader=hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es
    --config-reloader-cpu-request=10m --config-reloader-cpu-limit=100m --config-reloader-memory-request=50Mi
    --config-reloader-memory-limit=128Mi --web.listen-address=:8443 --web.enable-tls=true --log-level=info)
- Init containers:
  - -

### thanos-query-ecms

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - thanos-query (hub.easystack.io/production/thanos:v0.37.2-es; query --enable-auto-gomemlimit --auto-gomemlimit.ratio=0.9
    --query.replica-label=prometheus_replica --query.replica-label=thanos_ruler_replica
    --store=dnssrv+_grpc._tcp.prometheus-operated --store=dnssrv+_grpc._tcp.thanos-ruler-operated --log.level=info
    --alert.query-url=http://ecms-web-172-16-10-2.openstack.svc.cluster.local)
- Init containers:
  - -

### thanos-query-ecms-global

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - thanos-query-global (hub.easystack.io/production/thanos:v0.37.2-es; query --enable-auto-gomemlimit
    --auto-gomemlimit.ratio=0.9 --query.replica-label=prometheus_replica --query.replica-label=thanos_ruler_replica
    --store.sd-files=/thanos-query-global-configmap/file_sd_configs.yaml --store.sd-interval=1m --grpc-client-tls-secure
    --grpc-client-tls-cert=/certs-client/tls.crt --grpc-client-tls-key=/certs-client/tls.key
    --grpc-client-tls-ca=/certs-server/ca.crt --web.external-prefix=/global --web.route-prefix=/ --log.level=info)
- Init containers:
  - -

### alertmanager-ecms

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 2/2 ready
- Containers:
  - alertmanager (hub.easystack.io/production/alertmanager:v0.28.1-es;
    --config.file=/etc/alertmanager/config_out/alertmanager.env.yaml --storage.path=/alertmanager --data.retention=120h
    --cluster.listen-address=[$(POD_IP)]:9094 --web.listen-address=:9093 --enable-feature=auto-gomemlimit
    --web.route-prefix=/ --cluster.peer-timeout=60s --cluster.label=openstack/ecms
    --cluster.peer=alertmanager-ecms-0.alertmanager-operated:9094
    --cluster.peer=alertmanager-ecms-1.alertmanager-operated:9094 --cluster.reconnect-timeout=5m
    --web.config.file=/etc/alertmanager/web_config/web-config.yaml --auto-gomemlimit.ratio=0.9)
  - config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es; /bin/prometheus-config-reloader
    --listen-address=:8080 --reload-url=http://localhost:9093/-/reload
    --config-file=/etc/alertmanager/config/alertmanager.yaml.gz
    --config-envsubst-file=/etc/alertmanager/config_out/alertmanager.env.yaml --watched-dir=/etc/alertmanager/config
    --watch-interval=45s)
- Init containers:
  - init-config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es)

### prometheus-ecms

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 2/2 ready
- Containers:
  - prometheus (hub.easystack.io/production/prometheus:v2.55.1; --web.console.templates=/etc/prometheus/consoles
    --web.console.libraries=/etc/prometheus/console_libraries --config.file=/etc/prometheus/config_out/prometheus.env.yaml
    --web.enable-lifecycle --enable-feature=extra-scrape-metrics,auto-gomemlimit --web.route-prefix=/
    --storage.tsdb.retention.time=30d --storage.tsdb.retention.size=0.95TiB --storage.tsdb.path=/prometheus
    --query.max-concurrency=20 --query.timeout=2m --web.config.file=/etc/prometheus/web_config/web-config.yaml
    --storage.tsdb.max-block-duration=2h --storage.tsdb.min-block-duration=2h --auto-gomemlimit.ratio=0.9)
  - config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es; /bin/prometheus-config-reloader
    --listen-address=:8080 --reload-url=http://localhost:9090/-/reload
    --config-file=/etc/prometheus/config/prometheus.yaml.gz
    --config-envsubst-file=/etc/prometheus/config_out/prometheus.env.yaml
    --watched-dir=/etc/prometheus/rules/prometheus-ecms-rulefiles-0)
  - thanos-sidecar (hub.easystack.io/production/thanos:v0.37.2-es; sidecar --prometheus.url=http://localhost:9090/
    --grpc-address=:10901 --http-address=:10902 --log.level=info
    --prometheus.http-client-file=/etc/thanos/config/prometheus.http-client-file.yaml --enable-auto-gomemlimit
    --auto-gomemlimit.ratio=0.9)
- Init containers:
  - init-config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es)

### prometheus-vmm

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 2/2 ready
- Containers:
  - prometheus (hub.easystack.io/production/prometheus:v2.55.1; --web.console.templates=/etc/prometheus/consoles
    --web.console.libraries=/etc/prometheus/console_libraries --config.file=/etc/prometheus/config_out/prometheus.env.yaml
    --web.enable-lifecycle --enable-feature=extra-scrape-metrics,auto-gomemlimit --web.route-prefix=/
    --storage.tsdb.retention.time=200d --storage.tsdb.retention.size=475.00GiB --storage.tsdb.path=/prometheus
    --query.max-concurrency=20 --query.timeout=2m --web.config.file=/etc/prometheus/web_config/web-config.yaml
    --storage.tsdb.max-block-duration=2h --storage.tsdb.min-block-duration=2h --auto-gomemlimit.ratio=0.9)
  - config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es; /bin/prometheus-config-reloader
    --listen-address=:8080 --reload-url=http://localhost:9090/-/reload
    --config-file=/etc/prometheus/config/prometheus.yaml.gz
    --config-envsubst-file=/etc/prometheus/config_out/prometheus.env.yaml
    --watched-dir=/etc/prometheus/rules/prometheus-vmm-rulefiles-0)
  - thanos-sidecar (hub.easystack.io/production/thanos:v0.37.2-es; sidecar --prometheus.url=http://localhost:9090/
    --grpc-address=:10901 --http-address=:10902 --log.level=info
    --prometheus.http-client-file=/etc/thanos/config/prometheus.http-client-file.yaml --enable-auto-gomemlimit
    --auto-gomemlimit.ratio=0.9)
- Init containers:
  - init-config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es)

### thanos-ruler-ecms

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 2/2 ready
- Containers:
  - thanos-ruler (hub.easystack.io/production/thanos:v0.37.2-es; rule --data-dir=/thanos/data --eval-interval=30s
    --tsdb.retention=30d --label=thanos_ruler_replica="$(POD_NAME)" --label=public_vip="172.16.10.2"
    --alert.label-drop=thanos_ruler_replica --rule-file=/etc/thanos/rules/*/*.yaml --query=dnssrv+_web._tcp.thanos-query
    --alertmanagers.url=dnssrv+http://_web._tcp.alertmanager-operated
    --alert.relabel-config-file=/etc/thanos/config/alertrelabel-config/alertRelabelConfigs.yaml
    --alert.query-url=http://ecms-web-172-16-10-2.openstack.svc.cluster.local --enable-auto-gomemlimit
    --auto-gomemlimit.ratio=0.9 --http.config=/etc/thanos/web_config/web-config.yaml)
  - config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es; /bin/prometheus-config-reloader
    --listen-address=:8080 --web-config-file=/etc/thanos/web_config/web-config.yaml
    --reload-url=http://localhost:10902/-/reload --watched-dir=/etc/thanos/rules/thanos-ruler-ecms-rulefiles-0)
- Init containers:
  - -

### thanos-ruler-vmm

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 2/2 ready
- Containers:
  - thanos-ruler (hub.easystack.io/production/thanos:v0.37.2-es; rule --data-dir=/thanos/data --eval-interval=30s
    --tsdb.retention=200d --label=thanos_ruler_replica="$(POD_NAME)" --label=public_vip="172.16.10.2"
    --alert.label-drop=thanos_ruler_replica --rule-file=/etc/thanos/rules/*/*.yaml --query=dnssrv+_web._tcp.thanos-query
    --alertmanagers.url=dnssrv+http://_web._tcp.alertmanager-operated
    --alert.relabel-config-file=/etc/thanos/config/alertrelabel-config/alertRelabelConfigs.yaml
    --alert.query-url=http://ecms-web-172-16-10-2.openstack.svc.cluster.local --enable-auto-gomemlimit
    --auto-gomemlimit.ratio=0.9 --http.config=/etc/thanos/web_config/web-config.yaml)
  - config-reloader (hub.easystack.io/production/prometheus-config-reloader:v0.78.2-es; /bin/prometheus-config-reloader
    --listen-address=:8080 --web-config-file=/etc/thanos/web_config/web-config.yaml
    --reload-url=http://localhost:10902/-/reload --watched-dir=/etc/thanos/rules/thanos-ruler-vmm-rulefiles-0)
- Init containers:
  - -
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `alertmanager-ecms` | StatefulSet | 2 | Running:2 |
| `blackbox-exporter` | ReplicaSet | 3 | Running:3 |
| `kube-state-metrics-shard` | ReplicaSet | 2 | Running:2 |
| `mysqld-exporter` | ReplicaSet | 3 | Running:3 |
| `openstack-exporter` | ReplicaSet | 3 | Running:3 |
| `prometheus-ecms` | StatefulSet | 2 | Running:2 |
| `prometheus-operator` | ReplicaSet | 1 | Running:1 |
| `prometheus-vmm` | StatefulSet | 2 | Running:2 |
| `thanos-query-ecms` | ReplicaSet | 3 | Running:3 |
| `thanos-query-ecms-global` | ReplicaSet | 3 | Running:3 |
| `thanos-ruler-ecms` | StatefulSet | 2 | Running:2 |
| `thanos-ruler-vmm` | StatefulSet | 2 | Running:2 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `alertmanager` | ClusterIP | 9093/TCP |
| `openstack` | `alertmanager-operated` | ClusterIP | 9093/TCP, 9094/TCP, 9094/UDP |
| `openstack` | `blackbox-exporter` | ClusterIP | 9115/TCP |
| `openstack` | `kube-state-metrics-shard-0` | ClusterIP | 8080/TCP, 8081/TCP |
| `openstack` | `mysqld-exporter` | ClusterIP | 9104/TCP |
| `openstack` | `prometheus-operated` | ClusterIP | 9090/TCP, 10901/TCP |
| `openstack` | `prometheus-operator` | ClusterIP | 8443/TCP |
| `openstack` | `prometheus-shard-0` | ClusterIP | 9090/TCP |
| `openstack` | `prometheus-vmm-shard-0` | ClusterIP | 9090/TCP |
| `openstack` | `thanos-query` | ClusterIP | 10902/TCP, 10901/TCP |
| `openstack` | `thanos-query-global` | ClusterIP | 10902/TCP, 10901/TCP |
| `openstack` | `thanos-ruler` | ClusterIP | 10902/TCP |
| `openstack` | `thanos-ruler-operated` | ClusterIP | 10902/TCP, 10901/TCP |
| `openstack` | `thanos-ruler-vmm` | ClusterIP | 10902/TCP |

