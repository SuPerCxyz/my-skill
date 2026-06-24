# Troubleshooting Scenarios

## Scenario 1: VM Hard Reboot Fails — Volume Device Not Found

### Symptom
After a compute node restart, VM hard reboot fails with:
```
Volume device not found at .
os_brick.exception.VolumeDeviceNotFound: Volume device not found at .
```

### Diagnosis Flow

**Step 1 — Check nova-compute for the error:**
```bash
grep "Failed to resume instance\|VolumeDeviceNotFound" openstack/nova/nova-compute.*.log
```

**Step 2 — Identify the timeline:**
```bash
# Find the reconnect attempt
grep "Rebooting instance after nova-compute restart\|Connecting to multipath volume" openstack/nova/nova-compute.*.log
```

**Step 3 — Check what target portals the BDM has stored:**
```bash
grep "Connecting to multipath volume\|Disconnect multipath volume" openstack/nova/nova-compute.*.log | grep -oP "target_iqns.*?\]"
```

Look for the target IQN naming pattern `tgt1.node-<N>`. If all portals point to the same node that restarted, the issue is that the BDM `connection_info` is stale and only contains one node's portals.

**Step 4 — Check actual iSCSI session state:**
```bash
grep "iscsi session list\|iscsiadm.*session" openstack/nova/nova-compute.*.log
```

This shows which target nodes still have active iSCSI sessions. If sessions exist on other nodes but the BDM doesn't know about them, it confirms a stale `connection_info`.

**Step 5 — Check WWID fallback behavior:**
```bash
grep "_find_dm_device\|wwid.*fallback\|get_volume_paths" openstack/nova/nova-compute.*.log
```

If `wwid fallback also failed`, the multipath device (`/dev/dm-X`) was already removed during the restart.

### Root Cause Pattern

The `block_device_mapping` table in nova's database stores `connection_info` that was retrieved from cinder's `initialize_connection` at volume attach time (`nova/virt/block_device.py:713`). If cinder's target topology changes (e.g., after node additions/removals), nova's BDM **is not automatically refreshed**.

To verify:
1. In the DB: compare `cinder.volume_attachment.connection_info` vs `nova.block_device_mapping.connection_info` for the same volume
2. Look for differences in `target_iqns` and `target_portals`

### Resolution

1. Refresh the BDM `connection_info` from cinder's latest `volume_attachment`
2. In the code: `nova/virt/block_device.py:684` `refresh_connection_info()` fetches latest from cinder via `volume_api.attachment_get()` or `volume_api.initialize_connection()`
3. Then retry the hard reboot

### 实战诊断技巧（关键经验沉淀）

以下信号配合出现 = 几乎可以断定 BDM 陈旧 / connection_info 塌缩：

1. **`target_iqns` 4 项全相同**：典型多路径应该列出多节点 IQN（如 `tgt1.node-1`、`tgt1.node-2` …），如果 4 项全是 `tgt1.node-X` 同一节点，说明 portal 列表已塌缩成单节点。这是最强信号。

   ```bash
   # 抽取每个卷的 target_iqns，看是否塌缩
   grep "Connecting to multipath volume" openstack/nova/nova-compute.*.log \
     | grep -oE "'target_iqns': \[[^]]+\]" | sort | uniq -c | sort -rn
   ```

2. **`_find_dm_device: wwid fallback also failed`**：multipath 扫了所有 dm-X 都找不到这个 wwid，是 `VolumeDeviceNotFound` 的最直接前置告警。

3. **后端 target 日志中"没有"这卷的 mapping**：去对应 `alcubierre-target.<node>.log` 里搜该 wwid / `volume-<id>` / LUN 号，**找不到 `Applying volume mapping` 或 `Mapped lun` 记录**比 nova 侧的 `VolumeDeviceNotFound` 更上游 —— 证明远端 target 根本没在承载这卷。

   ```bash
   # 用 wwid 反查后端 target 是否真的服务这卷
   for d in ecs.*/; do
     n=$(basename "$d" | cut -d. -f2)
     hit=$(grep -l "<WWID_NO_PREFIX_3>" "$d/alcubierre/alcubierre-target.node-"*.log 2>/dev/null | wc -l)
     [ "$hit" -gt 0 ] && echo "$n serves this wwid"
   done
   ```

