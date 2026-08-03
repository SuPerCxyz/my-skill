# Analysis Playbook

Use this file as the main offline eslog analysis workflow. It coordinates decompression, identifier mapping, timeline construction, and final reporting; use the other reference files only for the specific step you are in.

End-to-end procedure when the user hands you an eslog bundle and a
symptom description. Goal: produce a structured, evidence-cited analysis.

## Standard Workflow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Intake                                                    │
│    - Symptom (what failed)                                   │
│    - Identifiers (VM UUID / volume ID / IP / instance name)  │
│    - Time window (≈ when, ± minutes)                         │
│    - Bundle name (eslog filename gives outer time range)     │
├──────────────────────────────────────────────────────────────┤
│ 2. Decompress (if not yet done)                              │
│    bash scripts/decompress-eslog.sh --input <path>           │
├──────────────────────────────────────────────────────────────┤
│ 3. Inventory: which nodes, which time range                  │
│    ls -d ecs.*/                                              │
│    grep date range from eslog filename                       │
├──────────────────────────────────────────────────────────────┤
│ 4. Locate target node(s) for the identifier                  │
│    (see SKILL.md Step 3)                                     │
├──────────────────────────────────────────────────────────────┤
│ 5. Resolve identifier mapping                                │
│    VM UUID ↔ libvirt domain name (instance-0000XXXX)         │
│    Volume ID ↔ target_iqn / rbd image / dm-X                 │
│    Host IP ↔ node name                                       │
├──────────────────────────────────────────────────────────────┤
│ 6. Pick scenario from troubleshooting.md → run its patterns  │
│    Cross-reference services in the same req-<UUID> or time   │
├──────────────────────────────────────────────────────────────┤
│ 7. Build timeline (sorted, multi-source)                     │
│    sort -k1,2 across files                                   │
├──────────────────────────────────────────────────────────────┤
│ 8. Form root-cause hypothesis with evidence citations        │
│    Validate with at least 2 independent log sources          │
├──────────────────────────────────────────────────────────────┤
│ 9. Output using the report template below                    │
└──────────────────────────────────────────────────────────────┘
```

## Identifier Resolution Cheatsheet

| You have | You need | How |
|----------|----------|-----|
| VM UUID | libvirt domain name | `grep "<UUID>.*instance-" libvirt/libvirt.*.log` or `grep "<UUID>" openstack/nova/nova-compute.*.log` (looks for `[instance: <UUID>] ...`) |
| Domain name | qemu log | `libvirt/qemu.<domain>.<node>.<date>.log` |
| Volume ID | target_iqn | `grep "<VOLUME_ID>" alcubierre/alcubierre-node.*.log` or `grep "<VOLUME_ID>" openstack/cinder/cinder-volume.*.log` |
| Volume ID | rbd image | `grep "<VOLUME_ID>" openstack/cinder/cinder-volume.*.log` (look for `volume-<UUID>`) |
| request ID | all related logs | `grep -r "req-<UUID>"` across all services |
| Pod restart | pod-name change | distinct values of field 3 in the wrapped log |
| Time → node | which node was active | wrapper TS field 1 is collector-monotonic and reliable |

## Confidence Calibration

Before declaring a root cause, ask:

1. **Is the evidence direct?** A Python traceback in nova-compute is direct;
   "the volume is missing from BDM" is inferred — say so.
2. **Has at least one corroborating source confirmed it?** e.g. nova says
   "VolumeDeviceNotFound", alcubierre says "no active iSCSI session for
   wwid X" — these corroborate.
3. **Is there a contradicting signal?** If `os/messages.*.log` shows the
   node never rebooted but nova-compute claims it did — call this out,
   don't paper over.
4. **Did you check the obvious infrastructure?** mariadb (WSREP), rabbitmq
   (network partition), chrony (clock drift), and ceph health are common
   upstream causes of multi-service incidents.

If you can't reach high confidence with the evidence at hand, **say so
explicitly** and list what additional data would close the gap.

## Output Report Template 输出报告模板

使用 [report-format.md](report-format.md) 的无表格模板, 标题后先输出一句话总结。
第 1 节核心结论和第 2 节详细分析固定输出, 第 3 至第 6 节按实际需要输出。第 1 节
放可分享的关键结论与精简日志, 第 2 节放完整证据、排查步骤和判断依据, 前后用桥接
行衔接, 不割裂。时间线按时间顺序使用数字项,
每个事件包含时间、节点、服务、事件和 `path/to/file:line` 证据引用。

命令使用 `bash` fenced code block, 日志使用 `text`, 配置使用对应语言标识。任何
一行都不得以 `-`、`#` 或 `$` 开头。与 `easystack-env-debugging` 联合分析时继续
使用同一模板, 不切换输出结构。

## Anti-Patterns (Don't)

- ❌ **不要**仅凭一条 ERROR 行下结论;OpenStack 经常出现"前置异常被吞掉、后置才报错"的情况。
- ❌ **不要**对 grep 计数下断言:"出现 50 次 ERROR" 不等于"有 50 个故障";
  循环重试会让一次故障刷出几十条。
- ❌ **不要**忽略 OS 层 / Galera / RabbitMQ / Ceph health。这些上游故障
  会以"业务服务报错"的形式呈现，把它们当下游来分析必然找错方向。
- ❌ **不要**把 wrapper TS 和 inner TS 混用做关联;同一行优先用
  wrapper TS(字段 1)做跨服务排序。
- ❌ **不要**只看一个节点。控制平面服务(nova-api/conductor/scheduler、
  cinder-api/scheduler、neutron-server)通常 active-active，事件可能
  发生在任一节点。

## High-Signal Diagnostic Moves(高确定性手段，能用就先用)

> 这些手段用于优先缩小搜索范围。只有证据链完整时才能确认根因, 不承诺固定耗时。

1. **同节点 / 同时段对照组**
   故障 VM A 失败的同时，看节点上其它 VM 是否都失败 / 都成功。
   - 全失败 → 节点级 / 基础设施 / 上游服务问题
   - 只 A 失败 → A 个体(卷、BDM、镜像、qemu xml)问题
   这是把搜索空间从"整个集群"快速收敛到"单实例"的最强手段。

2. **服务可用时间线 vs 失败动作时间**
   节点重启后，nova-compute 何时开始重连卷，alcubierre-target / cinder-volume / libvirt 何时 Starting，对齐时间。如果 nova 在依赖未 ready 时就开始重连，**前几次失败正常**;如果 4 分钟重试窗口内依赖一直没 ready，可能不是 BDM 问题而是部署/编排问题。

3. **重试节奏 = 看是不是标准超时**
   多路径连接典型退避节奏 10/10/10/30/65/130/255/~512s，累计接近 17 分钟。**看到这个节奏意味着 "_connect_volume 等了完整一轮"**，不是网络瞬时抖动。

4. **用 wwid 反查后端 target**
   故障 nova 端 `VolumeDeviceNotFound`，**真正的根因证据在后端 target 日志里**:远端 target 是否 `Applying volume mapping` / `Mapped lun` 过这个 wwid。后端没记录 → 卷根本不在那。比 nova 报错更上游、更可靠。

5. **`target_iqns` 列表是否塌缩**
   多路径正常应跨多节点;4 项全相同 = portal 列表塌缩到单节点 = BDM/connection_info 已陈旧。一行 grep 就能筛出。

6. **req-ID 全链路追踪**
   nova-compute 里抓到主 req(如 `req-30eb5314-...`)，用它一路追到 cinder-volume、alcubierre-node、glance-api，能直接看到"一次用户动作触发的所有跨服务调用"。比按 VM UUID 找更精准。
