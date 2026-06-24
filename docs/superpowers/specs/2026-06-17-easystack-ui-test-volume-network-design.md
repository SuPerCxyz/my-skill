# easystack-ui-test volume/network 操作库迁移设计

## 背景

`patterns/login.md`、`patterns/instance-ops.md`、
`patterns/quick-reference.md` 已完成第一轮契约收敛，但
`patterns/volume-ops.md` 和 `patterns/network-ops.md` 仍停留在旧格式:

- 仍以匿名脚本片段集合为主
- 仍包含硬编码 URL
- 返回值仍以自由字符串为主
- 高价值操作与遗留操作没有明确迁移状态
- `quick-reference.md` 目前只能把 volume 项保持为 `legacy`

这两份文件如果不继续迁移，会成为 `patterns` 层剩余的主要不一致来源。

## 本轮目标

本轮只处理 `patterns` 操作库第二轮迁移:

- `easystack-ui-test/patterns/volume-ops.md`
- `easystack-ui-test/patterns/network-ops.md`
- `easystack-ui-test/patterns/quick-reference.md`(仅同步索引)

## 迁移策略

采用和 `instance-ops.md` 相同的模式:

- 文档头部声明统一契约
- 明确 `ready / planned` 边界
- 只迁移少量高频操作
- 其余操作保留为待迁移名称清单

## 本轮 ready 操作

### `volume-ops.md`

- `create_volume`
- `delete_volume`
- `upload_image`

说明:

- `create_volume` 覆盖块存储最核心入口
- `delete_volume` 覆盖最常见回收动作
- `upload_image` 覆盖当前 volume 文档里承担的镜像入口

### `network-ops.md`

- `allocate_floating_ip`
- `create_network`
- `create_router`

说明:

- `allocate_floating_ip` 覆盖公网资源入口
- `create_network` 与 `create_router` 覆盖网络域最关键的两个创建动作

## 统一模板

每个 ready 操作统一包含:

1. 用途
2. 参数
3. 前置条件
4. 成功判定
5. 执行步骤概览
6. 失败信号
7. 返回值约定
8. `browser_run_code_unsafe` 示例

## 环境契约

所有示例统一:

- 从 `/tmp/easystack-env.json` 读取
- 使用 `platform.*`
- 必要时使用 `resources.*`
- 不再硬编码真实 URL

## 返回值约定

所有 ready 操作统一返回结构化对象，至少包含:

```json
{
  "ok": true,
  "resource": "volume",
  "action": "create",
  "name": "vol-01",
  "status": "Available",
  "message": "volume created",
  "url": "https://example.local/ebs/volumes"
}
```

失败时保持相同结构，并将:

- `ok` 设为 `false`
- `status` 写最终观察状态或失败类别
- `message` 写关键失败原因

## `volume-ops.md` 设计

### 文档头部

应与 `instance-ops.md` 风格一致，声明:

- 依赖 `patterns/login.md`
- 显式参数优先于环境默认值
- 所有 ready 操作必须显式验证结果状态

### 遗留操作处理

不在本轮迁移的 volume 相关操作，如:

- `create_volume_snapshot`
- `extend_volume`
- `edit_volume`
- `create_image_from_volume`
- `delete_volume_snapshot`

统一改成待迁移名称清单，而不是保留大量旧匿名代码块。

## `network-ops.md` 设计

### 文档头部

应与 `instance-ops.md`、`volume-ops.md` 对齐，声明:

- 依赖 `patterns/login.md`
- 默认执行入口使用当前基础层路径口径
- ready 操作必须显式验证结果状态

### 命名收敛

当前“分配浮动 IP”文案可以继续面向 `allocate_floating_ip`，
不再依赖自然语言标题作为事实函数名。

### 遗留操作处理

不在本轮迁移的操作，如:

- `associate_network`
- `disassociate_network`
- `edit_security_group`

统一改成待迁移名称清单。

## `quick-reference.md` 同步策略

索引层需要同步反映:

- `create_volume` / `delete_volume` / `upload_image` -> `ready`
- `allocate_floating_ip` / `create_network` / `create_router` -> `ready`
- 仍未迁移的 volume/network 名称条目 -> `planned`

## 验证标准

完成后应满足:

1. `volume-ops.md` 与 `network-ops.md` 不再包含真实 URL
2. 两份文档的 ready 操作使用统一模板
3. `quick-reference.md` 中 ready/planned 状态与实际文档一致
4. 不再保留大段旧匿名代码块与新模板混杂的结构

## 本轮不做

- 不做真实 UI 回放验证
- 不治理其他知识文档
- 不扩展到 `instance-ops.md`

## 预期产出

本轮完成后，`patterns` 核心操作库会形成三段式:

- `login.md`:共享前置契约
- `instance-ops.md` / `volume-ops.md` / `network-ops.md`:分域模板化操作库
- `quick-reference.md`:统一索引与迁移状态看板
