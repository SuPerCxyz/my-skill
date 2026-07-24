# Storage Impact Matrix

## Purpose 目标

Cinder 改动按 source、backend、consumer、数据路径和失败恢复展开。Volume 进入
`available` 只能证明生命周期终态, 不能证明 clone、cache、copy 或 encryption 分支。

## Creation Matrix 创建矩阵

| Source | 关键变量 | 后续关联 |
|--------|----------|----------|
| Blank | Volume Type、AZ、size、QoS、encryption | attach、extend、snapshot、delete |
| Image | raw/qcow2、virtual size、image cache、clone/copy | Boot Volume、cache hit/miss、conversion |
| Snapshot | source status、size、backend clone capability | incremental relation、delete dependency |
| Volume | same/cross backend、type、encryption key | clone depth、data consistency、source unchanged |
| Backup | 默认 OUT_OF_SCOPE | 仅在用户明确要求时加入 |

## Lifecycle Matrix 生命周期矩阵

- Snapshot: create、delete、force delete、busy source、encrypted source 和 clone。
- Extend: available/in-use、filesystem 之外的 block size、encrypted overhead 和 backend
  capability。
- Retype/migrate: same backend、cross backend、host-assisted、encryption transition、
  migration rollback 和 temporary volume residue。
- Attach/detach: Nova、Ironic、multiattach、connector、os-brick、multipath 和 stale
  attachment。
- Upload-to-image: public/private visibility、disk format、encrypted data exposure 和
  Glance cleanup。
- Replication/failover: service state、secondary ID、attachment continuity 和 failback。

## Encryption Obligations 加密义务

- 验证 Volume Type encryption metadata、Barbican Secret ownership、Project isolation
  和 key availability。
- 分开测试 blank、Image、Snapshot、Volume clone 和 cache source, 因为 key selection、
  decrypt/re-encrypt 和 backend optimized path 不同。
- VM data attach、Boot Volume、rebuild、migration、evacuate 和 detach 都是消费者回归面。
- Bare Metal 普通 Volume、boot-from-volume 和 encrypted attach 必须分别判断。
  EasyStack 声明 encrypted attach 不支持时, 验证请求被正确拒绝且无 attachment、
  connector、mapping 和 Secret 副作用。
- 不在日志或报告输出 key material、Secret payload 或未脱敏的 auth context。

## Backend And Clone Evidence Backend 和 Clone 证据

- 记录 `cinder-volume` 实际 Pod、host@backend、driver、protocol 和目标 Volume ID。
- clone/cache/copy 分支必须使用 worker 日志或 backend 直接证据, 不能从 UI 或资源终态
  反推。
- Ceph/RBD 场景关注 clone depth、flatten、parent、image-volume cache、pool 和 feature。
- LVM/iSCSI、FC、NVMe-oF 等场景关注 connector、target、multipath 和 cleanup。
- Cache 测试区分 hit/miss、cache limit、并发填充、失效 Image 和 internal tenant。

## Failure And Cleanup 失败和清理

- API、scheduler、volume worker、Barbican、backend 和 connector 任一层超时都要检查
  Cinder 状态和 DB/后端残留的一致性。
- 重试前先确定前一次 taskflow 已结束, 避免重复 Volume 或 attachment。
- 清理按 Server -> attachment -> Snapshot/clone -> Volume -> Image/Secret 依赖执行,
  实际顺序以本次资源图为准。
