# Reference - Essential Commands and Constants

## Essential Commands

```bash
# SSH to target node (replace IPs per environment)
sshpass -p "easystack" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@<JUMP_IP> 'ssh -i .ssh/id_rsa.roller <TARGET_NODE_IP>'

# Enter busybox pod (has openstack CLI, mysql client)
kubectl exec -it -n openstack services/busybox -- bash

# Enter mariadb pod for database access
kubectl exec -it -n openstack mariadb-0 -- bash
mysql --defaults-file=/etc/mysql/admin_user.cnf

# Restart a service
kubectl rollout restart deployment -n openstack <service-name>   # Deployment
kubectl rollout restart statefulset -n openstack <service-name>  # StatefulSet
kubectl delete pod -n openstack <pod-name>                       # Force recreate

# Check rollout status
kubectl rollout status deployment -n openstack <service-name> --timeout=120s

# Find which node a pod runs on (useful for /opt debugging)
kubectl get pod -n openstack <pod-name> -o wide

# Find all pods for a service
kubectl get pods -n openstack | grep <service>
```

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

## Important Notes

- ConfigMap edits require pod restart to take effect
- Pods mount configmaps read-only; editing requires modifying the configmap and restarting the pod
- Service logs go to stdout (via `kubectl logs`), not `/var/log/` inside pods
- Neutron uses OVN mode - no standalone `neutron-server` pods exist
- For multi-container pods, always specify `-c <container-name>` with `logs` and `exec`
- For multi-replica API services, changes to configmaps affect all replicas equally
- Helm releases track versions - use `helm history` and `helm rollback` for quick recovery
- Fluentd collects logs from all nodes - each of the 3 fluentd pods holds logs from a different node
- Fluentd default container is `httpd`; use `-c httpd` when exec'ing into fluentd pods
- `kubectl exec -it -n openstack services/busybox -- bash` enters the busybox pod via service selector
- Local OpenStack client maps endpoint hostnames to jump host IP in `/etc/hosts`, use `publicURL`
- Light queries (list, show) run locally; heavy I/O (image upload) runs in busybox pod
