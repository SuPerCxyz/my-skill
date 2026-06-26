# Cross-Domain Analysis Matrix

EasyStack OpenStack 故障经常跨越多个服务层。下表把"问题域 → 必看日志 / 强相关日志 / 兜底日志"
固化为硬规则，避免遗漏关键证据。

> **核心原则**:任何云主机生命周期 / 云盘挂载卸载 / 网络变更 / 镜像操作问题，**默认都要
> 把 `os/messages.*.log` 和 `os/openvswitch/*.log` 一起带进时间线分析**。OpenStack 控制面日志
> 只能解释"调度层做了什么决定"，真正的"发生了什么"往往落在内核 / 设备 / 网卡 / SCSI / multipath
> 层，必须靠系统日志补齐。

## 1. 云主机生命周期问题(创建 / 启动 / 重启 / 删除 / 迁移)

涉及 **compute + 块存储 + 网络 + 镜像 + 虚拟化层 + 系统层**，缺一不可。

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·主日志** | `openstack/nova/nova-compute.*.log` | 生命周期事件、init_host、hard_reboot、power_on、卷连接 |
| **必看·虚拟化** | `libvirt/libvirt.*.log` | domain define/start/destroy、agent、xml 错误 |
| **必看·虚拟化** | `libvirt/qemu.instance-<HEX>.*.log` | qemu 启动失败、设备初始化错误、BIOS/UEFI |
| **必看·系统层** | `os/messages.*.log` | 内核 OOM、softlockup、PCI/磁盘/网卡错误、kubelet / containerd 状态 |
| **必看·网络** | `os/openvswitch/ovs-vswitchd.*.log`、`ovn-controller.*.log` | 端口绑定、tap/vnet 接口、流表下发 |
| **必看·块存储** | `openstack/cinder/cinder-volume.*.log` | 卷状态变化、initialize_connection |
| **强相关** | `openstack/neutron/proton-server.*.log` | 端口创建/激活、IP 分配、安全组 |
| **强相关** | `openstack/glance/glance-api.*.log` | 镜像下载 / 拷贝失败 |
| **强相关** | `openstack/nova/nova-conductor.*.log` | DB 操作 / scheduler 决策回放 |
| **强相关** | `openstack/nova/nova-scheduler.*.log` | 选主机失败、过滤器拒绝 |
| **强相关·iSCSI 卷** | `alcubierre/alcubierre-node.*.log` | iSCSI 登录 / 多路径状态 |
| **强相关·Ceph 卷** | `ceph/host.ceph-osd.*.log` + `ceph/host.ceph.*.log` | RBD I/O 慢 / OSD down |
| **兜底·基础设施** | `openstack/mariadb/mariadb.*.log`、`openstack/rabbitmq/rabbitmq.*.log` | Galera 不可用 / AMQP 断连导致 RPC 失败 |
| **兜底·K8s** | `kubernetes/kube-apiserver.*.log` | pod 状态变化(nova-compute pod 是否被驱逐) |

### 云主机生命周期典型陷阱

- 只看 `nova-compute.*.log` 会漏掉**虚拟机网卡 vnet 没成功创建** —— 必须看 `ovs-vswitchd` 是否 add port 成功。
- 只看 OpenStack 日志会漏掉**节点 OOM 杀死 qemu 进程** —— 必须看 `os/messages.*.log` 的 oom-kill 段。
- 实例迁移失败可能源于**两端 libvirt 版本/能力不一致**或**TLS 失败**，必须看两个节点的 `libvirt.*.log`。

---

## 2. 云盘挂载 / 卸载问题