4. **同节点对照组**：在 nova-compute 重启后，**同时**看节点上其它 VM 是否成功 resume。

   - 全部失败 → 节点级问题（基础设施 / Galera / RabbitMQ / OS）
   - 只这一台失败、其它成功 → **VM 个体 + 卷个体的 BDM/拓扑问题**（本场景）
   - 失败 VM 都有 iSCSI 卷、成功的都是本地盘/RBD → 进一步聚焦在 iSCSI 后端

   ```bash
   # 一行抓出节点上所有 resume 结果
   grep -E "Instance rebooted successfully|Failed to resume instance" \
     openstack/nova/nova-compute.*.log \
     | awk -F' ¦ ' '{print $1, "|", $5}' | grep -oE "instance: [^]]+|rebooted|Failed to resume"
   ```

5. **重试节奏 = 10/10/10/30/65/130/255/~512s 的退避**：典型 4 分钟超时（约 1024s 累计）；如果看到这个节奏然后 `VolumeDeviceNotFound`，就是 `_connect_volume` 等多路径超时退出，**不是网络瞬时抖动**。

6. **服务启动时序对齐**：`alcubierre-target` / `alcubierre-node` 启动时间要早于 nova-compute 触发 `Rebooting instance after nova-compute restart` 的时间。如果 nova 已经开始 reconnect 但 target 还没 ready，前几次失败是预期，但**重试到 4 分钟还失败就不是时序问题了**。

   ```bash
   # 服务时序快速对照
   for d in ecs.*/; do
     n=$(basename "$d" | cut -d. -f2)
     echo "--- $n ---"
     grep "Starting alcubierre" "$d/alcubierre/alcubierre-target.node-"*.log 2>/dev/null | head -1 | awk -F' ¦ ' '{print "target start:", $1}'
     grep "Rebooting instance after nova-compute restart" "$d/openstack/nova/nova-compute.node-"*.log 2>/dev/null | head -1 | awk -F' ¦ ' '{print "nova reboot:", $1}'
   done
   ```

---

## Scenario 2: Node Reboot / Crash

### Symptom
Compute node becomes unavailable, instances are in error state or need evacuation.

### Diagnosis Flow

**Step 1 — Check OS messages for cause of restart:**
```bash
grep -i "reboot\|shutdown\|panic\|watchdog\|hung_task\|softlockup" os/messages.*.log
```

**Step 2 — Check nova-compute init sequence:**
```bash
grep -i "init_host\|resume_state_on_host_boot\|_resume_guests_state\|Rebooting instance after" openstack/nova/nova-compute.*.log
```

This shows: which instances nova tried to recover, and which failed.

**Step 3 — Check Kubernetes node status:**
```bash
grep -i "node.*not ready\|node.*ready\|NotReady" kubernetes/kube-controller-manager.*.log
```

**Step 4 — Check libvirt state:**
```bash
grep -i "domain\|destroy\|start\|state" libvirt/libvirt.*.log
```

---

## Scenario 3: iSCSI Connection Failure

### Symptom
Volume attachment fails, `VolumeDeviceNotFound` or iSCSI login failures.

### Diagnosis Flow

**Step 1 — Check the target portals in nova-compute:**
```bash
grep "Connecting to multipath volume\|Trying to connect to iSCSI portal" openstack/nova/nova-compute.*.log
```

**Step 2 — Check Alcubierre node agent:**
```bash
grep -i "connect_volume\|disconnect_volume\|login\|logout\|error\|fail" alcubierre/alcubierre-node.*.log
```

