# SSH 密钥对（SSH Key Pair）

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识；执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

## 页面信息

| 项目 | 值 |
|------|-----|
| URL | `https://<IP>/eec/keypairs` |
| 导航路径 | Computing → SSH Key Pair |
| 页面标题 | EasyStack Cloud |

## 页面说明

SSH 密钥对基于非对称加密，用于安全访问云主机。创建云主机时可选择公钥，平台不保存私钥。用户需通过本地私钥访问实例。

## 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Create Key Pair | `buttonByText("Create Key Pair")` | 始终可用 |
| Refresh | 工具栏 icon 按钮 | 始终可用 |
| Import Key Pair | `buttonByText("Import Key Pair")` | 始终可用 |
| Edit Tag | `buttonByText("Edit Tag")` | 默认禁用，选中 1+ 行后可用 |
| Delete Key Pair | `buttonByText("Delete Key Pair")` | 默认禁用，选中 1+ 行后可用 |
| Export | `buttonByText("Export")` | 始终可用 |
| Setup | `buttonByText("Setup")` | 始终可用 |

## 过滤器字段

Name、Tags、User、Fingerprint

## 表格列（5 列）

| 列名 | 可排序 | 说明 |
|------|--------|------|
| (展开/折叠) | ❌ | 展开显示公钥 |
| (选择框) | ❌ | 全选 checkbox |
| Name | ✅ | 密钥对名称 |
| Tags | ❌ | 标签 |
| User | ✅ | 创建用户 |
| Fingerprint | ✅ | MD5 指纹 |

### 展开行（子表格）

点击展开按钮显示公钥内容：

| 列名 | 说明 |
|------|------|
| Public Key | 完整公钥文本（如 ssh-ed25519 AAAA...） |

## Setup 列配置

可配置列：Name、Tags、User、Fingerprint

按钮：Restore Defaults、Select All、Cancel、Confirm

## Export 行为

点击 Export 立即下载 CSV 文件

文件名格式：`SSH Key Pair_YYYYMMDDHHmmss.csv`

CSV 列：Name、Tags、User、Fingerprint、Public Key

## 创建 Key Pair 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Key Pair Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |

弹窗按钮：Cancel、Create

> 创建后会显示私钥下载对话框，需立即保存私钥。

## Import Key Pair 弹窗

| 字段 | 必填 | 定位方式 | 说明 |
|------|------|--------|------|
| Key Pair Name | ✅ | `input[placeholder="Enter 1 to 128 characters in length"]` | 1-128 字符 |
| Public Key | ✅ | `input[placeholder="Please public Key is required."]` | 完整公钥文本 |

弹窗按钮：Cancel、Import

## 测试用例

### TC-K001: 创建 Key Pair

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-K002: 导入 Key Pair

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-K003: 删除 Key Pair

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
