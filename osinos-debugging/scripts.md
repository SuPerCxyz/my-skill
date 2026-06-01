# Scripts and Configuration

## ConfigMap Structure

Each service has two configmaps in `openstack` namespace:

- `<service>-etc` — configuration files (e.g., `cinder.conf`, `api-paste.ini`)
- `<service>-bin` — startup scripts and auxiliary scripts

```bash
kubectl edit cm -n openstack <service>-etc    # Edit config
kubectl edit cm -n openstack <service>-bin    # Edit scripts
```

## Script Pattern

Every OpenStack service pod follows the same pattern:

1. **Startup script**: `/tmp/<service>.sh` (mounted from `<service>-bin` configmap)
2. **Config files**: `/etc/<service>/` (mounted from `<service>-etc` configmap)
3. **Startup command**: `command: ["/tmp/<service>.sh", "start"]`

Scripts typically support `start`/`stop` subcommands. Some services (scheduler, compute)
use just `["/tmp/<service>.sh"]` without the `start` argument. Check script content first.

Auxiliary scripts in `/tmp/`:
- Cinder: `ceph-keyring.sh`, `bootstrap.sh` (from `cinder-bin`)
- Glance: `glance-api.sh`
- Coaster: `coaster-all.sh`
- Cinder Golem: `/tmp/golem.sh`

## ConfigMap → Pod Mount Mapping

- `<service>-bin` → mounted at `/tmp/` (scripts)
- `<service>-etc` → mounted at `/etc/<service>/` (configs)

## Debug Deployment Command (sleep 10d Pattern)

To debug code inside a pod:

```bash
# Step 1: Change the workload's command to sleep 10d
kubectl edit deployment -n openstack <service-name>         # For Deployments
kubectl edit statefulset -n openstack <service-name>        # For StatefulSets
kubectl edit daemonset -n openstack <service-name>          # For DaemonSetSets
# Change command from ["/tmp/service.sh", "start"] to ["sleep", "10d"]

# Step 2: Wait for pod to restart
kubectl get pod -n openstack -w

# Step 3: Exec into pod
kubectl exec -it -n openstack <pod-name> -- /bin/bash

# Step 4: Inside pod — edit code/config as needed
# Scripts are in /tmp/, configs in /etc/<service>/

# Step 5: Manually start the service
/tmp/<service>.sh start
# Or run code directly for debugging
python3 /path/to/module.py
```

When using `sleep 10d`, the service won't start automatically — you must exec in and start manually.

## Edit Config/Script and Restart Pod

```bash
# Step 1: Edit configmap or script
kubectl edit cm -n openstack <service>-etc
kubectl edit cm -n openstack <service>-bin

# Step 2: Restart pod (pick one)
kubectl delete pod -n openstack <pod-name>
kubectl rollout restart deployment -n openstack <service-name>
kubectl rollout restart statefulset -n openstack <service-name>
```

ConfigMap edits require pod restart to take effect. Pods mount configmaps read-only.
