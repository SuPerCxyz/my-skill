# Common Debugging Scenarios

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
