# 云主机回收站(Instance Recycle Bin)

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/instance-recycle-bin` |
| 导航路径 | Computing → Instance Recycle Bin |
| 页面标题 | EasyStack Cloud |

## 页面说明

云主机回收站用于防止误操作导致的数据丢失。删除云主机时，默认将其移入回收站而非直接删除。用户可在回收站中恢复或永久删除实例。

> **生命周期**:实例移入回收站后，浮动 IP 和数据磁盘会自动解绑。实例保留 **24 小时**，超时后自动强制删除。

## 从云主机页面删除时的策略选择

从云主机列表删除实例时，弹窗提供两种删除策略(单选):

| 策略 | 说明 |
|------|------|
| Remove to Recycle Bin(默认) | 移入回收站，可恢复 |
| Force Delete | 立即强制删除，不可恢复 |

> ⚠️ Force Delete 会同时删除实例创建的 vNIC。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Restore Instance | 工具栏 icon 按钮 | 默认禁用，选中 1+ 行后可用 |
| Force Delete Instance | 工具栏 icon 按钮 | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 无数据时禁用，有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 状态值 | 说明 |
|--------|------|
| All Status | 默认，显示所有状态 |
| Wait for Delete | 等待删除 |
| Restoring | 正在恢复 |
| Deleting | 正在删除 |

## 高级过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Name |
| Availability Zone |
| Node |
| Tags |
| Flavor:vCPU |
| Flavor:RAM |
| Flavor:DISK |
| Flavor:GPU |
| Boot Source |
| Private IP |
| Floating IP |
| Domain |
| Project |
| Estimated Delete Time |

## 表格列(8 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 实例名称 |
| Availability Zone / Node | ❌ | 可用域和计算节点(两行显示) |
| Status | ✅ | 实例状态 |
| Flavor / Boot Source | ❌ | 规格和启动源(两行显示) |
| IP Address | ❌ | 私网 IP / 浮动 IP |
| Domain / Project | ❌ | 域名和项目(两行显示) |
| Estimated Delete Time | ✅ | 预计自动删除时间 |

### 示例数据行

```
Name: <INSTANCE_NAME>
Availability Zone / Node: <AZ> / <COMPUTE_NODE>
Status: Wait for Delete
Flavor / Boot Source: 1C / 1.0GiB / 1GiB / TestVM
IP Address: (Private IP) <PRIVATE_IP>
Domain / Project: <DOMAIN> / <PROJECT>
Estimated Delete Time: <LOCAL_TIME>
```

## Setup 列配置

可配置列:Name、Availability Zone / Node、Status、Flavor / Boot Source、IP Address、Domain / Project、Estimated Delete Time

按钮:Restore Defaults、Select All、Cancel、Confirm

## Restore Instance 确认弹窗

| 元素 | 说明 |
|------|------|
| 标题 | Restore Instance |
| 描述 | "The amount of instance these will be restored is: N" |
| 补充说明 | "After the instances restored, you can view and manage them in the Instance page." |
| 表格列 | Name(可排序)、Estimated Delete Time(可排序) |
| 按钮 | Cancel、Restore Instance |

## Force Delete Instance 确认弹窗

| 元素 | 说明 |
|------|------|
| 标题 | Force Delete Instance |
| 警告 | "After the instance is forcibly deleted, it cannot be recovered. Please proceed with caution." |
| 补充 | "The vNICs created with the instance will also be deleted automatically." |
| 表格列 | Name(可排序)、Root Disk(可排序) |
| Root Disk 信息 | "Quantity: N, Set to delete with instance: N" |
| 说明 | Root Disk 删除行为说明、Data Disk 不会被删除 |
| 按钮 | Cancel、Force Delete |

## 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉，"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |

## 测试用例

### TC-RCY001: 验证回收站页面加载

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RCY002: 状态过滤验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RCY003: 恢复实例确认弹窗验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RCY004: 永久删除确认弹窗验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RCY005: 高级过滤验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
