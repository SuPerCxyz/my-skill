# OpenStack keystone

记录 `keystone` 相关组件在本次环境中的部署情况、pod 和启动方式。

## Helm Release

| Namespace | Release | Chart | Status |
|-----------|---------|-------|--------|
| `openstack` | `keystone` | `keystone-7.0.1-alpha.103` | DEPLOYED |

## Workload 启动方式

| Namespace | 启动方式 | Workload | Ready/状态 | Containers | Init containers |
|-----------|----------|----------|------------|------------|-----------------|
| `openstack` | Deployment | `keystone-api` | 3/3 ready | keystone-api | init |
| `openstack` | Job | `keystone-bootstrap` | succeeded=1, failed=0 | keystone-bootstrap | init |
| `openstack` | Job | `keystone-credential-setup` | succeeded=1, failed=0 | keystone-credential-setup | init |
| `openstack` | Job | `keystone-db-init` | succeeded=1, failed=0 | keystone-db-init | init |
| `openstack` | Job | `keystone-db-migrate` | succeeded=1, failed=0 | keystone-db-migrate | init |
| `openstack` | Job | `keystone-db-sync` | succeeded=1, failed=0 | keystone-db-sync | init |
| `openstack` | Job | `keystone-fernet-setup` | succeeded=1, failed=0 | keystone-fernet-setup | init |
| `openstack` | Job | `keystone-idp-setup` | succeeded=1, failed=0 | keystone-idp-setup | init |
| `openstack` | Job | `keystone-poll-ldap-users-29706720` | succeeded=1, failed=0 | keystone-poll-ldap-users | init |

## Container Details 容器详情

### keystone-api

- Namespace: `openstack`
- 启动方式: Deployment
- 状态: 3/3 ready
- Containers:
  - keystone-api (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; /tmp/keystone-api.sh start)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-bootstrap

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-bootstrap (hub.easystack.io/production/escloud-linux-source-heat-engine:6.0.2; /tmp/bootstrap.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-credential-setup

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-credential-setup (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; python
    /tmp/fernet-manage.py credential_setup)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-db-init

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-db-init (hub.easystack.io/production/escloud-linux-source-heat-engine:6.0.2; /tmp/db-init.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-db-migrate

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-db-migrate (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; /db-migrate.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-db-sync

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-db-sync (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; /tmp/db-sync.sh)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-fernet-setup

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-fernet-setup (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; python
    /tmp/fernet-manage.py fernet_setup)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-idp-setup

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-idp-setup (hub.easystack.io/production/escloud-linux-source-keystone:7.0.1-alpha.103; python /idp-setup.py
    idp_setup)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)

### keystone-poll-ldap-users-29706720

- Namespace: `openstack`
- 启动方式: Job
- 状态: succeeded=1, failed=0
- Containers:
  - keystone-poll-ldap-users (hub.easystack.io/production/escloud-linux-source-heat-engine:6.0.2; python
    /tmp/poll_users_from_ldap.py)
- Init containers:
  - init (hub.easystack.io/production/kubernetes-entrypoint:v0.2.1)
## Pod 分布

| Pod 组 | Owner 类型 | 数量 | 状态 |
|--------|------------|------|------|
| `keystone-api` | ReplicaSet | 3 | Running:3 |
| `keystone-bootstrap` | Job | 1 | Succeeded:1 |
| `keystone-credential-setup` | Job | 1 | Succeeded:1 |
| `keystone-db-init` | Job | 1 | Succeeded:1 |
| `keystone-db-migrate` | Job | 1 | Succeeded:1 |
| `keystone-db-sync` | Job | 1 | Succeeded:1 |
| `keystone-fernet-setup` | Job | 1 | Succeeded:1 |
| `keystone-idp-setup` | Job | 1 | Succeeded:1 |
| `keystone-poll-ldap` | Job | 1 | Succeeded:1 |
## Service 暴露

| Namespace | Service | Type | Ports |
|-----------|---------|------|-------|
| `openstack` | `keystone` | ExternalName | 80/TCP |
| `openstack` | `keystone-api` | ClusterIP | 80/TCP, 35357/TCP |

