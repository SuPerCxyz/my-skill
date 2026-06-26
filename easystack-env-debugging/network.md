# Network Diagnostics 网络排查

访问环境确认后, 如需检查网络问题, 阅读本文件。内容聚焦节点连通性、ARP、
VLAN 子接口以及相关只读诊断。

节点间网络连通性排查的方法论，适用于 EasyStack 环境中的多网平面场景。

## 网络平面速查

EasyStack 环境中常见的网桥及其用途:

| 网桥名称 | 典型用途 | 说明 |
|----------|---------|------|
| `br-mgmt` | 管理网 | 节点管理、OpenStack 内部 API 通信 |
| `br-pub` | 公网/外部网络 | 外网流量、虚拟机浮动 IP |
| `br-storage` | 存储后端网 | Ceph/RBD 后端存储流量 |
| `br-storagepub` | 存储公网 | 存储对外通信 |
| `br-vxlan` | VXLAN 隧道网 | Overlay 网络 |
| `br-roller` | 部署/运维网 | Ansible/Roller 部署通信 |
| `br-ipmi` | IPMI/带外网 | BMC 管理 |
| `br-ex` | 外部网络 | Provider 网络出口 |

## 节点间网络排查流程

### Step 1: 确认本机网络身份

```bash
# 查看所有 IP
hostname -I

# 查看本机名
hostname

# 确认核心网络接口和 IP
for iface in $(ip -o link show | grep -vE 'veth|tap|cali|tunl|cni' | \
  awk -F': ' '{print $2}'); do
  echo "--- $iface ---"
  ip addr show $iface 2>/dev/null | grep -w inet
done
```

### Step 2: 确认对端可达性

> ⚠️ **重要: 始终使用主机名(hostname)而非 IP 地址访问对端节点。**
> 原因: 节点有多个 IP 分布在不同的网平面(管理网、存储网、VXLAN 等)，
> `/etc/hosts` 由部署工具维护，解析到**当前可用的正确网络**。
> 如果直接使用 IP，可能无意间指定了当前有问题的网络，导致误判。

```bash
# ✅ 正确: 通过主机名访问 — 自动选择可达网络
ping -c 2 -W 2 node-3201

# 通过管理网 ping 对端 IP
ping -c 2 -W 2 <已知可达IP>
```

如果主机名能 ping 通，说明:
- DNS/hosts 解析正常
- 至少有一条网络路径可达
- 对端节点在线

### Step 3: 检查目标网络的接口状态

```bash
# 物理网卡状态
ip link show | grep -E 'enp|eth'

# VLAN 子接口/专用接口状态
ip -d link show <interface-name>
```

关注标志:
- `UP` + `LOWER_UP` = 物理链路正常
- `UP` + `NO-CARRIER` = 接口 config 了但没有线或对端不通
- `DOWN` = 接口被 admin down

### Step 4: 检查目标网络的路由

```bash
ip route show | grep <目标网段>
```

确认路由指向正确的设备。

### Step 5: 🔑 ARP 诊断（最关键）

```bash
# 查看特定 IP 的 ARP 状态
ip neigh show | grep <目标IP>

# 或者过滤特定网段
ip neigh show | grep <网段前缀>
```

**ARP 状态解读:**

| ARP 状态 | 含义 | 诊断结论 |
|----------|------|---------|
| `REACHABLE` | 最近通信成功 | ✅ L2 正常 |
| `STALE` | 曾成功但缓存过期 | ✅ 大概率 L2 正常 |
| `INCOMPLETE` | 发送了 ARP 请求但未收到响应 | ⚠️ L2 可能有问题 |
| `FAILED` | ARP 解析失败 | ❌ **L2 不通** |

**`FAILED` 意味着:**
- 物理层(L1)可能正常(接口 UP)
- 二层(L2)帧无法到达对端
- 与三层(L3)路由无关
- 与防火墙/iptables 无关(ARP 不过 IP 层)

### Step 6: Ping 验证

```bash
# Ping 目标 IP（不需要路由，直连网段）
ping -c 3 -W 2 <目标IP>
```

注意: ARP FAILED 时 ping 必然 100% loss。
如果 ARP 成功但 ping 失败，那才是三层(防火墙/iptables)的问题。

### Step 7: 对端交叉验证

从本机 SSH 到对端节点，在对方也执行同样的检查:

```bash
ssh node-<xxx> 'ip neigh show | grep <目标网段>'
ssh node-<xxx> 'ip -d link show ipsan-0'
ssh node-<xxx> 'ping -c 2 -W 2 <本机IP>'
```

确保两边现象对称（单通还是双不通）。

### Step 8: 查看 VLAN 配置（只读）

```bash
# 查看 VLAN 子接口的 VID
ip -d link show <vlan-interface>

# 查看 ifcfg 配置（只读）
cat /etc/sysconfig/network-scripts/ifcfg-<interface-name>
```

cat 命令如果被安全模块拦截禁止，说明环境有命令审计/过滤机制。

## VLAN 子接口排查

VLAN 子接口在输出中显示为 `@物理接口`，例如 `ipsan-0@enp130s0f0np0`。

检查要点:
```bash
# 确认 VLAN ID
ip -d link show ipsan-0 | grep vlan
# 应看到: vlan protocol 802.1Q id <VID> <REORDER_HDR>

# 确认 ifcfg 中的 VID 与对端一致
cat /etc/sysconfig/network-scripts/ifcfg-ipsan-0
# 关注: VID, PHYSDEV, IPADDR, PREFIX, MTU
```

两侧节点的以下参数必须**一致**:
- VLAN ID (VID)
- MTU
- 网络类型(802.1Q)
- 网段/Prefix

## 常见根因速查

| 现象 | 可能原因 |
|------|---------|
| 物理接口 `NO-CARRIER` | 网线/光模块/交换机端口故障 |
| 物理接口 `UP`，ARP `FAILED` | **交换机 VLAN 配置问题** |
| ARP `REACHABLE`，ping 100% loss | 防火墙/iptables/路由 ACL |
| 本端 ARP `FAILED`，对端 ARP `REACHABLE` | 单通(对端可见本端但反之不然) |
| 接口 `UP` 但 `ip addr` 无 IP | 接口未配 IP 或 DHCP 失败 |
| `cat ifcfg-*` 被拦截 | 环境有命令审计/安全模块 |
| VLAN 接口 `DOWN` | 父接口未 UP 或 VLAN 模块未加载 |

## 诊断命令保存

建议将诊断输出保存到文件以备后续分析:

```bash
# 一次性收集网络诊断信息
{
  echo "=== HOSTNAME ===" && hostname
  echo "=== IPs ===" && hostname -I
  echo "=== INTERFACES ===" && ip link show | grep -E '^[0-9]+:' | grep -vE 'veth|tap|cali'
  echo "=== ADDRS ===" && ip addr show | grep -E 'inet '
  echo "=== ROUTE ===" && ip route show
  echo "=== ARP ===" && ip neigh show
  echo "=== ERRORS ===" && ip -s link show | grep -E 'errors' -A1
} > /tmp/netdiag_$(hostname -s).txt
```
