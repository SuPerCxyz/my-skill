# 浮动 IP(Floating IP / 公网 IP)

Use this file when the UI task specifically involves floating IP list fields, allocation, association, release, or related assertions. For reusable action sequences, prefer [patterns/network-ops.md](../patterns/network-ops.md).

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/ens/floatingIPs` |
| 导航路径 | Network → Floating IP |
| 页面标题 | Floating IP |

## 页面说明

浮动 IP(Floating IP)用于管理云平台中的公网 IP 地址。用户可在此页面分配、释放、绑定和解绑浮动 IP，为云主机提供公网访问能力。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Apply For IP To Project | `agent-browser find text "Apply For IP To Project" click` | 始终可用 |
| Release Floating IPs | 顶部批量按钮 | 默认禁用，选中 1+ 行后可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## 状态过滤下拉

定位方式:`nz-select`(含 "All Status" 文本)

| 状态值 | 说明 |
|--------|------|
| All Status | 默认，显示所有状态 |
| Bound | 已绑定(绑定到某个端口/实例) |
| Unbound | 未绑定(空闲状态) |

## 过滤器字段

定位方式:`input[placeholder="Click here for filters."]`

| 过滤字段 |
|----------|
| Floating IP / Name |
| Description |
| Status |
| Port |
| Domain |
| Project |
| Created At |

## 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| IP Address | ✅ | 浮动 IP 地址 |
| Tags | ❌ | 标签 |
| Related router | ❌ | 关联路由 |
| Attach Resource | ✅ | 已绑定资源，如 `Instance: <name>` |
| Bandwidth(Mbps) | ✅ | 带宽 |
| Floating IP Pool | ✅ | 资源池 |
| Domain/Project | ❌ | 租户/项目 |
| Creation Time | ✅ | 创建时间 |
| Action | ❌ | 行内动作列 |

### 行内动作实测

- 已绑定资源行:
  `Release Floating IPs`、`Disassociate`、`Update Bandwidth`、`More`
- 未绑定资源行:
  `Release Floating IPs`、`Bind to resource`、`Update Bandwidth`、`More`

## 勾选与批量操作

- 未勾选时，顶部 `Release Floating IPs` disabled
- 勾选单条后，顶部 `Release Floating IPs` enabled
- 本页同时存在“顶部批量动作”和“行内动作”，不要混淆两类入口

## 权限限制

- 以当前云管理员账号在某些浮动 IP 上点击 `Bind to resource` 时，页面可能不会弹出
  绑定表单，而是直接提示:
  `Please do this by re-logging into the console as the project administrator/user to which the resource belongs`
- 这属于产品权限反馈，不应误判为自动化 click 失败。

## Setup 列配置

可配置列:Floating IP / Name、Description、Port、Status、Created At

按钮:Restore Defaults、Select All、Cancel、Confirm

## Allocate Floating IP 弹窗

标题:**Apply For IP To Project**

> ⚠️ 注意:由于物理节点上承载公网流量的物理网卡的带宽限制，浮动 IP 的最大带宽设置不能大于 1000 Mbps。

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Project | ✅ | `nz-select` 下拉 | 选择目标项目，默认 Default:admin |
| Resource Pool | ✅ | `nz-select` 下拉 | 选择浮动 IP 资源池，默认 public_net_1 0/253 |
| Floating IP | ❌ | `input` 文本输入 | 占位符:"Please enter IP address."，可选填写特定 IP |
| Bandwidth | ✅ | 数字输入框 | 单位 Mbps，默认 1，范围 1-1000 |

弹窗按钮:Cancel、Allocate

> 可通过 "Add IP address." 按钮添加多个 IP 地址。不填写 Floating IP 时系统自动分配。

## 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉，"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |

## 测试用例

### TC-FIP001: 验证浮动 IP 页面加载

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-FIP002: Allocate Floating IP 弹窗验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-FIP003: 状态过滤验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-FIP004: 按名称过滤浮动 IP

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
