# 原子操作统一模板

所有可沉淀为操作库的页面动作都必须使用本模板。未补齐模板前，只能放入
`待迁移操作`，不能标记为 `ready-template` 或 `ready-validated`。
补齐模板但尚未真实跑通的操作标记为 `ready-template`；通过真实 EasyStack
Web UI 用例验证后才能标记为 `ready-validated`。

## `<operation_name>`

### 用途

说明该操作解决什么资源动作，是否创建、修改、删除或绑定资源。

### 参数

- 必填参数：列出必须由调用方提供的字段
- 环境默认参数：列出从 `/tmp/easystack-env.json` 读取的字段
- 显式可选参数：列出调用方可覆盖的字段

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用 `agent-browser` 会话
- 目标资源、配额或页面入口满足操作要求

### 成功判定

- 必须写清可观测的成功状态
- 不能只以“按钮点击完成”作为成功

### 执行步骤概览

- 打开目标页面并确认未跳回登录页
- 定位目标资源或打开创建/编辑入口
- 填写表单或选择目标项
- 提交操作
- 轮询或验证目标状态

### 失败信号

- 缺少必填参数
- 页面跳回登录页
- 目标资源不可见或无法选择
- 提交后状态未达到预期
- 轮询超时

### 返回值约定

```json
{
  "ok": true,
  "resource": "<resource>",
  "action": "<action>",
  "name": "<resource-name>",
  "status": "<observed-status>",
  "message": "<short result>",
  "url": "<current-url>"
}
```

### `agent-browser eval --stdin` 示例

```bash
agent-browser eval --stdin <<'JS'
const result = {
  ok: true,
  resource: '<resource>',
  action: '<action>',
  name: '<resource-name>',
  status: '<observed-status>',
  message: '<message>',
  url: location.href
};
result;
JS
```
