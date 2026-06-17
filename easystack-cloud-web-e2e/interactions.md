# UI 组件交互

EasyStack Cloud 使用 Angular + NG-ZORRO 组件库。本文件只记录可嵌入
`agent-browser` 的定位方式和交互模式。

## 使用约定

- 示例均为 `agent-browser` CLI 或可放入 `agent-browser eval --stdin` 的定位方式知识。
- 优先合并为单次 `agent-browser eval --stdin` 或 `agent-browser batch`，减少 snapshot 和 token 消耗。
- 固定等待只作为动画兜底；成功判定应依赖 URL、目标元素或状态文本。
- 业务操作优先复用 `patterns/*-ops.md`，本文件只提供组件级 helper。
- `agent-browser` 不是 Playwright，不能直接使用 `:has-text()`、`text=` 等
  Playwright 风格伪选择器。CLI 文本定位使用 `agent-browser find text ...`；
  `eval --stdin` 内使用下方 helper。

## 按钮

```bash
agent-browser find text "Create Volume" click
agent-browser click 'button.ant-btn-primary'
agent-browser is enabled 'button.ant-btn-primary'
```

`agent-browser eval --stdin` 中按文本定位元素：

```javascript
const textOf = (node) => (node?.innerText || node?.textContent || '')
  .trim().replace(/\s+/g, ' ');
const byText = (selector, value, root = document) => {
  const nodes = [...root.querySelectorAll(selector)];
  return nodes.find((node) => textOf(node) === value) ||
    nodes.find((node) => textOf(node).includes(value));
};
const buttonByText = (value, root = document) => byText('button', value, root);
const formItemByLabel = (label, root = document) =>
  [...root.querySelectorAll('.ant-form-item')]
    .find((node) => textOf(node).includes(label));
const fieldInput = (label, selector = 'input, textarea', root = document) =>
  formItemByLabel(label, root)?.querySelector(selector);
```

列表页按钮在页面刚打开后可能先渲染为 `disabled`，随后由权限、配额或数据
加载结果异步放开。例如实例列表的 `Create Instance` 按钮可能需要等待数秒
才可点击。执行操作前必须轮询目标按钮进入 enabled 状态，不能仅凭首次
探测到 disabled 就判定无权限或配额不足。

```bash
agent-browser wait --fn "Array.from(document.querySelectorAll('button')).some((b) => b.innerText.trim() === 'Create Instance' && !b.disabled)"
```

`agent-browser eval --stdin` 中推荐使用通用等待：

```javascript
const waitButtonEnabledOnce = (text) => {
  const button = [...document.querySelectorAll('button')]
    .find((item) => item.innerText.trim() === text);
  return Boolean(button && !button.disabled);
};
```

长等待不要放进单次 `eval`，否则容易触发 CDP evaluate 超时。需要等待超过
数秒时，优先使用 `agent-browser wait --fn`，或在 shell 层做短轮询：

```bash
for i in $(seq 1 30); do
  agent-browser eval --stdin <<'JS' | grep '"enabled": true' && break
(() => {
  const button = [...document.querySelectorAll('button')]
    .find((item) => item.innerText.trim() === 'Create Instance');
  return { enabled: Boolean(button && !button.disabled) };
})()
JS
  sleep 1
done
```

如果必须在页面上下文中短等待，控制在几秒内：

```javascript
const waitButtonEnabledBriefly = async (text, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const found = [...document.querySelectorAll('button')]
      .find((button) => button.innerText.trim() === text);
    if (found && !found.disabled) return true;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  return false;
};
```

| 按钮类型 | 定位方式 | 说明 |
|----------|--------|------|
| 主要按钮 | `button.ant-btn-primary` | 主题色按钮 |
| 次要按钮 | `button.ant-btn-default` | 默认按钮 |
| 危险按钮 | `button.ant-btn-dangerous` | 危险操作按钮 |
| 禁用按钮 | `button.ant-btn[disabled]` | 禁用状态 |

## 文本输入

```bash
agent-browser fill '#id_username' "$USERNAME"
agent-browser fill 'input[placeholder="Enter 1 to 128 characters in length"]' "$NAME"
agent-browser fill 'textarea[placeholder*="description"]' "$DESCRIPTION"
```

按表单标签填写时使用 `eval --stdin`：

