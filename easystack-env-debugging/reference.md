# Reference - Environment Constants and Namespaces

## Environment Constants

```
Keystone Auth URL (busybox):  http://keystone-api.openstack.svc.cluster.local/v3
Keystone Public URL:          http://keystone-api.openstack.svc.cluster.local:80/v3
Keystone Public (APISIX):     http://keystone.openstack.svc.cluster.local:80/v3
Region:                       RegionOne
Interface for local client:   publicURL (APISIX only exposes port 80)
Interface for busybox:        adminURL
Python:                       python3 (in most pods)
OpenStack CLI (busybox):      /usr/bin/openstack
MySQL CLI (busybox):          /usr/bin/mysql
```

## Default Credentials

(Confirm with user - may vary per environment)

```
SSH jump host password:       easystack
OpenStack admin password:     Admin@ES20!8
MariaDB root password:        stored in /etc/mysql/admin_user.cnf on mariadb-0
```

## ChartMuseum

```
URL:     http://chartmuseum.openstack.svc.cluster.local:8090
Pod:     chartmuseum-0
NS:      openstack
```

## Namespaces

| Namespace | Purpose |
|-----------|---------|
| `openstack` | Core OpenStack services |
| `ceph` | Ceph storage (RGW for Swift) |
| `apisix` | API gateway |
| `ems` | Management services (peak) |
| `octavia` | Load balancer |
| `kube-system` | K8s system |
