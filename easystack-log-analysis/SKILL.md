---
name: easystack-log-analysis
description: "Use when needing to decompress, analyze, and troubleshoot EasyStack OpenStack cluster logs from eslog files. Covers decompression of encrypted eslog archives, log directory structure mapping, key log file locations per service, and common troubleshooting search patterns. Handles cross-domain analysis (VM lifecycle / volume attach-detach / network / image / bare-metal Ironic) — always correlates OpenStack service logs with OS-level logs (kernel, OVS/OVN, SCSI/multipath, IPMI) and control-plane infra (Galera, RabbitMQ, chrony, Ceph health) for true root cause. EasyStack cloud-product services (Ironic, APISIX, IAM, etc.) live under cloud-products/ rather than openstack/."
---

# EasyStack Log Analysis

## Overview

EasyStack diagnostic logs are distributed as password-protected `.eslog` files. After decompression, a `ecs.<host>.<date>.[N]/` directory tree is produced containing containerized service logs from Kubernetes pods organized by functional area.

This skill guides the decompression, directory mapping, and targeted log analysis for troubleshooting common OpenStack-on-K8s failure scenarios.

## Quick Reference

| When you need... | Read |
|------------------|------|
| **Standard end-to-end analysis workflow + report template** | [analysis-playbook.md](analysis-playbook.md) |
| **跨域关联分析矩阵（云主机/云盘/网络/镜像/裸金属 必看哪些日志）** | [cross-domain-analysis.md](cross-domain-analysis.md) |
| Decompress eslog files | [decompress.md](decompress.md) |
| Log line format (wrapper / fields / awk recipes) | [log-format.md](log-format.md) |
| Log directory structure map | [directory-map.md](directory-map.md) |
| Search patterns by issue type | [search-patterns.md](search-patterns.md) |
| Troubleshooting scenarios | [troubleshooting.md](troubleshooting.md) |

## Workflow

### Step 1: Decompress

Run decompression script (one-shot for all `.eslog` files in current dir):

```bash
# Decompress all .eslog files in current directory
./decompress_eslog.sh
```

Output: `ecs.<host>.<date>.[N]/` directory (or multiple, one per host).

> **Time window hint**: the eslog filename itself encodes the collection range:
> `ecs.20260618-20260623183823.eslog` = 2026-06-18 00:00 → 2026-06-23 18:38:23.
> Read this first to know what time window the bundle can answer for, and to
> narrow searches before you grep.

> **Log line format**: every log line has a 5-field wrapper
> `<ts> +0800 ¦ <node> ¦ <pod> ¦ <container> ¦ <raw>`. Plain content `grep`
> works as-is; see [log-format.md](log-format.md) for awk recipes when you
> need per-pod / per-container aggregation.

### Step 2: Understand directory layout

The top-level directories map to service layers:

| Directory | Contents |
|-----------|----------|
| `openstack/` | Core OpenStack services: nova, cinder, neutron, glance, keystone, etc. |
| `libvirt/` | Hypervisor: libvirtd, qemu instances, sync, ceph placement |
| `alcubierre/` | Alcubierre iSCSI storage node agent, target init, exporter |
| `ceph/` | Ceph monitor, manager, OSD, RGW logs |
| `ceph-k8s/` | Ceph OSD disk prepare, isolation |
| `kubernetes/` | K8s system: kube-apiserver, scheduler, controller-manager, coredns, flannel |
| `os/` | OS messages, chrony, openvswitch |
| `cloud-products/` | API gateway (apisix), IAM |
| `ecms/` | Monitoring: prometheus, grafana, alertmanager, fluentd |
| `ecas/` | Automation: coaster-agent, celery |
| `ems/` | Dashboard APIs: ecp-dashboard, ems-dashboard |
| `others/` | GPU, topology, event-monitor |

> **重要**: 默认搜索所有节点目录（`ecs.node-*`），除非用户指定只分析某个节点。日志文件可能是 `.log` 或 `.log.gz`，搜索时需同时处理两种格式。

### Step 3: Determine which node hosts the target VM

Use the VM/volume UUID to find which node's logs contain the relevant events:

```bash
# Find which nodes have logs mentioning a VM UUID
for d in ecs.*/; do
  count=$(find "$d" -name "nova-compute*" \( -name "*.log" -o -name "*.log.gz" \) \
    -exec sh -c 'case "$1" in *.gz) zgrep -l "$0" "$1";; *) grep -l "$0" "$1";; esac' \
    "<VM_UUID>" {} \; 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "$(basename $d): $count files match"
done
```