**Step 3 — Check active iSCSI sessions:**
```bash
grep "iscsi session list" openstack/nova/nova-compute.*.log
```

Count which target nodes have active sessions.

**Step 4 — Check cinder volume backend:**
```bash
grep "initialize_connection\|terminate_connection" openstack/cinder/cinder-volume.*.log
```

Check which backend driver (RBDDriver, AlcubierreDriver, etc.) is handling the volume.

---

## Scenario 4: Database Connectivity Issues

### Symptom
Services report `WSREP has not yet prepared node for application use` or `DBConnectionError`.

### Diagnosis Flow

**Step 1 — Check nova and cinder logs for DB errors:**
```bash
grep "WSREP\|DBConnectionError\|pymysql.err.OperationalError" openstack/nova/nova-compute.*.log openstack/cinder/cinder-volume.*.log
```

**Step 2 — Check mariadb logs:**
```bash
grep -i "WSREP\|galera\|cluster\|sync\|donor\|joiner" openstack/mariadb/mariadb.*.log
```

---

## Scenario 5: Volume Attachment/Detachment Failure

### Symptom
Volume attach fails or volume disappears from VM.

### Diagnosis Flow

**Step 1 — Check nova-compute volume operations:**
```bash
grep -i "attach_volume\|detach_volume\|_connect_volume\|_disconnect_volume" openstack/nova/nova-compute.*.log
```

**Step 2 — Check connect/disconnect detailed info:**
```bash
grep "Connecting to multipath volume\|Disconnect multipath volume" openstack/nova/nova-compute.*.log
```

Look at `target_iqns`, `target_portals`, `target_luns`, `wwid`, `device_path`.

**Step 3 — Check cinder volume operations:**
```bash
grep "initialize_connection\|terminate_connection\|attachment" openstack/cinder/cinder-volume.*.log
```

**Step 4 — Check Alcubierre if iSCSI type:**
```bash
grep -i "volume_id.*<VOLUME_ID>\|connect_volume\|disconnect_volume" alcubierre/alcubierre-node.*.log
```

---

## Scenario 6: VM Reboot After Host Reboot

This is a special case of Scenario 1. When a compute node restarts, nova-compute's `init_host` triggers `_resume_guests_state` which calls `_hard_reboot` on each instance that was running.

### Key Log Sequence

```bash
# 1. Nova-compute starts
grep "init_host\|Starting compute node" openstack/nova/nova-compute.*.log

# 2. Instance detected as running before restart
grep "expect_running\|_resume_guests_state\|Rebooting instance after" openstack/nova/nova-compute.*.log

# 3. Hard reboot: destroy phase
grep "Instance destroyed successfully\|destroy" openstack/nova/nova-compute.*.log

# 4. Hard reboot: reconnect volumes  
grep "Connecting to multipath volume\|Disconnect multipath volume" openstack/nova/nova-compute.*.log

# 5. Hard reboot: start instance
grep "Instance rebooted successfully\|Failed to resume instance" openstack/nova/nova-compute.*.log
```

### Why One Instance Fails and Others Succeed

If some instances resume successfully while others fail, compare:
- **Volume type**: iSCSI vs Ceph RBD volumes have different reconnection behavior
- **Target node**: volumes with targets on the rebooted node vs other nodes
- **Connection_info freshness**: BDM may have stale data for some volumes

---

## Scenario 7: 实战 case — VM 启动失败排查的高确定性路径

**用户问题**："分析云主机 `<UUID>` 在某天的启动异常"。

这是日常最高频的请求形态。下面是 5 分钟内能给出高置信度结论的标准流程，**每步都写明"看什么"和"找到什么意味着什么"**。

### Step 1：定位节点 + req-ID

