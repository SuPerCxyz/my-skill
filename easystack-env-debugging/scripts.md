# Scripts and Configuration

## ConfigMap Structure

Each service has two configmaps in `openstack` namespace:

- `<service>-etc` - configuration files (e.g., `cinder.conf`, `api-paste.ini`)
- `<service>-bin` - startup scripts and auxiliary scripts

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

## Startup-Time Code Overlay Debugging

Do not replace workload commands with `sleep 10d` for normal service debugging.
Instead, keep the service's normal startup path and inject a code overlay step at the
beginning of the startup script so the pod can start normally and still emit logs through
`kubectl logs`.

Recommended pattern:

```bash
# In the startup script's beginning, before the real service launch:
cp -rf /opt/<service>/* /path/to/site-packages/<service>/

# Then continue normal startup
exec /usr/bin/python3 -m <service>.main
```

Key points:

- Edit the startup script content in the `<service>-bin` ConfigMap or its mounted file
- Use the node-mounted `/opt/<service>/` directory as the source of debug code
- Copy the overlay into the container's target package directory before service startup
- Keep the original process running so `kubectl logs` remains the primary observability path

If the service needs a temporary manual shell for one-off debugging, prefer an interactive
`kubectl exec` session over changing the workload command.

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
