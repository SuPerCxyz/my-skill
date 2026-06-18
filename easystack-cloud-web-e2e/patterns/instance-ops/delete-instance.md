# delete_instance

> 来源：`patterns/instance-ops.md`，按原子操作拆分。

## `delete_instance`

### 用途

删除一台实例，并验证该实例已从当前实例列表中消失。

### 参数

- 必填参数: `name`
- 环境默认参数: 无
- 显式可选参数: `confirm_text`，用于少数二次确认场景

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### 成功判定

- 已触发删除确认
- 刷新列表后不再找到目标实例

### 操作注意

- 行选择优先点击可见 checkbox wrapper，不要默认只点隐藏 input。
- 删除弹窗可能是双确认 footer；第一层删除后必须重新获取当前 modal，再处理
  第二层 `Confirm`。
- 确认按钮只允许在当前最上层 modal 内定位。

### 执行步骤概览

- 打开实例列表页并确认当前会话仍处于已登录状态
- 在列表中定位并选中目标实例
- 通过更多操作触发删除并完成确认
- 刷新实例列表，直到目标实例从列表中消失

### 失败信号

- 缺少实例名称或平台地址等必填输入
- 页面跳转到登录页，说明当前会话失效
- 实例列表中找不到目标实例，或删除确认流程未成功触发
- 多次刷新后目标实例仍然可见

### 返回值约定

```json
{
  "ok": true,
  "resource": "instance",
  "action": "delete",
  "name": "<instance-name>",
  "status": "deleted",
  "message": "instance removed from list",
  "url": "<current-url>"
}
```

### `agent-browser eval --stdin` 示例

```js
const input = { name: '<instance-name>' };
const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
const row = [...document.querySelectorAll('tr')].find((item) => text(item).includes(input.name));
if (!row) {
  ({ ok: false, resource: 'instance', action: 'delete', name: input.name, status: 'missing', message: 'instance not found', url: location.href });
} else {
  row.querySelector('label.ant-checkbox-wrapper, .ant-checkbox-wrapper, label, input[type="checkbox"]')
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  [...document.querySelectorAll('button')].find((btn) => text(btn) === 'More' && !btn.disabled)
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  ({ ok: true, resource: 'instance', action: 'delete', name: input.name, status: 'menu_opened', message: 'click Delete, confirm dialog, then poll /eec/instances until row disappears', url: location.href });
}
```
