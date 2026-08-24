## Why

KVM 测试虚拟机目前依赖节点上的临时记忆和手工命令, 容易把模板、磁盘路径、桥接网络和 guest 扩容步骤混在一起. 需要一个可复用的 skill, 在节点或模板变化时仍能安全创建 hub/agent 并给出可验证的 SSH 测试入口.

## What Changes

- 新增 `kvm-test-vm-ops` skill, 覆盖节点发现、模板选择、clone、磁盘扩容和 guest 内扩容.
- 默认将 clone 后的虚拟磁盘扩展到 20 GiB, 并验证 guest 内分区和文件系统实际可用容量.
- 默认将新 VM 配置为 2 vCPU / 1 GiB 内存, 仅在有证据表明内存不足时按 512 MiB 逐级增加, 默认上限为 4 GiB.
- 通过 QGA 查询 guest 状态和地址, 通过 DHCP/网卡信息和 SSH 完成访问闭环验证.
- 使用本地环境和 VM inventory 作为优先访问线索, 经过 freshness check 后复用, 失效时才重新探测.
- 为 DHCP IPv4 设置有界等待窗口, IPv4 尚未就绪时允许使用有效 IPv6 先完成 SSH 验证.
- 将测试环境和每次创建的 VM 信息写入本地忽略文件, 将凭据与 tracked 文档隔离.
- 保留失败现场, 不自动修改模板、桥接、DHCP 或清理测试 VM.

## Capabilities

### New Capabilities

- `kvm-test-vm-operations`: 动态发现 KVM 测试环境并安全创建、扩容、验证 hub/agent 虚拟机.

### Modified Capabilities

无.

## Impact

- 新增 `kvm-test-vm-ops/` skill 文档、参考资料和环境记录模板.
- 更新根 `README.md` 的 Skills 列表.
- 新增 OpenSpec capability spec.
- 运行时通过 SSH 使用目标节点上的 `virsh`, `virt-clone`, `qemu-img` 和 QGA, 不新增仓库依赖.
- 经确认的真实验收会在当前 KVM 节点新增两台测试 VM, 但不修改源模板.