涉及 **nova + cinder + 后端驱动(iSCSI/RBD/SAN)+ 内核 SCSI/multipath**。

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·主日志** | `openstack/nova/nova-compute.*.log` | `_connect_volume`、`_disconnect_volume`、target_iqns / target_portals |
| **必看·主日志** | `openstack/cinder/cinder-volume.*.log` | `initialize_connection`、`terminate_connection`、attachment 状态 |
| **必看·系统层** | `os/messages.*.log` | **SCSI / multipath / dm-X / iscsi session / 块设备 I/O 错误** |
| **必看·虚拟化** | `libvirt/libvirt.*.log` | `attach-device` / `detach-device` xml、设备热插拔失败 |
| **必看·iSCSI** | `alcubierre/alcubierre-node.*.log` | iSCSI 登录 / WWID / 多路径成员 |
| **强相关·后端** | `openstack/cinder/cinder-api.*.log`、`cinder-scheduler.*.log` | API 拒绝、调度失败 |
| **强相关·RBD** | `ceph/host.ceph-osd.*.log`、`kubernetes/csi-rbdplugin.*.log` | RBD I/O 异常、CSI 挂载 |
| **强相关·etcd 锁** | `libvirt/etcdlock-manager.*.log`、`libvirt/etcd-client.*.log` | 共享卷 PR-key 锁冲突 |
| **兜底·DB** | `openstack/mariadb/mariadb.*.log` | BDM 表读写失败 |

### 云盘挂载/卸载典型陷阱

- 卷卸载后"幽灵设备":cinder 已 detach 成功，但内核多路径还残留 `dm-X` —— 必须看
  `os/messages.*.log` 中的 `multipath` 行和 `iscsi: session.*recovery`。
- 卷挂载到错的 LUN:看 `nova-compute` 的 `Connecting to multipath volume`，对比
  `target_iqns` 和 `target_portals` 是否指向了已下线的节点。
- 共享卷(多挂载点)异常:`etcdlock-manager.*.log` 会显示锁竞争失败。
- BDM 与 cinder attachment 不一致:经典 `VolumeDeviceNotFound`，见
  [troubleshooting.md](troubleshooting.md) Scenario 1。

---

## 3. 网络问题(云主机不通 / 安全组 / 浮动 IP / 路由)

涉及 **neutron + OVN/OVS + 系统网卡层**。

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·主日志** | `openstack/neutron/proton-server.*.log` | port / router / floating IP / SG 操作 |
| **必看·数据面** | `os/openvswitch/ovn-controller.*.log` | chassis 状态、流表同步 |
| **必看·数据面** | `os/openvswitch/ovs-vswitchd.*.log` | 端口 add/del、bridge 状态、流表错误 |
| **必看·系统层** | `os/messages.*.log` | NIC 链路 up/down、bonding 状态、carrier、IRQ |
| **必看·OVN DB** | `os/openvswitch/ovn-ovsdb-{nb,sb}.*.log` | NB/SB DB 选主、Raft 集群异常 |
| **强相关·元数据** | `openstack/neutron/proton-ovn-metadata-agent.*.log` | VM cloud-init / 元数据访问失败 |
| **强相关·L2GW** | `openstack/neutron/proton-ovn-l2gw-agent.*.log` | L2 网关接入 |
| **强相关·API 网关** | `cloud-products/apisix/apisix.*.log` | 公网入口 / 反向代理失败 |
| **强相关·DNS** | `kubernetes/coredns.*.log` | 服务发现 / VM 内部 DNS |
| **兜底·VIP** | `openstack/keepalived/keepalived.*.log` | 控制面 VIP 漂移导致 API 间歇不通 |

### 网络问题典型陷阱

- VM ping 不通但 `proton-server` 显示 port `ACTIVE`:必看 `ovs-vswitchd` 是否实际 add 了 vnet，
  以及 `ovn-controller` 是否下发了流表。
- 浮动 IP 挂上但访问不通:先看 `ovn-northd` 和 `nb` DB 是否有对应 NAT 规则，再看
  网关节点的 `ovn-controller`。
- VM 内 cloud-init 失败:往往是 `metadata-agent` 不可达，或 metadata 169.254.169.254 路由问题。

---

## 4. 镜像问题(创建/上传/下载/启动失败)

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·主日志** | `openstack/glance/glance-api.*.log` | 上传、下载、转换、checksum |
| **必看·后端** | `ceph/host.ceph.*.log`、`ceph/host.ceph-osd.*.log` | RBD 池写入失败、配额 |
| **强相关·消费方** | `openstack/nova/nova-compute.*.log` | `_create_image` / `_get_image` 流程、镜像缓存目录 |
| **强相关·消费方** | `openstack/cinder/cinder-volume.*.log` | 从镜像创建卷 / image cache |
| **强相关·系统层** | `os/messages.*.log` | `/var/lib/nova/instances` 所在盘 I/O 错误 / 容量满 |
| **兜底·权限** | `openstack/keystone/keystone-api.*.log` | 镜像 ACL / project 权限 |

