---
name: windows-mcp-operation
description: "Use when the user asks to operate a real Windows desktop via the windows-mcp server: screenshots, window control, mouse/keyboard, PowerShell, file/registry/process management, and toast notifications. Loads this skill before Windows MCP tool calls so the correct interface is chosen and known failure modes are avoided."
---

# Windows MCP

通过 windows-mcp server 操作和观察真实 Windows 桌面，包括截屏、窗口控制、鼠标键盘操作、系统管理等。

## Quick Decision

| 场景 | 首选工具 | 备注 |
|------|----------|------|
| 查看桌面 / 截屏 | `Snapshot` | 需 UI 元素坐标时加 `use_ui_tree: true` |
| 快速纯截图 | `Screenshot` | 无 UI 树，速度更快 |
| 启动应用 | `App` mode=launch | 需开始菜单中的完整名称 |
| 切换窗口 | `App` mode=switch | 支持部分名称匹配 |
| 调整窗口大小/位置 | `App` mode=resize | 省略 name 则操作活动窗口 |
| 鼠标点击 | `Click` | clicks=0 悬停, 1 单击, 2 双击 |
| 鼠标移动/拖拽 | `Move` | drag=true 执行拖拽 |
| 滚动 | `Scroll` | 支持垂直和水平 |
| 文本输入 | `Type` | 必须提供 loc 或 label(整数 ID) |
| 快捷键 | `Shortcut` | 如 ctrl+c, alt+tab, win+r |
| 批量填表 | `MultiEdit` | labels 或 locs 模式 |
| 等待 UI 就绪 | `WaitFor` | 支持 text/element/window 条件 |
| 固定等待 | `Wait` | 秒级暂停 |
| 执行命令/脚本 | `PowerShell` | Status Code 始终为 0，需检查输出 |
| 进程查看/终止 | `Process` | mode=list / mode=kill |
| 文件操作 | `FileSystem` | read/write/copy/move/delete/list/search/info |
| 注册表 | `Registry` | get/set/delete/list |
| 剪贴板 | `Clipboard` | mode=get / mode=set |
| Toast 通知 | `Notification` | 需要 app_id, title, message |
| 多选 UI 元素 | `MultiSelect` | 支持 press_ctrl |
| 抓取网页 | `Scrape` | 可选 DOM 模式 |

## Quick Reference - File Index

| 当需要... | 阅读 |
|-----------|------|
| Snapshot / Screenshot / Scrape 工具详情 | [observation.md](reference/observation.md) |
| App 窗口控制详情 | [window.md](reference/window.md) |
| Click / Move / Scroll / MultiSelect 鼠标操作 | [mouse.md](reference/mouse.md) |
| Type / Shortcut / Clipboard 键盘和剪贴板 | [keyboard.md](reference/keyboard.md) |
| Wait / WaitFor 等待条件 | [wait.md](reference/wait.md) |
| MultiEdit / Notification 填表和通知 | [form.md](reference/form.md) |
| PowerShell / Process / FileSystem / Registry 系统工具 | [system.md](reference/system.md) |
| 推荐工作流(启动应用、填表、键盘操作等) | [workflows.md](reference/workflows.md) |
| 安全规则和接口注意事项 | [safety.md](reference/safety.md) |

## When NOT to Use This Skill

- 浏览器内操作(导航、填表、点击网页元素)→ 用 Playwright MCP
- 纯命令行 / shell 操作 → 直接用 Bash
- 不需要与 Windows 桌面交互的任何任务
- 判断标准:是否需要操作真实的 Windows 窗口、图标、桌面应用

## Key Reminders

- 操作前先 `Snapshot` 确认桌面状态
- `Type` / `Move` / `Click` 的 `label` 必须为整数 ID，非字符串
- `PowerShell` 返回的 Status Code 始终为 0，需检查输出内容
- `App` launch 需要完整应用名(由 `Snapshot` UI 树获取)
- 截图功能需安装 `mss`:`uv tool install windows-mcp --with mss --force`
- 远程桌面中窗口枚举可能不稳定，优先使用 UI 树替代
