# 安全与回滚

## 校验策略

- 默认记录 `size` + `mtime`
- mapping 中使用 `hash_type` + `hash` 字段，不固定使用 sha256
- `hash_type` 取值:`none` / `quick_hash` / `sha256`
- 小于 1GB 的文件可计算完整 sha256(`hash_type=sha256`)
- 大于 1GB 的文件默认使用 quick_hash，读取文件头尾各 64MB(`hash_type=quick_hash`)
- 用户设置 `full_hash=true` 时统一使用 sha256
- 如果只记录 size + mtime:`hash_type=none`, `hash=null`

## 回滚要求

- 所有 rename / move 操作必须先写入 `_rename_mapping.json`
- JSON 中记录 `old_path`、`new_path`、`hash_type`、`hash`、`size`、`mtime`、`operation`、`timestamp`
- 回滚脚本默认只回滚 rename / move，不删除用户新增文件
- 如果目标路径已经被其他文件占用，回滚中止并提示人工处理
- 回滚脚本必须支持 dry-run

## `_rename_mapping.json` 格式

```json
{
  "timestamp": "2026-06-15T18:00:00",
  "source": "/data/media/video/综艺/原始目录",
  "files": [
    {
      "old": "/data/media/video/综艺/原始目录/old_name.mp4",
      "new": "/data/media/video/综艺/新目录/Season-01/新名称.mp4",
      "hash_type": "quick_hash",
      "hash": "abc123...",
      "size": 1234567890,
      "mtime": "2026-06-15T12:00:00",
      "operation": "rename"
    }
  ]
}
```

## 冲突处理策略

- 目标路径已存在时禁止覆盖
- 自动生成冲突报告
- 可选策略:
  1. `skip`:跳过(默认)
  2. `suffix`:追加 `-dup1` / `-dup2`
  3. `replace`:只有用户明确确认后才允许覆盖

## 附属文件备份规则

- 已存在的 NFO 不允许直接覆盖
- 已存在的 `poster.jpg` / `fanart.jpg` / `banner.jpg` / `clearlogo.png` 不允许直接覆盖
- 如果需要生成同名文件，默认跳过
- 如果用户明确允许 `replace`，则覆盖前必须先备份
- 备份目录为 `_backup_before_rename_{timestamp}`
- 备份文件路径必须写入 `_rename_mapping.json`
- 回滚时只恢复本次备份的文件，不删除用户后来新增的文件

## 路径安全规则

- 禁止处理系统根目录 `/`
- 禁止处理用户 home 根目录
- 禁止处理 `/bin`、`/etc`、`/usr`、`/var`、`/boot`、`/dev`、`/proc`、`/sys`
- 禁止跟随符号链接到输入路径之外
- 所有目标路径必须位于用户指定的媒体库根目录或 staging 目录内
- 对所有路径执行 `realpath` 校验，避免 `../` 路径逃逸
- 删除空目录前必须确认该目录内没有非本次处理文件
