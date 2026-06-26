# Common Debugging Scenarios

## 命令执行位置(常见错误)

**不要**在业务 pod(如 cinder-golem、cinder-api、nova-api 等)中执行 openstack 命令，这些 pod 没有 CLI 工具和认证环境。

| 操作类型 | 执行位置 | 说明 |
|---------|---------|------|
| 普通 openstack 操作 | **busybox** pod | `source /openrc` 后执行 |
| Nova 高级信息查看 | **nova-maintenance-xxx** pod | 仅查看 pod 和日志；管理操作需授权 |
| Cinder 信息查看 | **cinder-volume** pod | 仅查看日志和配置；manage 操作需授权 |
| 业务日志查看 | 对应业务 pod | 用 `kubectl logs` 查看 |

## SSH 访问与节点跳转

环境后台访问、`172.18.*` 跳板、JumpServer、连接验证和节点间跳转统一参考
[access.md](access.md)。场景排查文件不重复维护 SSH 命令，避免与实际入口方式冲突。

## Service Failing to Start

```bash
# 1. Check pod status and events
kubectl describe pod -n openstack <pod-name>

# 2. Check logs
kubectl logs -n openstack <pod-name> --tail=50
kubectl logs -n openstack <pod-name> --previous   # Previous instance if crashed

# 3. Check fluentd logs for recent activity
kubectl exec -n openstack fluentd-0 -c httpd -- ls /var/www/html/td-agent/openstack/<service>/

# 4. If config issue, inspect config only
kubectl get cm -n openstack <service>-etc -o yaml
kubectl describe pod -n openstack <pod-name>
```

## Database Issues

```bash
kubectl exec -n openstack mariadb-0 -- mysql --defaults-file=/etc/mysql/admin_user.cnf -e "show databases;"
kubectl exec -n openstack mariadb-0 -- mysql --defaults-file=/etc/mysql/admin_user.cnf -e "show processlist;"
```

When deeper database inspection is needed, keep SQL read-only:

```sql
show databases;
use <service_name>;
show tables;
show processlist;
```

Common service databases: `keystone`, `nova`/`nova_api`/`nova_cell0`, `cinder`, `glance`, `neutron`.

## Configuration Debugging

```bash
# View a configmap (don't edit yet)
kubectl get cm -n openstack <service>-etc -o yaml

# Find the specific config file
kubectl get cm -n openstack <service>-etc -o yaml | grep "cinder.conf\|nova.conf"

# Check current mounted config in a running pod
kubectl exec -n openstack <pod-name> -- cat /etc/<service>/<config-file>
```

## Inspecting a Bad Change

```bash
# View Helm history only
helm history -n openstack <release-name>

# View current config only
kubectl get cm -n openstack <service>-etc -o yaml
```

Rollback, manual restore, ConfigMap edits, and pod restarts affect the environment.
Do not run them unless the user explicitly authorizes that exact change.
