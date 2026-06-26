# Windows MCP Operation

通过 windows-mcp server 操作和观察真实 Windows 桌面:截屏、窗口控制、鼠标键盘、系统管理、PowerShell、文件 / 注册表 / 进程、Toast 通知等。范围限定为真实 Windows 桌面与系统工具交互, 不覆盖普通网页自动化或特定平台专用工作流。

## 功能

- 桌面观察:Snapshot(带 UI 树)/ Screenshot(快速)/ Scrape
- 窗口控制:App launch / switch / resize
- 鼠标键盘:Click / Move / Scroll / MultiSelect / Type / Shortcut / Clipboard
- 等待:Wait / WaitFor(text/element/window 条件)
- 系统:PowerShell / Process / FileSystem / Registry / Notification

## 快速开始

```
1. 操作前先 Snapshot 确认桌面状态
2. 按场景从 Quick Decision 表选工具(详见 SKILL.md)
3. 浏览器内网页操作请改用 Playwright MCP，本 skill 仅用于真实 Windows 桌面
```

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，Quick Decision 工具选型表与 Key Reminders |
| [reference/observation.md](reference/observation.md) | Snapshot / Screenshot / Scrape 详情 |
| [reference/window.md](reference/window.md) | App 窗口控制详情 |
| [reference/mouse.md](reference/mouse.md) | Click / Move / Scroll / MultiSelect 鼠标操作 |
| [reference/keyboard.md](reference/keyboard.md) | Type / Shortcut / Clipboard 键盘与剪贴板 |
| [reference/wait.md](reference/wait.md) | Wait / WaitFor 等待条件 |
| [reference/form.md](reference/form.md) | MultiEdit / Notification 填表与通知 |
| [reference/system.md](reference/system.md) | PowerShell / Process / FileSystem / Registry 系统工具 |
| [reference/workflows.md](reference/workflows.md) | 推荐工作流(启动应用、填表、键盘操作等) |
| [reference/safety.md](reference/safety.md) | 安全规则与接口注意事项 |
| [agents/openai.yaml](agents/openai.yaml) | 配套 opencode agent 配置(display name、默认 prompt) |
