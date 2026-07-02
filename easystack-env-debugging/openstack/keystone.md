# OpenStack keystone

`keystone` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `keystone-api` | keystone-api |
| Job | `keystone-bootstrap` | keystone-bootstrap |
| Job | `keystone-credential-setup` | keystone-credential-setup |
| Job | `keystone-db-init` | keystone-db-init |
| Job | `keystone-db-migrate` | keystone-db-migrate |
| Job | `keystone-db-sync` | keystone-db-sync |
| Job | `keystone-fernet-setup` | keystone-fernet-setup |
| Job | `keystone-idp-setup` | keystone-idp-setup |
| Job | `keystone-poll-ldap-users-29706720` | keystone-poll-ldap-users |