```bash
agent-browser eval --stdin <<'JS'
const value = '<volume-name>';
const textOf = (node) => (node?.innerText || node?.textContent || '').trim();
const item = [...document.querySelectorAll('.ant-form-item')]
  .find((node) => textOf(node).includes('Volume Name'));
const input = item?.querySelector('input, textarea');
if (input) {
  input.value = value;
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
}
Boolean(input);
JS
```

## 下拉选择框

NG-ZORRO Select 不是原生 `<select>`。优先点击当前可见下拉，再从未隐藏的
dropdown 中选项。

```javascript
const selectOption = (formItemText, optionText) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const formItem = [...document.querySelectorAll('.ant-form-item')]
    .find((item) => text(item).includes(formItemText));
  formItem?.querySelector('.ant-select, nz-select')?.click();
  setTimeout(() => {
    [...document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')]
      .find((item) => text(item).includes(optionText))?.click();
  }, 300);
};
```

获取当前值：

```javascript
const selectedText = document
  .querySelector('.ant-form-item .ant-select-selection-item')
  ?.textContent?.trim();
```

搜索并选择：

```javascript
const searchAndSelect = (formItemText, searchText, optionText) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const formItem = [...document.querySelectorAll('.ant-form-item')]
    .find((item) => text(item).includes(formItemText));
  formItem?.querySelector('.ant-select, nz-select')?.click();
  const search = document.querySelector('.ant-select-dropdown:not(.ant-select-dropdown-hidden) input');
  if (search) {
    search.value = searchText;
    search.dispatchEvent(new Event('input', { bubbles: true }));
  }
  setTimeout(() => {
    [...document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')]
      .find((item) => text(item).includes(optionText))?.click();
  }, 300);
};
```

## 弹窗

```javascript
const modal = document.querySelector('.ant-modal');
const title = modal?.querySelector('.ant-modal-title')?.textContent?.trim();
[...document.querySelectorAll('.ant-modal button')]
  .find((button) => /Confirm|OK|Create|Associate/i.test(button.innerText) && !button.disabled)
  ?.click();
```

填写弹窗表单：

```javascript
const fillModalField = (label, value) => {
  const text = (e) => (e.innerText || e.textContent || '').trim();
  const item = [...document.querySelectorAll('.ant-modal .ant-form-item')]
    .find((node) => text(node).includes(label));
  const input = item?.querySelector('input, textarea');
  if (!input) return false;
  input.value = String(value);
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
  return true;
};
```

## 表格

定位包含指定文本的行：

```javascript
const rowByText = (value) => [...document.querySelectorAll('.ant-table-tbody tr')]
  .find((row) => row.innerText.includes(value));
```

选中行：

```javascript
rowByText('<name>')?.querySelector('input[type="checkbox"], .ant-checkbox-input')?.click();
```

读取行状态：

```javascript
const rowText = rowByText('<name>')?.innerText || '';
const reached = rowText.includes('<target-status>');
```

搜索表格：

```javascript
const search = document.querySelector('.ant-input-search input, input[placeholder*="Search"]');
search.value = '<keyword>';
search.dispatchEvent(new Event('input', { bubbles: true }));
search.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
```

## 数字输入框

NG-ZORRO 数字输入框有时需要触发 `input` 和 `change` 事件。

```javascript
const setNumberInput = (selector, value) => {
  const input = document.querySelector(selector);
  if (!input) return false;
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, String(value));
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new Event('blur', { bubbles: true }));
  return true;
};
```

## 标签页

```javascript
const tab = [...document.querySelectorAll('.ant-tabs-tab')]
  .find((item) => item.innerText.includes('<tab-name>'));
tab?.click();
```

## 消息与通知

```javascript
const success = document.querySelector('.ant-message-success, .ant-notification-notice-success');
Boolean(success);
```

清理遮挡通知：

```javascript
document.querySelectorAll('.ant-notification-notice').forEach((node) => node.remove());
```

## 确认对话框

```javascript
document.querySelector('.ant-modal-confirm-btns .ant-btn-primary')?.click();
```

## 加载状态

```javascript
const loading = document.querySelector('.ant-spin-spinning');
Boolean(!loading);
```

## 截图

```javascript
agent-browser screenshot "/tmp/easystack-screenshots/<case-name>/result.png"
```
