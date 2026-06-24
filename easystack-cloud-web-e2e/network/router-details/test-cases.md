# 路由器测试用例

## agent-browser 迁移说明

本文件保留页面字段、步骤和断言知识;执行入口统一迁移到 agent-browser。
文中的历史代码块已替换为 agent-browser 迁移说明，新增用例必须使用 `agent-browser eval --stdin` 或 `agent-browser batch` 示例。

> 来源:`easystack-cloud-web-e2e/network/router.md`，按原文标题边界拆分。

## 分页

| 项目 | 值 |
|------|-----|
| 默认每页 | 10 条 |
| 每页定位方式 | 下拉，"10 / page" |
| 总数显示 | "Total N items, last updated [timestamp]" |
| 翻页 | 上一页/下一页、页码按钮 |

## 测试用例

### TC-RT001: 验证路由器页面加载

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RT002: Create Router 页面验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RT003: 按名称过滤路由器

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```

### TC-RT004: 行内操作验证

```text
agent-browser 执行说明:
- 当前 skill 只维护 agent-browser 执行入口。
- 执行本用例时，先读取 `patterns/login.md` 准备登录态。
- 页面操作优先复用 `patterns/` 下已迁移的原子操作。
- 未迁移的步骤应补充为 `agent-browser eval --stdin` 或 `agent-browser batch` 示例后再执行。
```