---

## 5. 裸金属 / Ironic(cloud-products 域)

> **重要**:EasyStack 的 ironic / 裸金属管理 / 部分云产品类服务日志归在 **`cloud-products/`** 下，
> 而不是 `openstack/`。如果集群启用了裸金属，目录里应该出现 `cloud-products/ironic/` 等子目录;
> 当前样本 bundle 只看到 `apisix/` 和 `iam/`，说明该环境未启用裸金属。

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·主日志** | `cloud-products/ironic/ironic-api.*.log`、`ironic-conductor.*.log` | 节点注册、部署状态、power_state |
| **必看·驱动** | `cloud-products/ironic/ironic-inspector.*.log` | 硬件探测 / introspection |
| **必看·镜像** | `openstack/glance/glance-api.*.log` | 部署镜像下载 |
| **必看·网络** | `openstack/neutron/proton-server.*.log`、`os/openvswitch/*.log` | 部署/清理网络切换、PXE 网络 |
| **必看·DHCP/TFTP** | `cloud-products/ironic/*dnsmasq*.log`、`*tftp*.log` | PXE 启动失败 |
| **必看·系统层** | `os/messages.*.log` | IPMI / BMC 通信、网卡链路 |
| **强相关·身份** | `cloud-products/iam/*.log`、`openstack/keystone/keystone-api.*.log` | API 鉴权 |

### 裸金属/Ironic 典型陷阱

- 节点 `provisioning → wait call-back` 卡住:通常是 PXE 网络问题，必须看
  `ovs-vswitchd` / `ovn-controller` 是否把端口切到了 provisioning 网。
- `power_on` 失败:先看 ironic-conductor 的 IPMI 错误，再到 `os/messages.*.log` 看
  BMC 网卡链路或 IPMI 超时。

---

## 6. API 网关 / 身份认证(cloud-products 域)

| 优先级 | 日志路径 | 看什么 |
|--------|---------|--------|
| **必看·入口网关** | `cloud-products/apisix/apisix.*.log` | 路由、限流、上游 5xx |
| **必看·身份服务** | `cloud-products/iam/iam-dashboard.*.log`、`cloud-products/iam/init.*.log` | EasyStack IAM 自身错误 |
| **必看·OpenStack 身份** | `openstack/keystone/keystone-api.*.log` | token、policy、project 角色 |
| **强相关·缓存** | `openstack/memcached/*.log` | token 缓存命中失败 |
| **强相关·K8s 鉴权** | `kubernetes/k8s-keystone-auth.*.log` | K8s API 用 keystone 做鉴权失败 |

---

## 跨域查证最小动作清单

接到任何"云主机/云盘/网络/镜像"类工单，先用 30 秒按下面这个清单扫一遍，再做深入分析:

```bash
# 1) 系统层先排雷(OOM / panic / 链路抖动 / 块设备错误)
grep -iE "panic|softlockup|hung_task|Out of memory|killed process|i/o error|link is (up|down)|iscsi.*recovery|multipath" \
  ecs.*/os/messages.*.log | sort -k1,2 | head -50

# 2) 基础设施(Galera / RabbitMQ / chrony / Ceph health)
grep -iE "WSREP|primary component|non-primary|netsplit|partition|HEALTH_(WARN|ERR)|cannot find.*source" \
  ecs.*/openstack/mariadb/*.log \
  ecs.*/openstack/rabbitmq/*.log \
  ecs.*/os/chrony.*.log \
  ecs.*/ceph/host.ceph.*.log 2>/dev/null | sort -k1,2 | head -30

# 3) 运维动作(看最近有没有人改过什么)
grep -E "systemctl|kubectl|reboot|shutdown|drain|reset|delete|stop" \
  ecs.*/openstack/dozer/bash-history.*.log | sort -k1,2 | tail -30
```

这三步任何一步发现强信号，都需要把它放到时间线最前面作为根因候选。
