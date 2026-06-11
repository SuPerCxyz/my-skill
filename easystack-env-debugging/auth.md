# OpenStack Authentication

## 重要：执行 OpenStack 命令前必须先 source 认证

**busybox pod 没有预设的 OS_ 环境变量，所有 openstack 命令必须在 source 之后执行。**

```bash
# ✅ 正确方式一：交互式 shell
kubectl exec -it -n openstack services/busybox -- bash
source /openrc
openstack volume list

# ✅ 正确方式二：一次性命令
kubectl exec -n openstack services/busybox -- bash -c 'source /openrc && openstack volume list'

# ❌ 错误方式（会报错：missing auth-url / missing OS_USERNAME）
kubectl exec -n openstack services/busybox -- openstack volume list
kubectl exec -n openstack services/busybox -- cinder show <volume-id>
```

## 两种用户身份

busybox 内可以通过不同认证方式切换身份：

| 用户 | 认证方式 | 用途 |
|------|---------|------|
| `drone` (service 项目用户) | `source /openrc` | 日常 openstack 操作 |
| `admin` | 手动 export 环境变量 | 需要管理员权限的操作 |

```bash
# 切到 drone 用户
source /openrc

# 切到 admin 用户（手动 export）
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME=admin
export OS_PASSWORD='<PASSWORD>'
export OS_AUTH_URL='http://keystone-api.openstack.svc.cluster.local/v3'
...
```

## Drone User (/openrc)

日常排障用 `source /openrc` 就够，admin 权限更大但很少需要。

## Drone User (/openrc)

`/openrc` contains `drone` user credentials (keystone v2.0 auth):

```bash
source /openrc
# Now you can run:
openstack volume list
openstack server list
cinder list
nova list
```

## Admin Credentials

For operations that need admin privileges:
