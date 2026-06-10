# Environment Access

## SSH Chain - 标准路径

**跳板机 → K8s 控制节点 (10.20.0.3)**

```bash
# 一步执行远端命令
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@10.20.0.3' "<kubectl-command>"

# 交互式会话
sshpass -p "easystack" ssh -tt -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@10.20.0.3'
```

- `<JUMP_IP>` 由用户指定（如 `172.18.0.133`、`172.18.0.242`）
- K8s 控制节点固定为 **10.20.0.3**，不需要扫描或查找其他节点
- 所有 `kubectl` 命令直接在远端执行，不要在本机扫描网络或试探节点
- 跳板机本身没有 kubectl，必须内层 SSH 到 10.20.0.3
- `easystack` 密码可能因环境不同，未知时询问用户

## 注意事项

- `for` 循环和复杂脚本不能通过嵌套 SSH 引号传递，需要先建立交互式 SSH 会话再执行
- 必须加 `-F /dev/null` 避免本机 ssh_config 干扰

## 嵌套 SSH + 复杂命令：可靠传递模式

多层 SSH 下，复杂 shell 逻辑最容易在引号、`$@`、`$$`、变量展开和转义上丢失。
如果命令里包含多行逻辑、循环、条件分支或需要精确保留参数，**唯一可靠的传递方式**是：

1. 先把复杂逻辑写成 Python 脚本
2. 在本机将脚本 `base64` 编码
3. 通过 SSH 管道把编码内容发送到远端
4. 远端解码后执行

示例：

```bash
python3 <<'PY' | base64 -w0 | sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@10.20.0.3 "base64 -d | python3"'
from pathlib import Path

print("hello from remote script")
PY
```

适用场景：

- 多层 SSH 远端执行复杂逻辑
- 需要保留 Python 字符串、`$@`、`$$`、引号和换行
- 临时排障脚本，不想把逻辑拆成一串难维护的一次性 shell 引号

## Local OpenStack Client via Endpoint Mapping

The jump host runs APISIX which routes requests by Host header.
Add all endpoint hostnames to `/etc/hosts` pointing to the jump host IP,
then install `python-openstackclient` locally:

```bash
# Step 1: Add endpoints to /etc/hosts (map to jump host IP)
<JUMP_IP> aodh-api.openstack.svc.cluster.local aodh.openstack.svc.cluster.local ceilometer-api.openstack.svc.cluster.local ceilometer.openstack.svc.cluster.local ceph-rgw.ceph.svc.cluster.local ceph-rgw-ingress.ceph.svc.cluster.local cinder-api.openstack.svc.cluster.local cinder.openstack.svc.cluster.local coaster-all.openstack.svc.cluster.local coaster.openstack.svc.cluster.local emla-apiserver.openstack.svc.cluster.local emla.openstack.svc.cluster.local glance-api.openstack.svc.cluster.local glance.openstack.svc.cluster.local gnocchi-api.openstack.svc.cluster.local gnocchi.openstack.svc.cluster.local keystone-api.openstack.svc.cluster.local keystone.openstack.svc.cluster.local neutron.openstack.svc.cluster.local neutron-server.openstack.svc.cluster.local nova-api.openstack.svc.cluster.local nova.openstack.svc.cluster.local peak-api.ems.svc.cluster.local peak.ems.svc.cluster.local placement-api.openstack.svc.cluster.local placement.openstack.svc.cluster.local

# Step 2: Install openstack client
pip install python-openstackclient

# Step 3: Set environment variables (use publicURL - APISIX routes via Host header)
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME=admin
export OS_PASSWORD='<PASSWORD>'        # default: Admin@ES20!8
export OS_AUTH_URL='http://keystone.openstack.svc.cluster.local:80/v3'
export OS_REGION_NAME=RegionOne
export OS_INTERFACE=publicURL
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Now run `openstack` commands directly: `project list`, `server list`, `volume list`, etc.

**Why publicURL:** APISIX on the jump host only exposes port 80.
Services with `internalURL`/`adminURL` on non-standard ports are not accessible.

## Local vs Busybox CLI - When to Use Each

| Scenario | Where to Run | Why |
|----------|-------------|-----|
| `project list`, `server list`, `volume list` | Local | Fast, no SSH needed |
| `server show`, `volume show`, `endpoint list` | Local | Metadata-only |
| `image create` / large file uploads | Busybox pod | Cluster-internal network faster |
| Operations requiring `adminURL` endpoints | Busybox pod | `adminURL` not routed through APISIX |
| Generate/download files then upload | Busybox pod | Download directly to cluster storage |

Example: upload image from busybox pod:
```bash
kubectl exec -it -n openstack services/busybox -- bash
# Inside busybox:
wget http://example.com/image.qcow2 -O /tmp/image.qcow2
openstack image create --file /tmp/image.qcow2 --disk-format qcow2 --container-format bare my-image
```
