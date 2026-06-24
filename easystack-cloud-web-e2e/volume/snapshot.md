# 云硬盘快照测试用例

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/ebs/volume-snapshots` |
| 导航路径 | Service Catalog → Block Storage → Volume Snapshot |
| 页面标题 | EasyStack Cloud |

## 页面说明

云硬盘快照是逻辑保护服务，提供数据保护能力。当卷上的数据遭受病毒入侵或误删时，可以快速恢复到最后一个快照检查点，保护数据安全并提高系统安全性。

## 页面按钮

| 按钮 | 定位方式 | 状态 | 说明 |
|------|--------|------|------|
| Create Volume | `buttonByText("Create Volume")` | 需选择快照 | 从快照创建新卷 |
| Update Status | `buttonByText("Update Status")` | 需选择快照 | 更新快照状态 |
| Roll Back Volume | `buttonByText("Roll Back Volume")` | 需选择快照 | 回滚卷到快照状态 |
| Delete | `buttonByText("Delete")` | 需选择快照 | 删除快照 |
| More | `buttonByText("More")` | 需选择快照 | 更多操作 |

> 注意:所有操作按钮在未选择快照时处于禁用状态

## 表格列信息

| 列名 | 说明 |
|------|------|
| Name | 快照名称 |
| Tags | 标签 |
| Description | 描述 |
| Status | 状态 |
| Size | 大小 |
| Volume Name | 来源卷名称 |
| Domain | 域 |
| Project | 项目 |
| Creation Time | 创建时间 |

## 测试用例

### TC-S001: 从卷创建快照

**前置条件:** 已登录且存在可用卷

**步骤:**
1. 导航到云硬盘页面 (`/ebs/volumes`)
2. 选择一个可用的卷(状态为 Available)
3. 点击 "More" 按钮
4. 选择 "Create Snapshot" 选项
5. 填写快照名称和描述
6. 点击确认创建

**代码:**

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-S002: 查看快照详情

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-S003: 删除快照

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-S004: 从快照恢复卷

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

## 常见快照状态

| 状态 | 说明 |
|------|------|
| Available | 可用，可以进行操作 |
| Creating | 创建中 |
| Restoring | 恢复中 |
| Error | 错误状态 |
| Deleting | 删除中 |
