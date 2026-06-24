# 云硬盘测试用例

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

> 来源:`easystack-cloud-web-e2e/volume/volume.md`，按原文标题边界拆分。

> 说明:本文件保留页面步骤和断言知识作为页面知识库。
> 新的可复用原子操作请优先参考 `../../patterns/volume-ops.md`。

## 测试用例

### TC-001: 创建空白云硬盘

**前置条件:** 已登录 EasyStack Cloud 平台

**步骤:**
1. 导航到云硬盘页面
2. 点击 "Create Volume" 按钮
3. 填写 Volume Name
4. 选择 Volume Source 为 "Empty Volume"
5. 选择 Type 为 "hdd"
6. 设置 Size
7. 点击 "Create" 按钮
8. 验证创建成功

**代码:**

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-002: 创建从镜像来源的云硬盘

**步骤:**
1. 导航到云硬盘页面
2. 点击 "Create Volume" 按钮
3. 填写 Volume Name
4. 选择 Volume Source 为 "Image"
5. 选择具体的镜像
6. 设置 Size
7. 点击 "Create" 按钮

**代码:**

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-003: 创建从快照来源的云硬盘

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-004: 创建云硬盘 - 验证表单校验

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
