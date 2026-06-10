# GUI 测试精简规则

## 硬规则

1. **snapshot 优先于 screenshot**
   - 使用 accessibility snapshot（如 Playwright `browser_snapshot`）代替截图
   - snapshot 返回结构化文本，比图片省 token
   - 仅在需要视觉验证时才用 screenshot

2. **禁止全页截图反复迭代**
   - 禁止 `fullPage: true` 截图后反复分析
   - 截图必须指定 `element` 参数，只截目标区域
   - 单轮交互最多 2 次截图

3. **定向元素交互**
   - 用 snapshot 返回的元素引用直接交互，不靠坐标猜测
   - 表单填写用 `browser_fill_form` 批量填写，不逐个点击
   - 等待用 `browser_wait_for`（文本出现/消失），不用固定 sleep

4. **状态检查精简**
   - 验证页面状态用 snapshot + 文本断言，不截图对比
   - 多步骤测试只截图关键节点（提交前后、结果页），不每步都截
   - 控制台日志用 `browser_console_messages` 取 error 级别

## 常用安全流程模板

```bash
# 1. 获取页面结构（代替截图）
browser_snapshot()

# 2. 定向交互
browser_click(target="element_ref_from_snapshot")
browser_type(target="input_ref", text="value")

# 3. 等待状态变化（不用 sleep）
browser_wait_for(text="Success")

# 4. 只在关键节点截图
browser_take_screenshot(element="result_area", type="png")

# 5. 检查控制台错误
browser_console_messages(level="error")
```

## 测试流程精简

```
1. 导航到目标页面
   └─ browser_navigate(url)

2. 获取 snapshot（不截图）
   └─ browser_snapshot()

3. 根据 snapshot 元素引用执行交互
   └─ browser_click / browser_type / browser_fill_form

4. 等待预期结果出现
   └─ browser_wait_for(text="expected text")

5. 仅截图关键结果区域
   └─ browser_take_screenshot(element="specific_element")
```

## 禁止清单

| 禁止操作 | 替代方案 |
|----------|----------|
| `browser_take_screenshot(fullPage=true)` | 截图指定 element |
| 每步操作都截图 | 只在关键节点截图 |
| `browser_snapshot()` 后再次全量 snapshot | 用 target 参数定向 snapshot |
| 固定 `sleep(5)` 等待 | `browser_wait_for(text=...)` |
| 截图后用视觉分析找元素 | 用 snapshot 返回的结构化引用 |
| `browser_console_messages(all=true)` | `browser_console_messages(level="error")` |
