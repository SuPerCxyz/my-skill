# Logs

当问题涉及可访问环境中的运行时日志时阅读本文件。离线 `.eslog` 包应使用
log-analysis skill。

## Real-time Logs (kubectl) 实时日志

服务日志输出到 stdout/stderr, 不写入 pod 内的 `/var/log/`。

```bash
# Single-container pod
kubectl logs -f -n openstack <pod-name>

# Multi-container pod - specify container name
kubectl logs -f -n openstack <pod-name> -c <container-name>

# List containers first
kubectl get pod -n openstack <pod-name> -o jsonpath='{.spec.containers[*].name}'

# Tail last N lines
kubectl logs -n openstack <pod-name> --tail=200

# Previous instance (if crashed/restarted)
kubectl logs -n openstack <pod-name> --previous
```

## Historical Logs (Fluentd) 历史日志

3 个 fluentd pod(`fluentd-0`, `fluentd-1`, `fluentd-2`)分别保存**不同节点**上的日志。
要获取某个服务的完整日志, 需要检查 3 个 pod。

**日志位置:** `/var/www/html/td-agent/openstack/<service>/<component>.<node>.<YYYYMMDD>.log.gz`

**目录结构:**
```
/var/www/html/td-agent/
├── openstack/          ← OpenStack service logs (nova, cinder, glance, keystone, ...)
├── ceph/               ← Ceph service logs
├── kubernetes/         ← K8s component logs
├── archives/           ← Older rotated logs (may be empty if cleaned)
```

**访问 fluentd pod**(默认容器为 `httpd`):
```bash
# View logs for a specific service on one fluentd pod
kubectl exec -n openstack fluentd-0 -c httpd -- ls /var/www/html/td-agent/openstack/<service>/

# Read a specific log file
kubectl exec -n openstack fluentd-0 -c httpd -- zcat /var/www/html/td-agent/openstack/<service>/<component>.node-<N>.<date>.log.gz | tail -100
```

**Search across all 3 fluentd pods** (requires interactive SSH shell on target node):
```bash
# First enter the target node via SSH, then run:
for i in 0 1 2; do
  echo "=== fluentd-$i ==="
  kubectl exec -n openstack fluentd-$i -c httpd -- ls /var/www/html/td-agent/openstack/<service>/ 2>/dev/null
done

# Search log content across all pods:
for i in 0 1 2; do
  echo "=== fluentd-$i ==="
  kubectl exec -n openstack fluentd-$i -c httpd -- sh -c 'zcat /var/www/html/td-agent/openstack/<service>/*.gz 2>/dev/null' | grep "<search-keyword>" | tail -20
done
```

按资源 UUID 搜日志时, 先搜对应服务目录, 例如 volume 查 `openstack/cinder`,
server 查 `openstack/nova`。如果用户明确要求直接看日志, 可以跳过数据库查询。

```bash
for i in 0 1 2; do
  echo "=== fluentd-$i ==="
  kubectl exec -n openstack fluentd-$i -c httpd -- sh -c 'zgrep -h -F "<resource-uuid>" /var/www/html/td-agent/openstack/<service>/*.gz 2>/dev/null' | tail -50
done
```

**日志行格式**(以竖线分隔):
```
<fluentd-timestamp> | <node-name> | <pod-name> | <service-name> | <actual log line>
```

**何时使用 fluentd 或 kubectl logs:**
- `kubectl logs` - 实时日志, 仅当前 pod, pod 重启后不保留
- Fluentd - 历史日志, 覆盖所有节点, 持久化保存(按天轮转), 可跨副本搜索
