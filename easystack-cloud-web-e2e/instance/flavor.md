# 实例规格(Instance Flavor)

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/flavors` |
| 导航路径 | Computing → Instance Flavor |
| 页面标题 | EasyStack Cloud |

## 页面说明

实例规格定义了云主机的计算资源配额(vCPU、内存、根磁盘、临时磁盘)。创建云主机时需选择合适的规格。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Flavor | `buttonByText("Create Flavor")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Edit Tags | `buttonByText("Edit Tags")` | 默认禁用，选中 1+ 行后可用 |
| Edit | `buttonByText("Edit")` | 默认禁用，选中 1+ 行后可用 |
| Delete | `buttonByText("Delete")` | 默认禁用，选中 1+ 行后可用 |
| Export | 工具栏 Export icon | 有数据时可用 |
| Setup | 工具栏 Setup icon | 始终可用 |

## 过滤器字段

Name、Tags、Description、Category、vCPUs、Memory Size、Root Disk Size、Ephemeral Disk Size、Swap Disk Size、RX/TX Factor、Domain、Project、Created Time

## 表格列(15 列)

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 规格名称 |
| Tags | ❌ | 标签 |
| Description | ✅ | 描述 |
| Category | ✅ | 分类 |
| vCPUs | ✅ | 虚拟 CPU 数量 |
| Memory Size | ✅ | 内存大小 |
| Root Disk Size | ✅ | 根磁盘大小 |
| Ephemeral Disk Size | ✅ | 临时磁盘大小 |
| Swap Disk Size | ✅ | 交换磁盘大小 |
| RX/TX Factor | ✅ | 网络收发因子 |
| Domain | ✅ | 域名 |
| Project | ✅ | 项目 |
| Created Time | ✅ | 创建时间 |

### 规格分类(Category)

| 分类 | 说明 |
|------|------|
| general | 通用计算 |
| computing-optimized | 计算优化 |
| network-optimized | 网络优化 |
| computing-network-optimized | 计算网络优化 |
| gpu-accelerated | GPU 加速 |

## 创建 Flavor 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Description | ❌ | `input[placeholder="Enter a description"]` | 描述 |
| Category | ✅ | `nz-select` 下拉 | 分类选择 |
| vCPUs | ✅ | `input[type="number"]` | 正整数 |
| Memory Size | ✅ | 数字输入 + 单位选择 | MB 或 GB |
| Root Disk Size | ✅ | 数字输入 + 单位选择 | GB |
| Ephemeral Disk Size | ❌ | 数字输入 + 单位选择 | GB，默认 0 |
| Swap Disk Size | ❌ | 数字输入 + 单位选择 | MB，默认 0 |
| RX/TX Factor | ❌ | 数字输入 | 网络因子，默认 1.0 |

弹窗按钮:Cancel、Create

## More 菜单(选中规格后)

| 操作 | 说明 |
|------|------|
| Edit Tags | 编辑标签 |

## 测试用例

### TC-F001: 创建 Instance Flavor

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
