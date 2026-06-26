# Scripts and Configuration

## ConfigMap Structure

Each service has two configmaps in `openstack` namespace:

- `<service>-etc` - configuration files (e.g., `cinder.conf`, `api-paste.ini`)
- `<service>-bin` - startup scripts and auxiliary scripts

```bash
kubectl get cm -n openstack <service>-etc -o yaml    # View config
kubectl get cm -n openstack <service>-bin -o yaml    # View scripts
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

## Inspect Config/Script

```bash
# View configmap or script without changing state
kubectl get cm -n openstack <service>-etc -o yaml
kubectl get cm -n openstack <service>-bin -o yaml

# View how pods mount the configmaps
kubectl describe pod -n openstack <pod-name>
```

ConfigMap edits and pod restarts affect the environment. Do not run `kubectl edit`,
`kubectl delete pod`, or `kubectl rollout restart` unless the user explicitly
authorizes that exact change.
