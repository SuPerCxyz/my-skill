---
name: easystack-log-analysis
description: "Use when analyzing offline EasyStack `.eslog` bundles or extracted `ecs.*` directories across OpenStack, Kubernetes, OS, Ceph, RabbitMQ, MariaDB, and operation history. Combine with `easystack-env-debugging` for older incidents that also require live checks. Do not use for unrelated generic logs."
---

# EasyStack Log Analysis

## Overview 概览

EasyStack 诊断日志以带密码的 `.eslog` 文件形式下发。解压后得到 `ecs.<host>.<date>.[N]/` 目录树, 内含按功能域组织的 Kubernetes pod 容器化服务日志。

本 skill 指导 eslog 解压、目录映射与针对常见 OpenStack-on-K8s 故障场景的定向日志分析。

## Scope Boundary 适用边界

适用于用户提供 `.eslog` 或已解压 `ecs.*` 目录的离线分析。历史故障同时需要登录
运行中环境执行 kubectl/SSH 检查时, MUST 联合使用 `easystack-env-debugging`, 并以两个
skill 共同维护的无表格报告格式输出。代码仓库测试使用 `easystack-ci-test`; Web 页面
E2E 使用 `easystack-cloud-web-e2e`。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| **标准端到端分析流程 + 报告模板** | [analysis-playbook.md](analysis-playbook.md) |
| 无表格、可复制的问题分析结论格式 | [report-format.md](report-format.md) |
| **跨域关联分析矩阵(云主机/云盘/网络/镜像/裸金属 必看哪些日志)** | [cross-domain-analysis.md](cross-domain-analysis.md) |
| 解压 eslog 文件 | [decompress.md](decompress.md) |
| 安全解压脚本 | [scripts/decompress-eslog.sh](scripts/decompress-eslog.sh) |
| 日志行格式(wrapper / 字段 / awk 配方) | [log-format.md](log-format.md) |
| 日志目录结构映射 | [directory-map.md](directory-map.md) |
| 按问题类型检索的模式 | [search-patterns.md](search-patterns.md) |
| 故障排查场景与实战 case | [troubleshooting.md](troubleshooting.md) |

## Workflow 工作流

### Step 1: 解压

用户指定路径时显式传给 `--input`; 未指定时脚本默认处理当前目录顶层的所有
`.eslog`。输出目录默认是当前目录, 也可通过 `--output` 指定:

```bash
bash scripts/decompress-eslog.sh --input <FILE_OR_DIR> --output <OUTPUT_DIR>
```

输出: `ecs.<host>.<date>.<N>/` 目录(每个 host 一个)。再次解压时直接合并同名目录:
同路径文件使用新内容覆盖, 新文件追加, 本次 bundle 未包含的旧文件保留。不要因已有
结果而跳过解压。默认保留 `.log.gz` 以避免大 bundle 耗尽磁盘; 只有确认空间充足
时才传 `--decompress-logs`。

> **时间窗提示**: eslog 文件名本身编码了采集时间范围:
> `ecs.20260618-20260623183823.eslog` = 2026-06-18 00:00 -> 2026-06-23 18:38:23。
> 先读它判断这个 bundle 能回答哪个时间窗的问题, 再缩窄搜索范围。

> **日志行格式**: 每行日志都有 5 字段 wrapper
> `<ts> +0800 ¦ <node> ¦ <pod> ¦ <container> ¦ <raw>`。纯文本 `grep`
> 可直接使用; 需要按 pod / container 聚合时参考
> [log-format.md](log-format.md) 的 awk 配方。

### Step 2: 理解目录布局

顶层目录映射到各服务层:

| Directory 目录 | Contents 内容 |
|-----------|----------|
| `openstack/` | OpenStack 核心服务: nova, cinder, neutron, glance, keystone 等 |
| `libvirt/` | Hypervisor: libvirtd, qemu 实例, sync, ceph placement |
| `alcubierre/` | Alcubierre iSCSI 存储节点 agent, target init, exporter |
| `ceph/` | Ceph monitor, manager, OSD, RGW 日志 |
| `ceph-k8s/` | Ceph OSD 磁盘准备, 隔离 |
| `kubernetes/` | K8s 系统: kube-apiserver, scheduler, controller-manager, coredns, flannel |
| `os/` | OS messages, chrony, openvswitch |
| `cloud-products/` | API 网关(apisix), IAM |
| `ecms/` | 监控: prometheus, grafana, alertmanager, fluentd |
| `ecas/` | 自动化: coaster-agent, celery |
| `ems/` | 仪表盘 API: ecp-dashboard, ems-dashboard |
| `others/` | GPU, topology, event-monitor |

> **重要**: 默认搜索所有节点目录(`ecs.node-*`), 除非用户指定只分析某个节点。日志文件可能是 `.log` 或 `.log.gz`, 搜索时需同时处理两种格式。

### Step 3: 定位目标 VM 所在计算节点

用 VM / volume UUID 查找哪些节点的日志包含相关事件:

