# Decompression

Use this file only when the input is a `.eslog` bundle. If the user already provides an
extracted `ecs.*` directory, skip to [directory-map.md](directory-map.md) and
[analysis-playbook.md](analysis-playbook.md).

## Input Selection 输入选择

- 用户指定 `.eslog` 文件或目录时, 通过 `--input` 原样传入。
- 用户未指定路径时, `--input` 默认使用当前工作目录。
- 输入目录只匹配顶层 `*.eslog`, 不递归扫描其他位置。
- `--output` 默认使用当前工作目录; 建议显式指定独立输出目录。
- 同名 `ecs.*` 输出已存在时直接合并: 同路径文件使用本次内容覆盖, 新文件追加,
  本次 bundle 未包含的旧文件保留。新 bundle 可能包含更完整的日志, 不因旧结果
  存在而跳过解压。

## Safe Script 安全脚本

使用仓库内置脚本, 不要从文档复制临时脚本:

```bash
# One explicit bundle
bash scripts/decompress-eslog.sh \
  --input /path/to/ecs.example.eslog \
  --output /path/to/output

# All top-level .eslog files in the current directory
bash scripts/decompress-eslog.sh

# Expand .log.gz only after confirming sufficient disk space
bash scripts/decompress-eslog.sh --decompress-logs
```

脚本行为:

- 内层 ZIP 默认暂存在 `/var/tmp` 的权限隔离临时目录, 避免与大体积输出共同占用
  `/tmp`; 设置 `TMPDIR` 时使用该目录。目标不可用时才回退到输出目录。
- 退出时清理内层 ZIP 临时目录。
- 外层 bundle 一次只处理一个内层归档, tar 通过管道校验和解包, 不保留 tar 副本。
- 解包前校验 tar 成员路径, 拒绝绝对路径、`..` 路径逃逸及非 `ecs.*` 顶层目录。
- 直接向同名 `ecs.*` 目录增量覆盖, 避免为旧结果创建完整副本而耗尽磁盘配额。
- 解包失败时停止并报告已处理范围; 已覆盖文件不自动回滚。修复空间或归档问题后可
  使用同一命令再次解压, 让完整 bundle 补齐结果。
- 默认保留原始 `.eslog` 和 `.log.gz`, 不批量展开日志, 避免大 bundle 耗尽磁盘配额。
- 只有显式传入 `--decompress-logs` 时才用 `gzip -dkf` 生成或更新 `.log`。
- 默认密码来自 `ESLOG_PASSWORD`, 未设置时使用 EasyStack 默认值。

如果缺少 `unzip`、`tar`、`gzip` 等依赖, 先报告缺失命令和建议安装命令, 获得用户
确认后再安装。不要自动修改系统依赖。

## Output Layout 输出结构

```text
ecs.<hostname>.<date>.<N>/
|-- alcubierre/
|-- ceph/
|-- ceph-k8s/
|-- cloud-products/
|-- ecas/
|-- ecms/
|-- ems/
|-- kubernetes/
|-- libvirt/
|-- openstack/
|-- os/
`-- others/
```

解压完成后先根据 bundle 文件名和日志 wrapper timestamp 确认覆盖时间窗, 再进入定向
检索。若同一 bundle 已有对应的 `ecs.*` 目录, 优先使用已解压目录, 不重复解压。
