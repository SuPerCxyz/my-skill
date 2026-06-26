# 可用域与主机聚合(AZ & Host Aggregates)

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/availability-zones` |
| 导航路径 | Computing → AZ & Host Aggregates |
| 页面标题 | EasyStack Cloud |

## 页面说明

可用域(Availability Zone)用于将物理资源逻辑分组，支持跨可用域部署以提高容灾能力。主机聚合(Host Aggregate)允许将主机分组并应用特定的调度策略。

## 标签页

| 标签 | 定位方式 | 说明 |
|------|--------|------|
| Availability Zone | `tab "Availability Zone"` | 默认，可用域列表 |
| Host Aggregate | `tab "Host Aggregate"` | 主机聚合列表 |

## Availability Zone 标签页

### Availability Zone 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Availability Zone | `buttonByText("Create Availability Zone")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Delete | `buttonByText("Delete")` | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

### Availability Zone 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 可用域名称 |
| Description | ✅ | 描述 |
| Hosts | ✅ | 关联主机数 |
| Instances | ✅ | 实例数 |
| Projects | ✅ | 项目数 |
| Created Time | ✅ | 创建时间 |

### 创建 Availability Zone 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |

弹窗按钮:Cancel、Create

## Host Aggregate 标签页

### Host Aggregate 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Host Aggregate | `buttonByText("Create Host Aggregate")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit | `buttonByText("Edit")` | 默认禁用，选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

### Host Aggregate 表格列

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 聚合名称 |
| Description | ✅ | 描述 |
| Availability Zone | ✅ | 所属可用域 |
| Hosts | ✅ | 关联主机 |
| Metadata | ✅ | 元数据标签 |
| Projects | ✅ | 项目数 |
| Created Time | ✅ | 创建时间 |

### 创建 Host Aggregate 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Availability Zone | ✅ | `nz-select` 下拉 | 选择已有可用域 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Metadata | ❌ | 键值对输入 | 自定义元数据 |

弹窗按钮:Cancel、Create

### Edit Host Aggregate 弹窗

与创建弹窗类似，预填充已有数据。

## 过滤器字段

Name、Description、Availability Zone、Hosts、Metadata、Projects、Created Time

## 测试用例

### TC-AZ001: 创建 Availability Zone

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-AZ002: 创建 Host Aggregate

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
