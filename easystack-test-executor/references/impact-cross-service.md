# Cross-Service Impact Method

## Dependency Graph 依赖图

先把改动点放入资源图, 再生成用例。常见 Server 路径:

```text
Glance Image
  -> Cinder Boot Volume -> Barbican Secret
  -> Nova Server -> Placement allocation
  -> Neutron Port -> Security Group -> Floating IP
  -> nova-compute / os-brick / hypervisor
```

常见 Bare Metal 路径:

```text
Ironic Node/Port
  -> Nova/Ironic scheduling
  -> Neutron provisioning/tenant network
  -> Glance image delivery
  -> optional Cinder boot/attach connector
  -> optional Barbican secret
```

图中每个边都检查正向能力、拒绝语义、rollback 和残留。某一服务不支持该边时, 仍要
验证上游资源和其它已支持边不受污染。

## Expansion Algorithm 发散算法

1. 定位被修改的 API、scheduler、worker、driver 或数据模型。
2. 列出它直接读取和写入的资源。
3. 沿 source、derivative、consumer 和 cleanup 四个方向各扩展一层。
4. 对每条边标记 SUPPORTED、UNSUPPORTED、CONDITIONAL、UNKNOWN 或 OUT_OF_SCOPE。
5. 对高风险边生成正向、负向、失败恢复和回归义务。
6. 为每项义务指定功能检查、worker 日志目标和清理对象。
7. 与用户计划对比, 未授权项只报告 coverage gap, 不直接执行。

## High-Risk Signals 高风险信号

出现以下信号时至少跨两个组件扩展:

- encryption、key、Secret、Project ownership。
- attachment、connector、Port binding、mapping。
- scheduler、trait、AZ、host/backend selection。
- cache、clone、copy、conversion、migration。
- retry、timeout、rollback、service restart。
- delete、force delete、reclaim、residue。
- mixed version、microversion、driver capability。

## Evidence Assignment 证据分配

每个用例在计划阶段分配:

- `functional` check: 用户可观察行为或资源状态。
- `diagnostic` check: scheduler/worker/driver 内部分支。
- `cleanup` check: 资源图最终状态和残留。
- `log_targets`: 真正执行操作的 Pod/Container, API 日志仅在请求拒绝或 Request ID
  关联需要时收集。

内部 clone、cache、connector、migration 和 encryption 分支必须有 worker 或 backend
证据。若证据不可得, 对应 diagnostic check 为 UNKNOWN; 已独立验证的 functional
check 仍按事实计算。

## Example: Encrypted Volume 示例

Volume encryption 改动至少关联 Cinder、Barbican、Nova、Ironic、Glance 和 backend:

- 从 Image 创建涉及 Glance format、Cinder cache/clone 和 key selection。
- VM attach 涉及 Nova、os-brick、connector 和 hypervisor。
- Ironic encrypted attach 若产品不支持, 生成拒绝和无残留用例, 不尝试伪造成功。
- migration/retype 涉及 source/target backend 和 re-encryption。
- cleanup 涉及 attachment、Volume、Snapshot/clone、cache relation 和 Secret ownership。
