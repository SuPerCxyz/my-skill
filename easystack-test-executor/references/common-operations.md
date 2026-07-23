# Common Operations

## Usage Rules 使用规则

从环境 profile 读取 ID, 不在每个用例前重新执行 list 或 help。所有资源名称包含
`run_id` 和 `case_id`, 创建后立即记录 Name、UUID、owning step 和 creation time。

下面命令优先统一使用 `openstack` client。Server force delete 必须使用环境
profile 中已验证的 `server_force_delete_strategy`; 不得退化成普通
`openstack server delete`。
实际执行位置和认证方式由环境 profile 决定, Password 和 Token 不得写入命令记录。

## Storage Operations 存储操作

### Create Volume 创建云硬盘

```bash
openstack volume create \
  --size <SIZE_GIB> \
  --type <VOLUME_TYPE_ID_OR_NAME> \
  <VOLUME_NAME> \
  -f value -c id
```

### Clone Volume 克隆云硬盘

```bash
openstack volume create \
  --source <SOURCE_VOLUME_ID> \
  --size <SIZE_GIB> \
  --type <VOLUME_TYPE_ID_OR_NAME> \
  <VOLUME_NAME> \
  -f value -c id
```

### Create Snapshot 创建快照

```bash
openstack volume snapshot create \
  --volume <VOLUME_ID> \
  <SNAPSHOT_NAME> \
  -f value -c id
```

### Show And Delete Volume 查询和删除云硬盘

```bash
openstack volume show <VOLUME_ID> -f json
openstack volume delete <VOLUME_ID>
```

等待 Volume 使用 `status=available`; 删除后用精确 Name 或 UUID 查询确认不存在。
Clone、Snapshot、Image copy、Migration 和 Retype 必须从 `cinder-volume` 日志证明
内部路径。

## Compute Operations 计算操作

### Create Server From Boot Volume 从云硬盘创建云主机

```bash
openstack volume create \
  --image <IMAGE_ID> \
  --size <BOOT_VOLUME_SIZE_GIB> \
  --type <VOLUME_TYPE_ID_OR_NAME> \
  <BOOT_VOLUME_NAME> \
  -f value -c id

openstack volume show <BOOT_VOLUME_ID> -f json

openstack server create \
  --volume <BOOT_VOLUME_ID> \
  --flavor <FLAVOR_ID> \
  --nic net-id=<NETWORK_ID> \
  --security-group <SECURITY_GROUP_ID> \
  <SERVER_NAME> \
  -f value -c id
```

所有 Server create 都必须使用这个 boot-from-volume 流程, 禁止
`openstack server create --image` 和隐式临时 root disk。Boot Volume 必须有独立名称,
并立即记录 Name、UUID、Image source、Volume Type、size、创建步骤和本地创建时间。

`server_network_option=nic_net_id` 时使用上面的 `--nic net-id=<NETWORK_ID>`;
只有 profile 已验证 `server_network_option=network` 时才改用
`--network <NETWORK_ID>`。不得在每次用例中重复查询 help。

