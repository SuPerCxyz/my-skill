# 推荐工作流

## 获取桌面状态

1. 调用 `Snapshot` `{"use_vision": true}`
2. 总结可见窗口和应用状态
3. 若需 UI 元素坐标，改用 `Snapshot` `{"use_ui_tree": true}`
4. 降级（截屏偶发失败时）：
   - `Snapshot` `{"use_ui_tree": true, "use_vision": false}` — 仅 UI 树
   - `PowerShell` 获取窗口列表作为最终降级

## 启动并操作应用

1. `App` `mode=launch` 启动目标应用
2. `Wait` 等待启动（2-3 秒）
3. `WaitFor` `text_exists` 等待应用标题出现
4. `App` `mode=resize` 调整到合适大小
5. `Snapshot` 确认状态
6. `Click` / `Type` / `Shortcut` 执行操作

## 填写 Windows 表单

1. `Snapshot` `{"use_ui_tree": true}` 获取字段标签和坐标
2. 优先 `MultiEdit` `labels` 模式
3. 标签不可用时用 `Type` + 坐标
4. `Shortcut` `ctrl+s` 或 `Click` 保存按钮

## 关闭应用

`App` 无 close 模式，使用：
- `PowerShell`：`Stop-Process -Name <process_name> -Force`
- 或 `Shortcut` `alt+F4`

## 键盘驱动操作

1. `App` `mode=switch` 切换目标窗口
2. `Shortcut` 使用快捷键（`alt+F` 打开菜单等）
3. `Type` 输入文本 + `press_enter`
4. `Wait` / `WaitFor` 等待响应
