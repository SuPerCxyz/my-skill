# create_instance_snapshot

> 来源:`patterns/instance-ops.md`，按原子操作拆分。

## `create_instance_snapshot`

### 用途

从实例创建快照，并验证快照列表中出现目标快照。

### 参数

- 必填参数: `instance`
- 必填参数: `snapshot_name`

### 前置条件

- `/tmp/easystack-env.json` 中至少存在 `platform.url`
- 调用前已按 `patterns/login.md` 准备可复用会话
- 目标实例当前出现在实例列表中

### 成功判定

- 创建快照请求已提交
- 实例快照列表中出现 `snapshot_name`

### 操作注意

- 行选择优先点击可见 checkbox wrapper，不要默认只点隐藏 input。
- 提交时必须限定在 `Create Snapshot` 弹窗内;如果弹窗内存在 form，优先提交
  form。

### 执行步骤概览

- 打开实例列表页并确认未跳回登录页
- 选中目标实例
- 通过 More / Create Snapshot 打开弹窗
- 填写快照名称并提交
- 打开实例快照列表并轮询目标快照

### 失败信号

- 缺少实例名、快照名或平台地址
- 页面跳回登录页
- 目标实例不可见
- 创建快照入口或名称输入框不可见
- 轮询超时后快照仍未出现

### 返回值约定

```json
{"ok":true,"terminal":true,"submitted":true,"resource":"instance_snapshot","action":"create","name":"<snapshot-name>","status":"created","message":"instance snapshot created","url":"<current-url>"}
```

### `agent-browser eval --stdin` 示例

```js
const input = { instance: '<instance-name>', snapshotName: '<snapshot-name>' };
const text = (e) => (e.innerText || e.textContent || e.value || '').trim().replace(/\s+/g, ' ');
const row = [...document.querySelectorAll('tr')].find((item) => text(item).includes(input.instance));
if (!row) {
  ({ ok: false, terminal: true, submitted: false, resource: 'instance_snapshot', action: 'create', name: input.snapshotName, status: 'missing_instance', message: 'instance not found', url: location.href });
} else {
  row.querySelector('label.ant-checkbox-wrapper, .ant-checkbox-wrapper, label, input[type="checkbox"]')
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  [...document.querySelectorAll('button')].find((btn) => text(btn) === 'More' && !btn.disabled)
    ?.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
  ({ ok: null, terminal: false, submitted: false, resource: 'instance_snapshot', action: 'create', name: input.snapshotName, status: 'menu_opened', message: 'click Create Snapshot, fill name, submit, then poll /eec/instance-snapshots', url: location.href });
}
```