先等待 Boot Volume 进入 `available`, 再创建 Server。Profile 存在可用 Keypair 时,
在 `<SERVER_NAME>` 前添加 `--key-name <KEYPAIR_NAME>`。Server 进入 `ACTIVE` 后必须
执行 [Default Floating IP Binding 默认绑定公网 IP](#default-floating-ip-binding-默认绑定公网-ip);
只有用例明确设置 `floating_ip: disabled` 时才跳过。

### Attach And Detach Volume 挂载和卸载

```bash
openstack server add volume <SERVER_ID> <VOLUME_ID>
openstack server remove volume <SERVER_ID> <VOLUME_ID>
```

### Show And Force Delete Server 查询和强制删除云主机

```bash
openstack server show <SERVER_ID> -f json
nova force-delete <SERVER_ID>
```

不得使用普通 `openstack server delete`, 因为它可能进入 soft delete/reclaim 流程。
`server_force_delete_strategy=openstack_force` 时使用
`openstack server delete --force --wait <SERVER_ID>`;
`server_force_delete_strategy=nova_client` 时使用
`nova force-delete <SERVER_ID>`。其它 strategy 必须先在目标环境验证并补充通用映射。
执行后轮询确认 Server 不存在。

等待 Server 使用 `status=ACTIVE`; 失败时同时保留 `fault`、event、`nova-compute`
和相关 `cinder-volume` 证据。

## Network Operations 网络操作

### Create Network And Subnet 创建网络和子网

```bash
openstack network create <NETWORK_NAME> -f value -c id

openstack subnet create \
  --network <NETWORK_ID> \
  --subnet-range <CIDR> \
  <SUBNET_NAME> \
  -f value -c id
```

需要显式 Gateway 时, 在 `<SUBNET_NAME>` 前添加 `--gateway <GATEWAY_IP>`。

### Create Router 创建路由器

```bash
openstack router create <ROUTER_NAME> -f value -c id
openstack router set --external-gateway <EXTERNAL_NETWORK_ID> <ROUTER_ID>
openstack router add subnet <ROUTER_ID> <SUBNET_ID>
```

### Create Floating IP 创建 Floating IP

```bash
openstack floating ip create \
  <EXTERNAL_NETWORK_ID> \
  -f json

openstack server add floating ip <SERVER_ID> <FLOATING_IP>
```

保存创建输出并提取 `id` 和 `floating_ip_address`, 两者都写入资源台账。

### Default Floating IP Binding 默认绑定公网 IP

每个新建 Server 默认执行:

1. 等待 Server 进入 `ACTIVE`。
2. 从 profile 的 `external_network_id` 创建 Floating IP。
3. 记录 Floating IP UUID、address、Project、创建步骤和本地创建时间。
4. 使用 `openstack server add floating ip` 绑定。
5. 使用 `openstack floating ip show` 和 `openstack server show` 验证关联关系。
6. 用例要求 connectivity 时, 从授权探测点验证 Floating IP 数据面。

External Network、Floating IP quota 或绑定能力缺失时, 默认 Server create 用例标记为
`BLOCKED`。只有原始计划明确不需要公网访问时, 才允许设置
`floating_ip: disabled` 并在报告说明原因。

### Cleanup Server And Floating IP 清理云主机和公网 IP

```bash
openstack server remove floating ip <SERVER_ID> <FLOATING_IP>
openstack floating ip delete <FLOATING_IP_ID>
nova force-delete <SERVER_ID>
openstack volume delete <BOOT_VOLUME_ID>
```

先解除并删除本次创建的 Floating IP, 再 force delete Server。确认 Server 和
attachment 不存在后, 删除本次创建的 Boot Volume。即使 Server 创建或绑定失败,
也要分别查询 Server、Boot Volume、Port 和 Floating IP, 清理所有已进入资源台账的
对象。

### Cleanup Network 清理网络资源

```bash
openstack router remove subnet <ROUTER_ID> <SUBNET_ID>
openstack router unset --external-gateway <ROUTER_ID>
openstack router delete <ROUTER_ID>
openstack subnet delete <SUBNET_ID>
openstack network delete <NETWORK_ID>
```

严格按依赖逆序清理, 并且只删除运行级资源台账中由本次测试创建的资源。

## Image Operations 镜像操作

Image 的发现、创建、查询和删除统一使用 `openstack image`。

```bash
openstack image list
openstack image show <IMAGE_ID> -f json

openstack image create \
  --disk-format <DISK_FORMAT> \
  --container-format bare \
  --public \
  --file <IMAGE_FILE> \
  <IMAGE_NAME> \
  -f value -c id

openstack image delete <IMAGE_ID>
```

测试创建的 Image 默认使用 `public` visibility。只有测试计划明确验证 private/shared/
community visibility、RBAC 或跨 Project 隔离时才改变 visibility, 并在资源台账记录
实际值。

等待 Image 使用 `status=active`; 失败时保留 `status`、`size`、`checksum`、
`os_hash_value` 和 Glance 实际处理容器日志。上传文件路径、格式和 checksum 必须
进入步骤记录, 但不得把镜像内容写入报告。

## Security Operations 安全操作

此处 Security 指 Neutron Security Group。发现、创建、规则管理和删除统一使用
`openstack security group`。

```bash
openstack security group list
openstack security group show <SECURITY_GROUP_ID> -f json

openstack security group create \
  --description <DESCRIPTION> \
  <SECURITY_GROUP_NAME> \
  -f value -c id

openstack security group rule create \
  --ingress \
  --protocol <PROTOCOL> \
  --dst-port <PORT_MIN>:<PORT_MAX> \
  --src-ip <CIDR> \
  <SECURITY_GROUP_ID> \
  -f value -c id

openstack security group rule delete <SECURITY_GROUP_RULE_ID>
openstack security group delete <SECURITY_GROUP_ID>
```

Security Group 规则验证必须同时检查 Neutron resource state 和实际 dataplane
行为。只测试控制面创建成功时, 报告必须明确未验证 dataplane connectivity。

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
