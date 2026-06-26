# Scripts and Configuration

## ConfigMap Structure 结构

每个服务在 `openstack` namespace 中有两个 configmap:

- `<service>-etc` - 配置文件(如 `cinder.conf`, `api-paste.ini`)
- `<service>-bin` - 启动脚本和辅助脚本

```bash
kubectl get cm -n openstack <service>-etc -o yaml    # View config
kubectl get cm -n openstack <service>-bin -o yaml    # View scripts
```

## Script Pattern 脚本模式

每个 OpenStack 服务 pod 都遵循相同模式:

1. **Startup script**: `/tmp/<service>.sh`(从 `<service>-bin` configmap 挂载)
2. **Config files**: `/etc/<service>/`(从 `<service>-etc` configmap 挂载)
3. **Startup command**: `command: ["/tmp/<service>.sh", "start"]`

脚本通常支持 `start`/`stop` 子命令。部分服务(scheduler, compute)只使用
`["/tmp/<service>.sh"]`, 不带 `start` 参数。先检查脚本内容。

`/tmp/` 中的辅助脚本:
- Cinder: `ceph-keyring.sh`, `bootstrap.sh` (from `cinder-bin`)
- Glance: `glance-api.sh`
- Coaster: `coaster-all.sh`
- Cinder Golem: `/tmp/golem.sh`

## ConfigMap → Pod Mount Mapping 挂载关系

- `<service>-bin` → 挂载到 `/tmp/`(scripts)
- `<service>-etc` → 挂载到 `/etc/<service>/`(configs)

## Inspect Config/Script 查看配置和脚本

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
