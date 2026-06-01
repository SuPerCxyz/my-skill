# Pod Patterns

## Multi-Container Pods

Always check containers before `exec` or `logs`:

```bash
kubectl get pod -n openstack <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

Examples:
- `mariadb-0` → `mariadb` (kubectl auto-defaults this, no `-c` needed for most commands)
- `fluentd-0` → `httpd` (default) + `fluentd`
- `cinder-api-*` → `cinder-api` (default) + `init` (init container)

When in doubt, use `-c <container-name>` explicitly.

## Multi-Replica Pods (API Services)

API services typically run 3 replicas. Changes to configmaps affect all replicas equally.

```bash
# Quick way: grep the first running pod
kubectl get pods -n openstack | grep <service>-api | head -1

# Or by label selector (component name varies):
# cinder: component=api, nova: component=os-api, glance: component=api
kubectl get pods -n openstack --selector=application=<service>,component=api --field-selector=status.phase=Running
```

When restarting a deployment, all pods are recreated automatically.

## StatefulSet vs Deployment vs DaemonSet

| Type | Examples | Pod Names | Restart Behavior |
|------|----------|-----------|-----------------|
| **Deployment** | `cinder-api-*`, `nova-conductor-*` | Random suffix (e.g., `cinder-api-6b58d8ddd6-jncth`) | New pod with new name |
| **StatefulSet** | `glance-api-0`, `mariadb-0` | Numbered (`-0`, `-1`, `-2`) | Same name, has persistent volumes |
| **DaemonSet** | `ovn-controller-*`, `nova-compute-*` | One per compute node | Same name on same node |
