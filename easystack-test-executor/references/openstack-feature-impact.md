# OpenStack Feature Impact

## Goal 目标

在标准化用例前, 分析一个功能或改动点会影响哪些 OpenStack 服务、资源生命周期、
消费者、部署形态和不支持路径。不能只测试用户最先提到的直接路径。

## Evidence Priority 证据优先级

按以下顺序确认能力:

1. 当前 EasyStack 产品需求、支持矩阵和测试计划。
2. 目标环境版本、配置、driver、backend 和 API microversion。
3. OpenStack 官方当前版本文档、API reference、support matrix 和 release note。
4. 目标版本源代码、测试和历史 bug。
5. 既有经验, 只能作为待验证假设。

区分 `upstream capability`、`EasyStack support`、`environment enabled` 和
`test expectation`。不得将单个环境限制写成所有 OpenStack 版本的通用事实。

## Local Component Knowledge 本地组件知识

分析调用链和部署边界时按需读取:

- 若已安装 `easystack-env-debugging`, 按相关 service 读取其 OpenStack service map、
  Nova、Cinder、Glance、Barbican、Keystone、Networking 和 Bare Metal/Ironic
  文档。Standalone 模式使用本 skill catalog 和 upstream references。

这些文档用于定位 EasyStack 服务和证据入口, 不能替代目标版本 capability 验证。

生成测试义务时必须再读取与改动相关的本 skill 矩阵:

- [Compute Impact Matrix](impact-compute.md)
- [Storage Impact Matrix](impact-storage.md)
- [Network Image Security Impact Matrix](impact-network-image-security.md)
- [Cross-Service Impact Method](impact-cross-service.md)

## Impact Dimensions 影响维度

对每个改动点至少检查:

1. API 和 client: 参数、microversion、policy、错误码和幂等。
2. Control plane: API、scheduler、conductor、worker、RPC 和 taskflow。
3. Resource lifecycle: create、show、update、delete、extend、retype、migrate、transfer。
4. Source and derivative: Image、Snapshot、Clone、Cache、Upload、Backup。
5. Consumer: VM、Bare Metal、Container、Kubernetes integration 和其它服务。
6. Compute operation: boot、attach、detach、rebuild、resize、evacuate、migration。
7. Storage: backend、protocol、multipath、availability zone、replication 和 failover。
8. Security: Keystone、Barbican、key ownership、project isolation、rotation 和 redaction。
9. Failure and recovery: timeout、retry、rollback、service restart、host failure 和 residue。
10. Upgrade and compatibility: mixed version、legacy resource 和 API behavior。
11. Observability: Request ID、service logs、audit、metrics 和 resource correlation。
12. Cleanup: dependency order、failed resource、source preservation 和 leaked attachment。

Image 和 Security Group 用例的业务命令统一使用 `openstack` client。所有 Server
create 必须展开 Image-to-Volume、Boot Volume、Cinder/Nova attachment 和
boot-from-volume 路径, 并默认包含 Floating IP 创建、绑定和验证。Server cleanup
必须分析 force delete、Boot Volume、Port/Floating IP 解关联及残留。功能影响分析
必须将 client 行为、service logs 和实际 dataplane 证据分别列出。

未明确要求 Backup 时默认排除, 但必须在影响分析中记录为 `OUT_OF_SCOPE`, 不能因忽略
而误判覆盖完整。测试计划明确包含 Backup 时按正常能力分析。

## Capability Classification 能力分类

每个影响项标记:

```text
SUPPORTED
UNSUPPORTED
CONDITIONAL
UNKNOWN
OUT_OF_SCOPE
```

- `SUPPORTED`: 当前产品和环境明确支持, 生成正向和关键异常用例。
- `UNSUPPORTED`: 生成正确拒绝、状态一致性和无残留用例。
- `CONDITIONAL`: 明确 driver、backend、protocol、microversion 或配置条件。
- `UNKNOWN`: 先调查, 不直接执行破坏性验证。
- `OUT_OF_SCOPE`: 记录排除原因。

不支持不等于不测试。必须验证拒绝发生在正确层级, 错误可理解, 资源状态不被污染,
且没有 attachment、mapping、Secret、port 或后端残留。

## Expansion Output 发散输出

生成 `feature-impact.yaml`, 每个条目至少包含:

```text
feature
change_point
affected_service
resource_or_operation
consumer
capability_status
conditions
test_obligation
evidence_source
case_ids
```

先由影响项生成测试义务, 再将测试义务转换成标准化用例。若测试计划没有覆盖高风险
影响项, 在执行前报告 coverage gap, 不静默补成已授权用例。

## Encryption Example 加密云硬盘示例

分析 Cinder 加密或用户指定密钥改动时, 至少展开:

### Cinder Paths Cinder 路径

- 创建空卷, 以及从 Image、Snapshot、Volume 和 Cache 创建。
- Snapshot、Clone、Upload-to-Image、Extend、Retype、Migration 和 Transfer。
- source key、requested key、target key、数据一致性和源资源不变性。
- Backend、protocol、availability zone、driver capability 和容量开销。

### Consumer Paths 消费者路径

- VM data volume attach/detach。
- Boot-from-volume、encrypted system disk、rebuild、evacuate 和 migration。
- Barbican project access、key deletion、permission failure 和 Secret ownership。
- Bare Metal/Ironic 的普通 Cinder volume、boot-from-volume 和 encrypted volume
  attachment 能力必须分别判断。

OpenStack upstream Ironic 支持特定条件下的 Cinder boot-from-volume, 因此不能笼统
写成 "Bare Metal 不支持 Cinder volume"。但 Nova 当前 support matrix 将 Ironic 的
`Attach encrypted block volume to server` 标记为 `missing`。在 EasyStack 将其定义为
不支持时, 仍需生成以下负向义务:

1. 创建或 attach 请求被正确拒绝。
2. Server、Volume 和 Bare Metal node 状态保持一致。
3. Cinder attachment 和 Ironic volume connector 没有残留。
4. Barbican Secret 和 key ownership 不被意外修改。
5. Nova、Cinder、Ironic 和 Barbican 日志能够关联到同一请求。
6. 已支持的普通 volume 或 boot-from-volume 路径不发生回归。

### Failure Paths 失败路径

- Key 不存在、无权限、已删除或属于其它 Project。
- Cinder、Barbican、Nova 或 backend 超时和服务重启。
- attach、detach、migration 或 retype 中途失败。
- 日志缺失、重复请求、残留 mapping 和清理失败。

## Upstream Verification 上游验证

Capability、API microversion、support matrix 或跨组件影响不确定时读取
[upstream-references.md](upstream-references.md), 并使用与目标环境 release 匹配的
文档。
