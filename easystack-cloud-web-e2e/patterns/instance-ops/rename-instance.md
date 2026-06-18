# rename_instance

> 来源：`patterns/instance-ops.md`，按原子操作拆分。

## `rename_instance`

### 用途

修改实例名称，并验证实例列表中出现新名称。

### 参数

- 必填参数: `instance`
- 必填参数: `new_name`

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### 成功判定

- 编辑提交完成
- 列表中出现 `new_name`

### 操作注意

- 行选择优先点击可见 checkbox wrapper，不要默认只点隐藏 input。
- 提交时必须限定在编辑弹窗内；如果弹窗内存在 form，优先提交 form。

### 执行步骤概览

- 打开实例列表页并确认未跳回登录页
- 选中目标实例
- 通过 More / Edit 进入编辑弹窗
- 填写新名称并提交
- 轮询实例列表直到新名称出现

### 失败信号

- 缺少实例名、新名称或平台地址
- 页面跳回登录页
- 目标实例不可见
- 编辑入口或名称输入框不可见
- 轮询超时后新名称仍未出现

### 返回值约定

```json
{"ok":true,"resource":"instance","action":"rename","name":"<new-name>","status":"renamed","message":"instance renamed","url":"<current-url>"}
```

### `agent-browser eval --stdin` 示例

```js
const input = { instance: '<old-name>', newName: '<new-name>' };
const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
const row = [...document.querySelectorAll('tr')].find((item) => text(item).includes(input.instance));
if (!row) {
  ({ ok: false, resource: 'instance', action: 'rename', name: input.newName, status: 'missing', message: 'instance not found', url: location.href });
} else {
  row.querySelector('label.ant-checkbox-wrapper, .ant-checkbox-wrapper, label, input[type="checkbox"]')
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  [...document.querySelectorAll('button')].find((btn) => text(btn) === 'More' && !btn.disabled)
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  ({ ok: true, resource: 'instance', action: 'rename', name: input.newName, status: 'menu_opened', message: 'click Edit, fill new name, submit, then poll /eec/instances until new name appears', url: location.href });
}
```
