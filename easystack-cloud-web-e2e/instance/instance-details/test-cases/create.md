# 创建类测试用例

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识；执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

> 来源：`easystack-cloud-web-e2e/instance/instance-details/test-cases.md`，按测试用例边界拆分。

# 实例测试用例

> 来源：`easystack-cloud-web-e2e/instance/instance.md`，按原文标题边界拆分。

## 测试用例

### TC-I001: 创建云主机（已验证可用）

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-I002: 创建带数据盘的云主机

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-I003: 挂载云硬盘到云主机

```text
agent-browser 执行说明：
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
