# Alcubierre Unmap And Via Access

## Goal 目标

扩展 `easystack-env-debugging`, 支持安全批量解除 Alcubierre 云盘 mapping,
并支持先经过一层普通 SSH 跳板机后进入现有三类环境。

## Alcubierre Trigger 触发

当用户给出明确环境、一个或多个 Cinder volume UUID, 并要求“解挂高性能盘”、
“解挂 Alcubierre 盘”或“解除 mapping”时进入专项流程。

仅表达“查看”、“分析”或“可能需要解挂”时只执行预检。即使用户已使用执行性措辞,
也先展示预检结果、影响和回滚限制, 获得一次批量确认后才执行写操作。

## Batch Workflow 批量流程

1. 校验 UUID 格式并去重。
2. 选择 Running、Ready 且没有 `deletionTimestamp` 的 Manul pod。
3. 批次开始时扫描一次 Alcubierre volume 清单, 从同一快照解析每个 UUID 的
   volume、协议和状态; 一次目标化 mapping 批处理读取全部目标盘的 mapping。
4. iSCSI 按唯一 initiator 调用 `disconnections`; NVMe-oF 按唯一 hostnqn 调用
   `nvme_disconnections`。
5. 每个盘执行前 mapping 已为空时作为幂等成功跳过, 不发送 POST。
6. 全部串行 POST 完成后执行一次目标化 mapping 批处理, 再扫描一次 volume 清单,
   统一验证 mapping 为空、volume 为 `unlinked` 且 `error_message` 为空。
7. 中断后原样重跑批次, 已完成对象自动跳过。
8. 第一个 API 写操作失败时停止。API 成功但 mapping 未清空时在批次末尾统一报告,
   不回滚已经完成的对象。

没有 mapping 的对象不论 volume 状态均作为幂等成功跳过。UUID 不存在、协议未知、
存在多个不同客户端标识, 或 mapping 存在但 volume 状态异常时阻止自动操作。
流程不修改 Cinder 状态, 不删除云盘, 不自动修改 `volume` 或 `volctrl`。

固定逻辑放在 `scripts/alcubierre-unmap.sh`; 本地
`scripts/run-alcubierre-unmap.sh` 通过 env-access 在一次 SSH 会话内发送脚本,
不在远端落盘, 避免拼接超长 `--cmd`。

## Volume Scan Optimization Volume 扫描优化

`preflight` 和独立 `verify` 每批只扫描一次完整 volume 清单。`execute` 在批次
开始和所有 mapping 操作结束后各扫描一次, 不再按 UUID 重复运行完整
`kvctl list volume --format object`。

执行期间不比较 volume 或客户端是否相对预检发生变化。初始 mapping 快照中没有
mapping 的对象直接跳过。API 保持逐盘串行, API 失败立即停止; API 成功后不逐盘
重新建立 `kubectl exec`, 而是在所有 POST 完成后统一刷新 mapping 和 volume。
mapping 或 volume 状态异常令命令返回失败, 已完成的 mapping 不回滚。

mapping 批处理只查询目标 `DISK_ID`, 在一次 Manul pod `kubectl exec` 中按协议循环
执行现有 `--where` 查询, 并用稳定边界标记归组结果。不要扫描或输出无关 mapping。
`preflight` 和独立 `verify` 各执行一次 mapping 批处理; `execute` 在 POST 前后
各执行一次。

输出 `INITIAL_VOLUME`、`INITIAL_MAPPING`、`API_TOTAL`、`FINAL_MAPPING`、
`FINAL_VOLUME` 和 `TOTAL` 阶段耗时, 并输出每盘 API 耗时。耗时仅用于诊断,
不改变成功条件。

## Via Access 普通跳板访问

为 `env-access.sh` 增加 `--via <SSH_TARGET>`, 与现有 mode 正交组合:

1. `ssh`: 本机经普通跳板机直达目标 IP 或 SSH target。
2. `jump18`: 本机经普通跳板机进入环境跳板 IP, 再进入 control node。
3. `jumpserver`: 本机经普通跳板机连接 JumpServer, 再通过菜单进入 asset。

使用 OpenSSH `ProxyJump`, 不向普通跳板机复制脚本, 也不依赖普通跳板机安装
`expect`、`sshpass` 或 skill 文件。

## JumpServer Without Alias 无 Alias 访问

JumpServer 支持两种输入:

1. 本机已有 SSH alias 时使用 `--alias`.
2. 没有 alias 时使用 `--jumpserver-host`、`--jumpserver-user`、
   `--jumpserver-port` 和 `--jumpserver-identity-file` 构造连接。

`--via` 必须传递到 `jumpserver-env.sh` 并加入 JumpServer SSH 命令。脚本不得硬编码
JumpServer 地址、用户名、密码或私钥。部分 override 参数缺失时在连接前失败。

## Compatibility 兼容性

`--via` 接受 SSH alias、IP 或 `user@host`, 拒绝以 `-` 开头的值。所有 SSH
路径显式读取用户 SSH config; 文件不存在时使用 `/dev/null`, 避免系统 SSH config
异常阻断连接。`--via` 只追加 ProxyJump, 不改变 SSH config 选择。

## Temporary Auth Profiles 临时认证 Profile

用户提供 JumpServer 认证信息时, Agent 使用稳定的 `--auth-profile <NAME>` 保存并
复用。默认目录为 `/tmp/easystack-env-access-${UID}/profiles/<NAME>/`。

profile 目录权限为 `0700`, 配置、密码和私钥文件权限为 `0600`。密码通过
`--jumpserver-password-file` 输入, 不提供明文命令行参数。保存 profile 时复制
密码和私钥内容, 后续不依赖原始文件。profile 可以保存 `via`、JumpServer host、
user、port、identity 和 password。

脚本不得在日志或错误中打印密码和私钥内容。`/tmp` 被系统清理或主机重启后,
用户需要重新提供认证信息。测试通过 `EASYSTACK_AUTH_CACHE_DIR` 使用隔离目录。

## Verification 验证

1. shell 语法检查。
2. access 脚本现有测试。
3. 新增 direct、jump18、JumpServer alias 和 JumpServer explicit override 的
   `--via` 参数测试。
4. 验证 auth profile 的保存、权限、复用和敏感信息不进入命令行。
5. 检查 skill frontmatter、全角标点和内部链接。
6. 检查 Alcubierre 流程包含授权门禁、批量失败策略和协议分流。
7. 通过 fake `kubectl` 调用计数验证 `preflight`、`verify` 各扫描一次 volume,
   `execute` 无论 UUID 数量只扫描两次 volume。
8. 验证 `preflight`、`verify` 各调用一次 mapping 批处理, `execute` 调用两次,
   且最终不再逐 UUID 重复查询 mapping。
9. 验证阶段及每盘 API 耗时输出存在, 数值为非负整数。
