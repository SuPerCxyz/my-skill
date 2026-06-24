# 云主机分组(Instance Group)

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/instance-groups` |
| 导航路径 | Computing → Instance Group |
| 页面标题 | EasyStack Cloud |

## 页面说明

云主机分组允许将多个实例组织在一起，支持反亲和性策略(Anti-Affinity)，确保组内实例分布在不同计算节点上以提高可用性。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Instance Group | `buttonByText("Create Instance Group")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用，选中 1+ 行后可用 |
| More | `buttonByText("More")` | 默认禁用，选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## 过滤器字段

Name、Tags、Description、Policy、Instances、Domain、Project、Created Time

## 表格列(9 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 分组名称 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Policy | ✅ | 策略(如 anti-affinity) |
| Instances | ✅ | 关联实例数量 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | 创建时间 |

## 创建 Instance Group 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Policy | ✅ | `nz-select` 下拉 | 策略选择 |

Policy 下拉选项:

| 策略 | 说明 |
|------|------|
| anti-affinity | 反亲和性:组内实例分布在不同计算节点 |

弹窗按钮:Cancel、Create

## More 菜单(选中分组后)

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |
| Associate Instances | 关联实例到分组 |
| Disassociate Instances | 从分组中移除实例 |

## 测试用例

### TC-G001: 创建 Instance Group

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-G002: 关联实例到分组

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
