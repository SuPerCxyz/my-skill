# Compute Impact Matrix

## Purpose 目标

Nova 改动不能只验证 Server create。按操作、资源关系、调度、生命周期和失败恢复展开,
并结合目标环境的 virt driver、microversion、配置和 support matrix 收敛。

## Mandatory Paths 必查路径

| 改动点 | 关联正向路径 | 关联异常和恢复 | 关键证据 |
|--------|--------------|----------------|----------|
| Server create | Boot Volume、Port、Security Group、Floating IP、AZ、scheduler hint | build error、no valid host、quota、rollback、残留 Port/Volume | nova-scheduler、nova-conductor、nova-compute、cinder-volume |
| Flavor/spec | create、resize、rebuild、evacuate、migration | 不支持 spec、资源不足、回滚 | Request spec、allocation、instance action |
| Attach interface | Port create/attach/detach、fixed IP、Security Group | binding failure、重复 detach、残留 binding | neutron-server、L2 agent、nova-compute |
| Attach volume | data volume、multiattach、encrypted、detach | connector failure、busy、attachment 残留 | nova-compute、cinder-volume、os-brick |
| Host operation | live/cold migration、evacuate、shelve | destination failure、rollback、allocation 泄漏 | Placement、scheduler、compute 两端 |
| Image operation | boot、rebuild、snapshot、rescue | download failure、format、image status | nova-compute、glance-api、hypervisor |

## Driver Boundaries Driver 边界

- 分别判断 libvirt/KVM、Ironic 和其它 virt driver, 不把 Nova API 可接受等同于 driver
  支持。
- Ironic Server 没有虚拟机磁盘和虚拟 NIC 的完全等价语义。Volume connector、
  boot-from-volume、encrypted attach 和 config-drive 必须分别查 support matrix。
- NUMA、CPU pinning、huge page、PCI/SR-IOV 和 vGPU 会同时影响 Placement trait、
  scheduler filter/weigher、compute claim 和 migration compatibility。
- Live migration 需展开 shared/non-shared storage、block migration、encrypted volume、
  attached port、CPU compatibility 和 destination capacity。

## Default Server Contract 默认 Server 契约

本 skill 创建 Server 时默认:

1. 使用 Image 创建 Boot Volume。
2. 以 `--volume <BOOT_VOLUME_ID>` 启动, 不使用 `--image` 临时 root disk。
3. 使用显式 Network、Security Group 和 Port/Network 选择。
4. 创建并绑定 Floating IP, 验证 Server、Port 和 Floating IP 三方关系。
5. 删除时使用环境已验证的 force delete strategy。
6. 独立验证 Server、Boot Volume、Port 和 Floating IP 的最终状态及残留。

## Regression Obligations 回归义务

- API 成功不代表 guest ready。至少分开验证 Nova 状态、task_state、power state 和 guest
  reachability。
- Server 失败后检查 Placement allocation、Cinder attachment、Neutron Port binding、
  Floating IP association 和 instance mapping。
- 影响 scheduler 或 resource tracking 时覆盖新建和已有 Server, 并覆盖 source 和
  destination host。
- 影响删除语义时覆盖 ACTIVE、ERROR、BUILD 和迁移中 Server, 但只操作本次创建资源。
