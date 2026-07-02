# OpenStack infrastructure

基础组件 pod、启动方式和排查入口参考。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `busybox` | `busybox-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `chartmuseum` | `chartmuseum-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `chrony` | `chrony-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `docker-registry` | `docker-registry-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `keepalived` | `keepalived-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `libvirt` | `libvirt-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `mariadb` | `mariadb-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `memcached` | `memcached-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `mongodb` | `mongodb-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `rabbitmq` | `rabbitmq-7.0.1-alpha.103` | DEPLOYED |
| `openstack` | `redis` | `redis-7.0.1-alpha.103` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | DaemonSet | `keepalived` | 3/3 ready | keepalived | - |
| `openstack` | DaemonSet | `libvirt` | 3/3 ready | etcd-client<br>etcdlock-manager<br>libvirt<br>libvirt-sync | reservation-key-gen<br>ceph-keyring-placement<br>ceph-conf-placement |
| `openstack` | DaemonSet | `libvirt-exporter` | 3/3 ready | libvirt-exporter | init |
| `openstack` | Deployment | `busybox-openstack` | 1/1 ready | busybox-openstack | - |
| `openstack` | Deployment | `chrony` | 1/1 ready | chrony | - |
| `openstack` | Deployment | `fluentd-api` | 3/3 ready | fluentd-api | init |
| `openstack` | Deployment | `memcached` | 3/3 ready | memcached | - |
| `openstack` | Deployment | `redis` | 1/1 ready | redis | init |
| `openstack` | Job | `mariadb-backup-incr-29706900` | succeeded=1, failed=0 | mariadb-backup-incr | grep busybox-openstack \     \ |
| `openstack` | Job | `mongodb-backup-full-29706960` | succeeded=1, failed=0 | mongodb-backup-full | grep busybox-openstack \     \ |
| `openstack` | Job | `rabbitmq-bootstrap-6.0.1` | succeeded=1, failed=0 | rabbitmq-bootstrap | init |
| `openstack` | StatefulSet | `chartmuseum` | 1/1 ready | chartmuseum | permissionadopt |
| `openstack` | StatefulSet | `docker-registry` | 1/1 ready | docker-registry<br>image-manager | - |
| `openstack` | StatefulSet | `fluentd` | 3/3 ready | httpd<br>fluentd | init |
| `openstack` | StatefulSet | `mariadb` | 3/3 ready | mariadb | init |
| `openstack` | StatefulSet | `mongodb` | 1/1 ready | mongodb | - |
| `openstack` | StatefulSet | `rabbitmq` | 3/3 ready | rabbitmq | init<br>rabbit-init-check |

## Container Details 容器详情

### keepalived

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - keepalived (hub.easystack.io/production/escloud-linux-source-keepalived:v2.3.4; /scripts/start.sh)
- Init containers:
  - -

### libvirt

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - etcd-client (hub.easystack.io/production/escloud-linux-source-etcdlock-manager:7.0.1-alpha.103; /usr/sbin/etcd_client)
  - etcdlock-manager (hub.easystack.io/production/escloud-linux-source-etcdlock-manager:7.0.1-alpha.103;
    /tmp/etcdlock_manager.sh)
  - libvirt (hub.easystack.io/production/escloud-linux-source-libvirt:7.0.1-alpha.103; /tmp/libvirt.sh)
  - libvirt-sync (hub.easystack.io/production/escloud-linux-source-libvirt:7.0.1-alpha.103; /tmp/sync-hosts.sh)
- Init containers:
  - reservation-key-gen (hub.easystack.io/production/escloud-linux-source-libvirt:7.0.1-alpha.103)
  - ceph-keyring-placement (hub.easystack.io/production/escloud-linux-source-libvirt:7.0.1-alpha.103)
  - ceph-conf-placement (hub.easystack.io/production/escloud-linux-source-libvirt:7.0.1-alpha.103)

### libvirt-exporter

- Namespace: `openstack`
- 启动方式: DaemonSet
- 状态: 3/3 ready
- Containers:
  - libvirt-exporter (hub.easystack.io/production/escloud-linux-source-libvirt-exporter:7.0.1-alpha.28; image default
    entrypoint)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### busybox-openstack

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - busybox-openstack (hub.easystack.io/production/escloud-linux-source-busybox:7.0.1-alpha.103; /tmp/startup.sh)
- Init containers:
  - -

### chrony

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - chrony (hub.easystack.io/production/escloud-linux-source-chrony:7.0.1-alpha.103; /tmp/chronyd-start.sh)
- Init containers:
  - -

### fluentd-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - fluentd-api (hub.easystack.io/production/escloud-linux-source-busybox:latest; /tmp/fluentd-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### memcached

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - memcached (hub.easystack.io/production/memcached:1.6.39-es; /tmp/start.sh)
- Init containers:
  - -

### redis

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 1/1 ready
- Containers:
  - redis (hub.easystack.io/production/redis:7.2.13-es; redis-server --port 6379 --requirepass Y6VhhX_DjXKfrWQJ)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### mariadb-backup-incr-29706900

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - mariadb-backup-incr (hub.easystack.io/production/mariadb:10.11.14-es; /bin/bash -ec send_failure_mail() {   local
    exit_code="$1"   local backup_kind="incr"   local backup_kind_cn="增量"   local busybox_pod   local mail_lang   local
    mail_lang_rc   local mail_rc   local subject   local body    if [ "${backup_kind}" = "full" ]; then
    backup_kind_cn="全量"   fi    busybox_pod=$(/tmp/kubectl get po -n "${NAMESPACE}" \     \
- Init containers:
  - grep busybox-openstack \     \

### mongodb-backup-full-29706960

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - mongodb-backup-full (hub.easystack.io/production/mongodb:8.0.13-ubuntu2204-es; /bin/bash -ec send_failure_mail() {
    local exit_code="$1"   local busybox_pod   local mail_lang   local mail_lang_rc   local mail_rc   local subject   local
    body    busybox_pod=$(/tmp/kubectl get po -n "${NAMESPACE}" \     \
- Init containers:
  - grep busybox-openstack \     \

### rabbitmq-bootstrap-6.0.1

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - rabbitmq-bootstrap (hub.easystack.io/production/rabbitmq:3.13.7-es; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### chartmuseum

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - chartmuseum (hub.easystack.io/production/es-chartmuseum:v0.16.3-es; --port=8090 --storage=local --depth=0
    --storage-local-rootdir=/storage)
- Init containers:
  - permissionadopt (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### docker-registry

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - docker-registry (hub.easystack.io/production/registry:v3; /bin/registry serve /etc/docker/registry/config.yml)
  - image-manager (hub.easystack.io/production/escloud-linux-source-openstack-base:6.1.1; /usr/bin/gunicorn --timeout 3600
    --chdir /tmp/ -w 1 -b 0.0.0.0:5007 image-manager:app)
- Init containers:
  - -

### fluentd

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - httpd (hub.easystack.io/production/escloud-linux-source-busybox:latest; /tmp/httpd.sh start)
  - fluentd (hub.easystack.io/production/fluentd:v1.6.2-1.0-es; /tmp/fluentd.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### mariadb

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - mariadb (hub.easystack.io/production/mariadb:10.11.14-es; /tmp/start.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### mongodb

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 1/1 ready
- Containers:
  - mongodb (hub.easystack.io/production/mongodb:8.0.13-ubuntu2204-es; /tmp/start.sh)
- Init containers:
  - -

### rabbitmq

- Namespace: `openstack`
- 启动方式: StatefulSet
- 状态: 3/3 ready
- Containers:
  - rabbitmq (hub.easystack.io/production/rabbitmq:3.13.7-es; /scripts/start.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
  - rabbit-init-check (hub.easystack.io/production/rabbitmq:3.13.7-es)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `busybox-openstack` | ReplicaSet | 1 | Running:1 |
| `chartmuseum` | StatefulSet | 1 | Running:1 |
| `chrony` | ReplicaSet | 1 | Running:1 |
| `docker-registry` | StatefulSet | 1 | Running:1 |
| `fluentd` | StatefulSet | 3 | Running:3 |
| `fluentd-api` | ReplicaSet | 3 | Running:3 |
| `keepalived` | DaemonSet | 3 | Running:3 |
| `libvirt` | DaemonSet | 3 | Running:3 |
| `libvirt-exporter` | DaemonSet | 3 | Running:3 |
| `mariadb` | StatefulSet | 3 | Running:3 |
| `mariadb-backup-incr` | Job | 1 | Succeeded:1 |
| `memcached` | ReplicaSet | 3 | Running:3 |
| `mongodb` | StatefulSet | 1 | Running:1 |
| `mongodb-backup-full` | Job | 1 | Succeeded:1 |
| `rabbitmq` | StatefulSet | 3 | Running:3 |
| `rabbitmq-bootstrap-6.0.1` | Job | 1 | Succeeded:1 |
| `redis` | ReplicaSet | 1 | Running:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `busybox` | ClusterIP | 80/TCP, 4200/TCP, 8000/TCP, 8899/TCP, 8080/TCP |
| `openstack` | `chartmuseum-chartmuseum` | ClusterIP | 8090/TCP |
| `openstack` | `chronyd` | NodePort | 123/UDP |
| `openstack` | `docker-registry` | ClusterIP | 443/TCP, 5007/TCP |
| `openstack` | `fluentd` | ClusterIP | 24224/TCP, 24280/TCP, 24231/TCP |
| `openstack` | `fluentd-logging` | ClusterIP | 80/TCP |
| `openstack` | `libvirt-exporter` | ClusterIP | 8778/TCP |
| `openstack` | `mariadb` | ClusterIP | 3306/TCP |
| `openstack` | `mariadb-discovery` | ClusterIP | 3306/TCP |
| `openstack` | `memcached` | ClusterIP | 11211/TCP |
| `openstack` | `mongodb` | ClusterIP | 27017/TCP |
| `openstack` | `rabbitmq` | NodePort | 5672/TCP, 15672/TCP |
| `openstack` | `rabbitmq-discovery` | ClusterIP | 5672/TCP |
| `openstack` | `redis` | ClusterIP | 6379/TCP |
