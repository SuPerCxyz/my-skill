# OpenStack Authentication

## Admin Credentials (for debugging inside the cluster)

The busybox pod in `openstack` namespace has the `openstack` CLI at `/usr/bin/openstack`.

```bash
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME=admin
export OS_PASSWORD='<PASSWORD>'        # default: Admin@ES20!8, may vary per env
export OS_AUTH_URL='http://keystone-api.openstack.svc.cluster.local/v3'
export OS_REGION_NAME="RegionOne"
export OS_INTERFACE=adminURL
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

To get the admin project ID:
```bash
kubectl exec -it -n openstack services/busybox -- bash
env -i PATH=/usr/bin:/usr/local/bin:/bin HOME=/root OS_IDENTITY_API_VERSION=3 OS_USERNAME=admin OS_PASSWORD='<PASSWORD>' OS_AUTH_URL=http://keystone-api.openstack.svc.cluster.local/v3 OS_REGION_NAME=RegionOne OS_INTERFACE=adminURL OS_PROJECT_NAME=admin OS_USER_DOMAIN_NAME=Default OS_PROJECT_DOMAIN_NAME=Default /usr/bin/openstack token issue
```

The project ID from the token output is used as `OS_PROJECT_ID` when needed.

## Auth Command Template

```bash
# Quick interactive shell in busybox pod
kubectl exec -it -n openstack services/busybox -- bash

# One-shot OpenStack CLI command
kubectl exec -n openstack services/busybox -- env -i PATH=/usr/bin:/usr/local/bin:/bin HOME=/root OS_IDENTITY_API_VERSION=3 OS_USERNAME=admin OS_PASSWORD='<PASSWORD>' OS_AUTH_URL=http://keystone-api.openstack.svc.cluster.local/v3 OS_REGION_NAME=RegionOne OS_INTERFACE=adminURL OS_PROJECT_NAME=admin OS_USER_DOMAIN_NAME=Default OS_PROJECT_DOMAIN_NAME=Default /usr/bin/openstack <command>
```

## Drone User (Limited)

`/openrc.v3.domain` contains `drone` user credentials with limited permissions.
Gets 403 on many operations — use admin credentials for debugging.
