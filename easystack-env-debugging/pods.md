# Pod Patterns

Use this file when selecting pods, containers, labels, or controllers for read-only inspection. It is the reference for avoiding wrong-container `exec` and `logs` calls.

## Multi-Container Pods

Always check containers before `exec` or `logs`:

```bash
kubectl get pod -n openstack <pod-name> -o jsonpath='{.spec.containers[*].name}'
```

Most service pods follow a pattern of **init container + business container**, some may have multiple business containers. Always specify `-c <container-name>` when exec'ing into non-default containers.

Examples:
- `mariadb-0` → `mariadb` (single container, no `-c` needed)
- `fluentd-0` → `httpd` (default) + `fluentd`
- `cinder-api-*` → `cinder-api` (default) + `init` (init container)
- `cinder-golem-*` → `golem` (default) + `init`

When in doubt, use `-c <container-name>` explicitly.

## Exec by Pod Name, Not Service Label

Avoid `kubectl exec -n <ns> -l service=<name>` for service pods. Pods with init
containers may print `Defaulted container ...`, and label-based `exec` is less
predictable across kubectl versions and pod layouts.

Prefer confirming labels, resolving the pod name first, then exec by concrete pod name:

```bash
kubectl get pods -n <ns> --show-labels | grep <name>
pod=$(kubectl get pods -n <ns> -l service=<name> -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n <ns> "$pod" -c <container-name> -- <read-only-command>
```

Use the `service=<name>` selector only after confirming that the pod actually has
that label. If using a set selector such as `-l 'service in (a,b,c)'`, verify
that the target kubectl version supports it. Otherwise split the query into
separate `-l service=a`, `-l service=b`, and `-l service=c` calls.

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
