# start_stop_reboot_instance

> 来源：`patterns/instance-ops.md`，按原子操作拆分。

## `start_stop_reboot_instance`

### 用途

对实例执行启动、关机或重启，并验证实例状态达到预期。

### 参数

- 必填参数: `name`
- 必填参数: `action`，可选值为 `start`、`stop`、`reboot`
- 显式可选参数: `target_status`

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### 成功判定

- 操作提交成功
- 实例状态达到 `target_status`；未显式传入时，`start` 对应 `Active`，`stop` 对应 `Shutoff`，`reboot` 对应 `Active`

### 执行步骤概览

- 打开实例列表页并确认未跳回登录页
- 选中目标实例
- 点击对应操作按钮或 More 菜单项
- 处理确认弹窗
- 轮询实例列表直到目标状态出现

### 操作注意事项

- 实例列表可能先渲染导航和标题，表格稍后才出现；必须等目标实例名称在
  `document.body.innerText` 或 snapshot 中可见后再解析 refs。
- 行复选框优先使用 `agent-browser snapshot` 中目标行的 `LabelText [ref=...]`
  做真实点击；单纯 DOM `.click()` 可能不会触发 ng-zorro 表格选择状态。
- 点击 `Start` 后确认弹窗里的主按钮文本仍为 `Start`，不是 `Confirm`；点击时
  必须限定在弹窗内或使用弹窗里的最后一个 `Start` ref。
- 如果选中后目标动作按钮仍 disabled，重新获取 snapshot；不要继续空轮询状态，
  因为操作可能根本没有提交。

### 失败信号

- 缺少实例名、动作或平台地址
- 动作不在允许列表中
- 页面跳回登录页
- 目标实例不可见
- 操作入口不可见或状态轮询超时

### 返回值约定

```json
{"ok":true,"resource":"instance","action":"reboot","name":"<instance-name>","status":"Active","message":"instance action completed","url":"<current-url>"}
```

### `agent-browser eval --stdin` 示例

```js
const input = { name: '<instance-name>', action: 'reboot' };
const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
const row = [...document.querySelectorAll('tr')].find((item) => text(item).includes(input.name));
if (!row) {
  ({ ok: false, resource: 'instance', action: input.action, name: input.name, status: 'missing', message: 'instance not found', url: location.href });
} else {
  row.querySelector('label.ant-checkbox-wrapper, label, input[type="checkbox"]')?.click();
  const direct = [...document.querySelectorAll('button')].find((btn) => new RegExp(input.action, 'i').test(text(btn)) && !btn.disabled);
  direct?.click();
  ({ ok: true, resource: 'instance', action: input.action, name: input.name, status: direct ? 'submitted_or_confirm_needed' : 'selected', message: 'use direct button or More menu, confirm dialog, then poll instance status', url: location.href });
}
```