### Step 3.5: Resolve identifier mappings

Before deep-diving, resolve the cross-layer identifiers — the same VM has
**three** names across the stack and each appears in different logs.

```bash
# VM UUID → libvirt domain name (instance-0000XXXX) → qemu log file
grep -hoE "instance-[0-9a-f]{8}" \
  $(grep -l "<VM_UUID>" openstack/nova/nova-compute.*.log libvirt/libvirt.*.log) \
  | sort -u
# Then: libvirt/qemu.instance-<HEX>.<node>.<date>.log

# Volume ID → target IQN / WWID (for iSCSI/Alcubierre volumes)
grep "<VOLUME_ID>" alcubierre/alcubierre-node.*.log | grep -oE "iqn\.[^ ]+|target_iqn[^ ]+|wwid[^ ]+"

# Volume ID → rbd image (for Ceph RBD volumes)
grep "<VOLUME_ID>" openstack/cinder/cinder-volume.*.log | grep -oE "volume-[0-9a-f-]+"

# Request ID propagation (single user action → all services)
grep -rh "<VM_UUID>" openstack/nova/nova-api.*.log | grep -oE "req-[0-9a-f-]+" | sort -u
# Then trace that req-* across services:
grep -r "req-<REQ_UUID>" .
```

See [analysis-playbook.md](analysis-playbook.md) for the full cheatsheet.

### Step 4: Narrow to relevant service area

Based on the issue type, focus on the corresponding log directory:

- **Compute/VM issues** → `openstack/nova/` (nova-compute.log is primary)
- **Volume/storage issues** → `openstack/cinder/`, `libvirt/`, `alcubierre/`, `openstack/nova/`
- **Network issues** → `openstack/neutron/`, `os/openvswitch/`
- **Ceph issues** → `ceph/`, `ceph-k8s/`
- **K8s infrastructure** → `kubernetes/`, `os/messages`
- **Bare-metal / Ironic** → `cloud-products/ironic/`（注意：ironic 等云产品日志放在 `cloud-products/` 而非 `openstack/`）
- **API 网关 / IAM** → `cloud-products/apisix/`、`cloud-products/iam/`

> **⚠ 跨域强制规则**：选定"主服务"只是起点，不是终点。任何**云主机生命周期 / 云盘挂载卸载 /
> 网络变更 / 镜像 / 裸金属**问题，**必须同时把以下日志带入时间线分析**，否则容易把根因归到错的层：
>
> - `os/messages.*.log`（内核 / OOM / SCSI / 多路径 / 网卡链路 / IPMI）
> - `os/openvswitch/*.log`（实际数据面流表是否下发）
> - `openstack/mariadb/*.log` + `openstack/rabbitmq/*.log` + `os/chrony.*.log`（控制面基础设施）
> - `openstack/dozer/bash-history.*.log`（最近的人工动作）
>
> 完整的"问题域 → 必看 / 强相关 / 兜底日志"对照见 [cross-domain-analysis.md](cross-domain-analysis.md)。

### Step 5: Search and analyze

Use targeted grep patterns (see [search-patterns.md](search-patterns.md)) to find error events, then trace timeline across relevant services. Search across all nodes by default.

### Step 6: Cross-reference services

For cross-service issues (e.g., volume attach failure), search the same time window across:
1. `openstack/nova/nova-compute.*.log` - VM lifecycle
2. `openstack/cinder/cinder-volume.*.log` - volume operations
3. `libvirt/libvirt.*.log` - hypervisor operations
4. `alcubierre/alcubierre-node.*.log` - iSCSI connections
5. `os/messages.*.log` - system-level errors

Also probe the **upstream infrastructure** that ~30% of multi-service issues
trace back to:

- `openstack/mariadb/mariadb.*.log` — Galera WSREP state
- `openstack/rabbitmq/rabbitmq.*.log` — AMQP partitions / disconnects
- `os/chrony.*.log` — clock drift (breaks Galera quorum and Ceph)
- `ceph/host.ceph.*.log` — cluster health
- `openstack/dozer/bash-history.*.log` — recent operator actions

### Step 7: Synthesize using the report template

Use the structured output format defined in [analysis-playbook.md](analysis-playbook.md):

- **结论** (1–2 sentences)
- **关键时间线** (table, multi-source, sorted by wrapper TS)
- **根因分析** (symptom → evidence → derivation, with file:line citations)
- **处置建议** (immediate / root-cause / prevention)
- **风险与未验证项**

Cite every claim with `path/to/file:line` so the user can audit the evidence.