```bash
# Find which nodes have logs mentioning a VM UUID
for d in ecs.*/; do
  count=$(find "$d" -name "nova-compute*" \( -name "*.log" -o -name "*.log.gz" \) \
    -exec sh -c 'case "$1" in *.gz) zgrep -l "$0" "$1";; *) grep -l "$0" "$1";; esac' \
    "<VM_UUID>" {} \; 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "$(basename $d): $count files match"
done
```

### Step 3.5: 解析标识符映射

深入排查前, 先解析跨层标识符 - 同一个 VM 在栈内有**三种**名字, 各自出现在不同日志中。

```bash
# VM UUID -> libvirt domain name (instance-0000XXXX) -> qemu log file
grep -hoE "instance-[0-9a-f]{8}" \
  $(grep -l "<VM_UUID>" openstack/nova/nova-compute.*.log libvirt/libvirt.*.log) \
  | sort -u
# Then: libvirt/qemu.instance-<HEX>.<node>.<date>.log

# Volume ID -> target IQN / WWID (for iSCSI/Alcubierre volumes)
grep "<VOLUME_ID>" alcubierre/alcubierre-node.*.log | grep -oE "iqn\.[^ ]+|target_iqn[^ ]+|wwid[^ ]+"

# Volume ID -> rbd image (for Ceph RBD volumes)
grep "<VOLUME_ID>" openstack/cinder/cinder-volume.*.log | grep -oE "volume-[0-9a-f-]+"

# Request ID propagation (single user action -> all services)
grep -rh "<VM_UUID>" openstack/nova/nova-api.*.log | grep -oE "req-[0-9a-f-]+" | sort -u
# Then trace that req-* across services:
grep -r "req-<REQ_UUID>" .
```

完整速查表见 [analysis-playbook.md](analysis-playbook.md)。

### Step 4: 缩窄到相关服务域

按问题类型聚焦对应日志目录:

- **计算 / VM 问题** -> `openstack/nova/`(nova-compute.log 为主)
- **云盘 / 存储问题** -> `openstack/cinder/`, `libvirt/`, `alcubierre/`, `openstack/nova/`
- **网络问题** -> `openstack/neutron/`, `os/openvswitch/`
- **Ceph 问题** -> `ceph/`, `ceph-k8s/`
- **K8s 基础设施** -> `kubernetes/`, `os/messages`
- **裸金属 / Ironic** -> `cloud-products/ironic/`(注意: ironic 等云产品日志放在 `cloud-products/` 而非 `openstack/`)
- **API 网关 / IAM** -> `cloud-products/apisix/`, `cloud-products/iam/`

> **跨域强制规则**: 选定"主服务"只是起点, 不是终点。任何**云主机生命周期 / 云盘挂载卸载 / 网络变更 / 镜像 / 裸金属**问题, **必须同时把以下日志带入时间线分析**, 否则容易把根因归到错的层:
>
> - `os/messages.*.log`(内核 / OOM / SCSI / 多路径 / 网卡链路 / IPMI)
> - `os/openvswitch/*.log`(实际数据面流表是否下发)
> - `openstack/mariadb/*.log` + `openstack/rabbitmq/*.log` + `os/chrony.*.log`(控制面基础设施)
> - `openstack/dozer/bash-history.*.log`(最近的人工动作)
>
> 完整的"问题域 -> 必看 / 强相关 / 兜底日志"对照见 [cross-domain-analysis.md](cross-domain-analysis.md)。

### Step 5: 检索与分析

用定向 grep 模式(见 [search-patterns.md](search-patterns.md))查找错误事件, 再跨相关服务追时间线。默认跨所有节点搜索。

### Step 6: 跨服务关联

对跨服务问题(如云盘挂载失败), 在同一时间窗内检索:
1. `openstack/nova/nova-compute.*.log` - VM 生命周期
2. `openstack/cinder/cinder-volume.*.log` - 云盘操作
3. `libvirt/libvirt.*.log` - hypervisor 操作
4. `alcubierre/alcubierre-node.*.log` - iSCSI 连接
5. `os/messages.*.log` - 系统层错误

同时探测**上游基础设施**。多服务问题常会追溯到这些层, 不能只检查业务服务:

- `openstack/mariadb/mariadb.*.log` -- Galera WSREP 状态
- `openstack/rabbitmq/rabbitmq.*.log` -- AMQP 脑裂 / 断连
- `os/chrony.*.log` -- 时钟漂移(会破坏 Galera 仲裁与 Ceph)
- `ceph/host.ceph.*.log` -- 集群健康
- `openstack/dozer/bash-history.*.log` -- 最近运维动作

### Step 7: Report 汇总报告

MUST 使用 [report-format.md](report-format.md) 的无表格结构。第 1 至第 4 节固定输出,
第 5 至第 8 节按实际需要输出。关键时间线使用普通 Markdown 列表, 命令、日志和配置
使用 fenced code block。每条结论用 `path/to/file:line` 引证, 便于用户审计证据链。

与 `easystack-env-debugging` 联合分析时, 两个 skill 使用相同模板, 不再切换为表格或
其他报告结构。

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
