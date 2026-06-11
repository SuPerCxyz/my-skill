# Common Debugging Scenarios

## 命令执行位置（常见错误）

**不要**在业务 pod（如 cinder-golem、cinder-api、nova-api 等）中执行 openstack 命令，这些 pod 没有 CLI 工具和认证环境。

| 操作类型 | 执行位置 | 说明 |
|---------|---------|------|
| 普通 openstack 操作 | **busybox** pod | `source /openrc` 后执行 |
| Nova 高级管理操作 | **nova-maintenance-xxx** pod | cell 管理、迁移、宿主机维护 |
| cinder-manage 命令 | **cinder-volume** pod | 有 cinder 管理命令 |
| 业务日志查看 | 对应业务 pod | 用 `kubectl logs` 查看 |

## SSH 嵌套命令转义问题

从本机通过双层 SSH 到 K8s 节点执行复杂命令时，shell 引号和变量展开容易丢失。
进入环境后，通过 `ssh node-xxx` 的方式访问其他节点更可靠：

```bash
# 先进入 K8s 控制节点
ssh root@<TARGET_IP>
# 在控制节点上，直接 ssh 到其他节点
ssh node-3 'multipath -ll'
```

## Service Failing to Start

```bash
# 1. Check pod status and events
kubectl describe pod -n openstack <pod-name>

# 2. Check logs
kubectl logs -n openstack <pod-name> --tail=50
kubectl logs -n openstack <pod-name> --previous   # Previous instance if crashed

# 3. Check fluentd logs for recent activity
kubectl exec -n openstack fluentd-0 -c httpd -- ls /var/www/html/td-agent/openstack/<service>/

# 4. If config issue, edit and restart
kubectl edit cm -n openstack <service>-etc
kubectl delete pod -n openstack <pod-name>
```

## Database Issues

```bash
kubectl exec -it -n openstack mariadb-0 -- bash
mysql --defaults-file=/etc/mysql/admin_user.cnf

MariaDB> show databases;
MariaDB> use <service_name>;
MariaDB> show tables;
MariaDB> show processlist;
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

## Reverting a Bad Change

```bash
# Helm rollback is safest:
helm history -n openstack <release-name>
helm rollback -n openstack <release-name> <previous-revision>

# Or manually restore:
kubectl edit cm -n openstack <service>-etc  # undo changes, then restart pods
```
