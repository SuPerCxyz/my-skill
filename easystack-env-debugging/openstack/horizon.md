# OpenStack horizon

`horizon` 组件 pod、启动方式和排查入口参考。

## Workload 启动方式

| 启动方式 | Workload | Containers |
|----------|----------|------------|
| Deployment | `horizon` | nginx<br>horizon |
| Job | `horizon-cached-db-init-631` | horizon-cached-db-init |
| Job | `horizon-ecpbackendcheck-1782348112` | horizon-ecpbackendcheck |
