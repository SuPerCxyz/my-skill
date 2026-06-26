# Logs

Use this file when the question is about runtime logs in a reachable environment. For offline `.eslog` bundles, use the log-analysis skill instead.

## Real-time Logs (kubectl)

Service logs go to stdout/stderr, not `/var/log/` inside pods.

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

## Historical Logs (Fluentd)

3 fluentd pods (`fluentd-0`, `fluentd-1`, `fluentd-2`), each holding logs from a **different node**.
To get complete logs for a service, check all 3.

**Log location:** `/var/www/html/td-agent/openstack/<service>/<component>.<node>.<YYYYMMDD>.log.gz`

**Directory structure:**
```
/var/www/html/td-agent/
├── openstack/          ← OpenStack service logs (nova, cinder, glance, keystone, ...)
├── ceph/               ← Ceph service logs
├── kubernetes/         ← K8s component logs
├── archives/           ← Older rotated logs (may be empty if cleaned)
```

**Access fluentd pods** (default container is `httpd`):
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

**Log line format** (pipe-delimited):
```
<fluentd-timestamp> | <node-name> | <pod-name> | <service-name> | <actual log line>
```

**When to use fluentd vs kubectl logs:**
- `kubectl logs` - real-time, current pod only, not persisted after pod restart
- Fluentd - historical, across all nodes, persisted (daily rotation), searchable across replicas