```bash
VM=<UUID>
# 节点定位
for d in ecs.*/; do
  c=$(grep -l "$VM" "$d/openstack/nova/nova-compute."*.log 2>/dev/null | wc -l)
  [ "$c" -gt 0 ] && echo "$(basename $d): $c"
done
# 抽出主 req（多数情况下整个生命周期事件共用一个 req）
grep "$VM" ecs.<node>/openstack/nova/nova-compute.*.log | grep -oE "req-[0-9a-f-]+" | sort | uniq -c | sort -rn | head -3
```

> 找到的 req 是后续跨服务关联的钥匙。

### Step 2：抽 VM 的事件主线（结论性事件）

只看"结论性"事件，不要被几千行 INFO 淹没：

```bash
grep "$VM" ecs.<node>/openstack/nova/nova-compute.*.log \
  | grep -E "Rebooting instance|Instance destroyed|Instance rebooted successfully|Failed to resume|VolumeDeviceNotFound|Setting instance vm_state to ERROR|During.*sync.*power_state|VM (Started|Resumed|Stopped) \(Lifecycle Event\)" \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,250)}'
```

读得出"开始 → 销毁 → 重连卷 → 成功/失败 → ERROR"的就是主线。

### Step 3：如果是"卷连接"失败，**必看 4 个东西**

```bash
# (a) BDM 给的 target 列表 + wwid
grep "$VM\|Connecting to multipath volume" ecs.<node>/openstack/nova/nova-compute.*.log \
  | grep "Connecting to multipath volume" | head -3 \
  | awk -F' ¦ ' '{print substr($5,1,500)}'

# (b) 当时 iscsi 实际 session 落在哪
grep "iscsi session list" ecs.<node>/openstack/nova/nova-compute.*.log | tail -3 \
  | awk -F' ¦ ' '{print $1, "|", substr($5,1,300)}'

# (c) 重试次数 + 间隔（判断是否 4 分钟超时模式）
grep -c "Connecting to multipath volume.*<VOLUME_ID>" ecs.<node>/openstack/nova/nova-compute.*.log

# (d) 远端 target 是否真在服务这卷（最上游证据）
WWID=<wwid_no_prefix3>
for d in ecs.*/; do
  n=$(basename "$d" | cut -d. -f2)
  hit=$(grep -l "$WWID" "$d/alcubierre/alcubierre-target.node-"*.log 2>/dev/null | wc -l)
  echo "$n: $hit alcubierre-target files mention this wwid"
done
```

### Step 4：同节点对照组（强诊断手段）

同时间窗内同节点上的**其它 VM** 是否成功：

```bash
grep -E "Instance rebooted successfully|Failed to resume instance" \
  ecs.<node>/openstack/nova/nova-compute.*.log \
  | awk -F' ¦ ' '{raw=$5; sub(/^[^F]*F /, "", raw); print $1, "|", substr(raw,1,200)}' \
  | head -20
```

- 全部失败 → 节点级 / 基础设施问题（去 Step 5）
- 只这一台失败 → VM 个体问题（卷 / BDM / 镜像），直接出报告

### Step 5：上游基础设施脉冲检查（30 秒）

在聚焦 VM 之前，先确认基础设施层是否健康。基础设施异常往往是 VM 问题的上游根因。

```bash
# (a) OS 层：内核错误、OOM、磁盘 I/O、网络链路
grep -iE "panic|softlockup|Out of memory|i/o error|link is (up|down)|iscsi.*recovery|iscsid.*connect to.*failed \(Connection refused\)|multipath" \
  ecs.<node>/os/messages.*.log | head -20

# (b) 控制面基础设施：Galera 集群、RabbitMQ 分区、chrony 时钟漂移
grep -iE "WSREP|non-primary|partition|HEALTH_(WARN|ERR)" \
  ecs.<node>/openstack/mariadb/*.log ecs.<node>/openstack/rabbitmq/*.log \
  ecs.<node>/os/chrony.*.log 2>/dev/null | head -20

# (c) Ceph 集群健康
grep -E "HEALTH_(WARN|ERR)" ecs.<node>/ceph/host.ceph.*.log 2>/dev/null | tail -5

# (d) Ceph CSI driver 是否注册（影响 RBD PVC 挂载）
grep -iE "rbd.csi.ceph.com not found in the list of registered CSI drivers" \
  ecs.<node>/os/messages.*.log | head -5

# (e) 操作审计：近期人工操作
grep -E "systemctl|reboot|shutdown|drain|reset|kubectl delete" \
  ecs.<node>/openstack/dozer/bash-history.*.log | tail -20
```

