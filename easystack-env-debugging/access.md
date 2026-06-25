# Environment Access

## SSH 到 K8s 控制节点

### 跳板机模式(IP 以 172.18. 开头)

```bash
# 一步执行远端命令
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>' "<kubectl-command>"

# 交互式会话
sshpass -p "easystack" ssh -tt -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>'
```

- `<JUMP_IP>` 由用户指定(如 `172.18.0.133`、`172.18.0.242`)
- `<CONTROL_NODE_IP>` 通常为 **10.20.0.3**，失败时询问用户
- 跳板机本身没有 kubectl，必须内层 SSH 到控制节点

### 直连模式(非 172.18. 开头)

```bash
# 直接 SSH 到 K8s 控制节点
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<TARGET_IP>
```

- 如果密码错误，先试 `easystack`，再问用户

### 进入控制节点后

> ⚠️ **始终使用主机名而非 IP 地址访问其他节点。**
> 节点有多个 IP 分布在管理网、存储网、VXLAN 等多个网平面。
> `/etc/hosts` 由部署工具维护，解析到**当前可用的正确网络路径**。
> 直接使用 IP 可能会指定到有问题的网络，导致误判或 SSH 不通。

```bash
# ✅ 正确: 通过主机名访问(节点间已配免密)
ssh node-3 'multipath -ll'

# ❌ 不要直接用 IP
ssh 32.168.40.2 'command'  # 可能选了存储网而非管理网

# 执行 kubectl 命令
kubectl get pods -n openstack | grep cinder
```

## 注意事项(两种模式通用)

- **复杂命令避免嵌套 SSH 引号传递** — 无论是跳板机双层 SSH 还是直连后跳 node，引号和变量展开都容易丢失。优先进入交互式会话再执行
- 必须加 `-F /dev/null` 避免本机 ssh_config 干扰
- **不要从本机直连 K8s 节点内网 IP**(如 10.10.1.x)，必须通过控制节点中转
- `easystack` 密码可能因环境不同，未知时询问用户

## 复杂命令:可靠传递模式

SSH 执行复杂 shell 逻辑时，引号、`$@`、`$$`、变量展开和转义最容易丢失。
如果命令里包含多行逻辑、循环、条件分支或需要精确保留参数，**唯一可靠的传递方式**是:

1. 先把复杂逻辑写成 Python 脚本
2. 在本机将脚本 `base64` 编码
3. 通过 SSH 管道把编码内容发送到远端
4. 远端解码后执行

示例(跳板机模式):

```bash
python3 <<'PY' | base64 -w0 | sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP> "base64 -d | python3"'
from pathlib import Path

print("hello from remote script")
PY
```

直连模式更简单:

```bash
python3 <<'PY' | base64 -w0 | ssh -o StrictHostKeyChecking=no root@<TARGET_IP> "base64 -d | python3"
print("hello from remote")
PY
```

## JumpServer 堡垒机模式

部分环境通过 JumpServer 堡垒机管理，而非直接 SSH 到 K8s 控制节点。

### 连接流程

```
ssh js                    → 进入 JumpServer 控制台
输入目标资产名(如 BJ-32)  → JumpServer 代理 SSH 到目标主机
sudo su -                 → 切换到 root
```

### JumpServer 配置

- **Host**: `js.easystack.io:2222`
- **SSH 别名配置**: 在 `~/.ssh/config` 中通常配为:

```
Host js
    HostName js.easystack.io
    Port 2222
    User <your-email>
```

### 交互式使用(expect 脚本)

JumpServer 是交互式 TUI 菜单，无法通过管道直接输入。使用 expect 脚本完成自动登录:

```bash
#!/usr/bin/expect -f
set timeout 30

# 连接 JumpServer
spawn ssh -tt js

# 等待菜单提示符
expect "Opt>"

# 发送目标资产名(替换 ASSET_NAME 为实际名称)
send "ASSET_NAME\r"

# 等待目标主机的 shell 提示符
expect {
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    -re {[$#>]} {
        send_user "已连接到目标主机\n"
    }
    timeout {
        send_user "连接超时\n"
        exit 1
    }
}

# 切换到 root
send "sudo su -\r"
expect {
    -re {[$#>]} {
        send_user "✅ 已切换到 root\n"
    }
    "not in the sudoers" {
        send_user "❌ 没有 sudo 权限\n"
        exit 1
    }
    timeout {
        send_user "⚠️ 切换超时,可能需要密码\n"
        exit 1
    }
}

# 进入交互模式
send "cd ~\r"
interact
```

### 常见资产名

| 名称 | 说明 |
|------|------|
| `BJ-32` (node-3202, 172.32.0.2) | 北京 32 号环境 |
| *(其他资产由用户指定)* | |

### 资产内特征

| 属性 | 说明 |
|------|------|
| 登录用户 | `dev` (JumpServer 系统用户) |
| sudo 权限 | ✅ NOPASSWD，可免密 `sudo su -` |
| root 验证 | `uid=0(root) gid=0(root)` |
| 额外组 | `pamauth` (1000) |
| JumpServer 复用 | 资产支持复用 SSH 连接 |

### 连接验证

进入目标主机并切到 root 后，按已有流程执行 kubectl 验证:

```bash
whoami       # 应返回 root
id           # uid=0(root)
kubectl get namespaces | grep openstack
```

### 节点间跳转(从 JumpServer 资产的当前节点到另一节点)

```bash
# ✅ 正确: 使用主机名 SSH 到其他节点(节点间已配免密)
ssh node-3201

# ⚠️ 注意: 不要直接用 IP。节点有多个网平面 IP，
# 用 IP 可能选到当前的故障网络，导致 SSH 不通或绕路
# ❌ ssh 10.254.32.1  # ipsan 网段，可能不通
```

### 注意事项

- JumpServer TUI 菜单支持: 输入资产名(唯一时自动登录)、`/ + IP/名称` 搜索、`p` 列出有权限的主机
- 如果 `sudo su -` 需要密码，说明不是 NOPASSWD 配置，需询问用户密码
- 这种方式与 jump host 模式、直连模式并列，是第三种环境访问路径

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
