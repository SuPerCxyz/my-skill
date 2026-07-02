# OpenStack infrastructure

基础组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| DaemonSet | `keepalived` | keepalived |
| DaemonSet | `libvirt` | etcd-client<br>etcdlock-manager<br>libvirt<br>libvirt-sync |
| DaemonSet | `libvirt-exporter` | libvirt-exporter |
| Deployment | `busybox-openstack` | busybox-openstack |
| Deployment | `chrony` | chrony |
| Deployment | `fluentd-api` | fluentd-api |
| Deployment | `memcached` | memcached |
| Deployment | `redis` | redis |
| Job | `mariadb-backup-incr-29706900` | mariadb-backup-incr |
| Job | `mongodb-backup-full-29706960` | mongodb-backup-full |
| Job | `rabbitmq-bootstrap-6.0.1` | rabbitmq-bootstrap |
| StatefulSet | `chartmuseum` | chartmuseum |
| StatefulSet | `docker-registry` | docker-registry<br>image-manager |
| StatefulSet | `fluentd` | httpd<br>fluentd |
| StatefulSet | `mariadb` | mariadb |
| StatefulSet | `mongodb` | mongodb |
| StatefulSet | `rabbitmq` | rabbitmq |