**任何一行强信号都要纳入根因候选。** 如果基础设施层（Galera/RabbitMQ/Ceph/CSI）有异常，VM 问题往往是表象而非根因。

**快速判断分支：**
- 基础设施无异常，仅个别 VM 失败 → 聚焦 VM 个体（卷 / BDM / 镜像）
- 基础设施有异常 + 多个服务同时报错 → 先解基础设施问题，再回看 VM
- 仅 iSCSI target `Connection refused` → 检查 Alcubierre 节点状态和启动时序

### Step 6：节点重启时间 + 服务可用时间对齐

> `os/boot.*.log` 比 `os/messages.*.log` 更准确。boot.log 记录 systemd 启动序列，
> 可以精确看到 iscsid/containerd/kubelet 各在什么时间点 ready。

```bash
# 节点真实启动时间（kernel 起来）
zgrep -h "Linux version\|Command line: BOOT_IMAGE" ecs.<node>/os/messages.*.log* | head -3 \
  | awk -F' ¦ ' '{print $1, "|", substr($5,1,150)}'

# systemd boot complete（更准确）
grep -E "Reached target.*Multi-User\|Reached target.*Graphical" \
  ecs.<node>/os/boot.*.log | tail -1 | awk -F' ¦ ' '{print $1}'

# 各 OpenStack/存储/网络服务可用时间
for svc in nova-compute cinder-volume alcubierre-target alcubierre-node libvirt kubelet containerd iscsid; do
  f=$(ls ecs.<node>/**/$svc.node-*.log 2>/dev/null | head -1)
  [ -z "$f" ] && continue
  ts=$(grep -iE "Starting|started" "$f" | head -1 | awk -F' ¦ ' '{print $1}')
  [ -n "$ts" ] && echo "$svc ready: $ts"
done
```

如果 nova-compute 重连卷时**后端 target 还没启动 10 秒**，前几次失败是正常的；只要总重试窗口（默认 ~4 分钟）内拿到设备就算成功。

### Step 7：写报告（用 [analysis-playbook.md](analysis-playbook.md) 模板）

务必包含：
- **结论 1 句话** + 关键失败行 file:line
- **时间线表**：节点 boot → 服务 ready → VM 事件 → 失败时刻
- **同节点对照组**结果（成功 vs 失败的 VM 各几台、差异点是什么）
- **未验证项**：哪些证据是间接的（例如"日志窗口内没有 cinder 操作"≠"cinder 从来没操作过这卷"）

### 这类问题的高频根因 TOP 5

| # | 根因 | 关键证据 |
|---|------|---------|
| 1 | **BDM connection_info 陈旧/塌缩**（本案例） | `target_iqns` 4 项全相同；远端 target 无 mapping；wwid fallback 失败 |
| 2 | **节点重启后 alcubierre/cinder 后端未就绪** | nova reconnect 时 target 日志显示服务尚未 Starting |
| 3 | **iSCSI 网络瞬断** | os/messages 中 `iscsi: session.*recovery`、`link is down`；只此一次重试就成功 |
| 4 | **RBD 卷在 Ceph 健康异常** | ceph HEALTH_ERR/PG down，nova-compute 卡在 `librbd` 调用 |
| 5 | **libvirt/qemu 启动失败**（非卷问题） | qemu.instance-<HEX>.log 末尾出现 `qemu-kvm:` 错误；nova 看到 domain define 成功但 start 失败 |
