# 系统工具

## PowerShell

执行任意 PowerShell 命令。

### 典型调用

```json
{"command": "Get-Process | Select-Object -First 5", "timeout": 15}
```

### PowerShell 注意事项

- **Status Code 始终为 0**(反映 shell 调用本身，非内部命令结果)，需检查输出内容判断命令是否真正成功
- 超时默认 30s，可调
- 可用于 Snapshot 失败时获取窗口列表作为降级方案:

```powershell
Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object Id, ProcessName, MainWindowTitle | Format-Table -AutoSize
```

## Process

查看或终止进程。

| mode | 用途 | 关键参数 |
|------|------|----------|
| `list` | 列出进程 | `limit`(默认20), `sort_by`(`cpu`/`memory`/`name`) |
| `kill` | 终止进程 | `name` 或 `pid`, `force` |

```json
{"mode": "list", "limit": 10, "sort_by": "cpu"}
{"mode": "kill", "name": "notepad"}
```

### Process 安全规则

- kill 非用户启动的进程时需确认
- kill 用 `name` 可能匹配失败，用 `pid` 更可靠

## FileSystem

文件和目录操作。路径相对于用户 Desktop 目录，`"."` 表示 Desktop 本身。

| mode | 用途 | 关键参数 |
|------|------|----------|
| `read` | 读文件 | `encoding`(默认 utf-8), `offset`, `limit` |
| `write` | 写/追加 | `content`(必填), `append`, `overwrite` |
| `copy` | 复制 | `destination` |
| `move` | 移动/重命名 | `destination` |
| `delete` | 删除 | `recursive` |
| `list` | 列目录 | `pattern`, `show_hidden` |
| `search` | 搜索文件 | `pattern`(glob) |
| `info` | 文件元数据 | — |

### FileSystem 注意事项

- 绝对路径可访问非 Desktop 位置
- UTF-16 文件需指定 `encoding: "utf-16"`(默认 utf-8 会乱码)
- `overwrite=false` 不阻止覆盖(仍会覆盖)
- `write` 必须提供 `content` 参数
- `delete` 非临时文件时需确认

## Registry

读写 Windows 注册表。

| mode | 用途 |
|------|------|
| `get` | 读取特定值(需 `name`) |
| `set` | 创建/修改值 |
| `delete` | 删除值或键 |
| `list` | 列出值和子键 |

路径格式:`HKCU:\Software\...` 或 `HKLM:\SOFTWARE\...`

```json
{"mode": "list", "path": "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer"}
{"mode": "get", "path": "HKCU:\\...\\Explorer", "name": "LogonCount"}
```

### Registry 安全规则

- `get` / `list` 安全可自由使用
- `set` / `delete` 需用户确认
