# Common Operations

## Usage Rules 使用规则

从环境 profile 读取 ID, 不在每个用例前重新执行 list 或 help。资源名称使用
`test-<case_id>-<role>-<short_suffix>`。`run_id` 只用于结果目录和内部关联, 不写入
OpenStack 资源名称。创建后立即记录 Name、UUID、owning step 和 creation time。

下面命令优先统一使用 `openstack` client。Server force delete 必须使用环境
profile 中已验证的 `server_force_delete_strategy`; 不得退化成普通
`openstack server delete`。
实际执行位置和认证方式由环境 profile 决定, Password 和 Token 不得写入命令记录。

## Operation Catalog 操作目录

不要将所有 OpenStack 操作加载进上下文。先列出 domain 操作, 再查询目标项:

```bash
python3 scripts/query-catalog.py --domain storage
python3 scripts/query-catalog.py --domain storage --operation volume_retype
```

Domain 为 `compute`、`storage`、`network-image-security` 和 `baremetal`。Catalog
返回 command template、services、checks 和不变量; Plan 必须把选中项转为 V3 Action。

## Compute Operations 计算操作

所有 Server create 必须先创建具名 Boot Volume, 再使用 `--volume`; 禁止 image-backed
ephemeral root。Server ACTIVE 后默认创建并绑定 Floating IP, 只有 plan 明确禁用时跳过。

Server 删除必须使用 profile 已验证的 force delete strategy, 禁止回退为普通
`openstack server delete`。清理顺序为 Floating IP -> Server -> attachment -> Boot
Volume, 每一步精确确认终态。

## Network Operations 网络操作

Network、Subnet、Router、Port、Floating IP、QoS 和 Trunk 均使用 `openstack`
命令及 JSON output capture。Control plane create 成功不能证明 dataplane; 用例必须
明确是否验证 DHCP、routing、security enforcement 或 guest connectivity。

Cleanup 按 Floating IP -> Port/Router interface -> Router gateway -> Router ->
Subnet -> Network 的逆依赖顺序执行。

## Image Operations 镜像操作

Image 操作统一使用 `openstack image`。测试创建的 Image 默认 `--public`; 只有测试
visibility/RBAC 时允许改变。验证 active、visibility、size、checksum/os_hash 和实际
import worker; 不将 image 内容写入报告。

## Security Operations 安全操作

Security Group 统一使用 `openstack security group`。规则验证同时检查 Neutron
resource state 和 dataplane; 未验证 connectivity 时必须在报告说明。

## Polling Pattern 轮询方法

异步资源统一按 Name 或 UUID 执行精确 show:

```text
记录 poll start
-> show resource
-> success state: 结束
-> failure state: 收集证据并结束
-> timeout: 记录最后状态并结束
-> 未终态: 等待 poll_interval 后重试
```

不要用反复 list 代替精确 show。Poll 过程记录每次状态变化, 相同状态无需重复粘贴。

## Data-Path Log Targets 数据路径日志目标

操作到日志目标的映射以 [case-normalization.md](case-normalization.md) 为唯一来源;
采集优先级和内部路径证据使用 [log-evidence.md](log-evidence.md)。
