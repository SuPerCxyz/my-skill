# 云主机快照（Instance Snapshot）

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识；执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/instance-snapshots` |
| 导航路径 | Computing → Instance Snapshot |
| 页面标题 | EasyStack Cloud |

## 页面说明

实例快照是特定时间点上根磁盘和卷磁盘数据的完整副本。可用于将实例恢复到快照创建时的状态。

> **注意**：快照没有独立的"创建"按钮，需从云主机页面 More → Create Snapshot 创建。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏第一个 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用，选中 1+ 行后可用 |
| More | `buttonByText("More")` | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 无数据时禁用，有数据时可用 |
| Setup | 工具栏最后一个 icon 按钮 | 始终可用 |

## 状态过滤下拉

定位方式：`nz-select`（含 "All Status" 文本）

| 选项 |
|------|
| All Status（默认） |
| Available |
| Pending Delete |
| Deleted |
| Saving |
| Queued |
| Creating |

## 过滤器字段

Name、Tags、Description、Snapshot Source、Size、Format、Domain、Project、Created Time

## 表格列（11 列）

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 快照名称，点击进入详情 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Status | ✅ | 状态徽章 |
| Snapshot Source | ✅ | 来源实例名称 |
| Size | ✅ | 磁盘大小 |
| Format | ✅ | 镜像格式 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | YYYY-MM-DD HH:mm:ss |

## Setup 列配置

可配置列：Name、Tags、Description、Status、Snapshot Source、Size、Format、Domain、Project、Created Time

按钮：Restore Defaults、Select All、Cancel、Confirm

## More 菜单（选中快照后）

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |
| Delete | 删除快照 |

## 创建快照（从云主机页面）

入口：Instance 页面 → 选择实例 → More → Create Snapshot

### 创建快照弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Snapshot Name | ✅ | `textbox "Enter 1 to 128 characters in length"` | 1-128 字符 |
| Description | ❌ | `textbox "Enter a description"` | 描述 |

弹窗按钮：Cancel、Create

> ⚠️ 警告信息："It is strongly recommended to create snapshot during the shutdown state of the instance or during non busy periods of instance I/O, otherwise it may cause data consistency issues."

## 测试用例

### TC-S001: 从云主机创建快照

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-S002: 恢复快照（Snapshot Rollback）

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-S003: 删除快照

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
