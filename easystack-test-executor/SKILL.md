---
name: easystack-test-executor
description: "Use when planning or executing EasyStack OpenStack Compute, Storage, Network, Image, Security, or cross-service functional and regression tests that require feature-impact analysis, environment discovery, OpenStack CLI operations, worker logs, evidence, cleanup, and Chinese Markdown results. Exclude Backup unless explicitly requested."
---

# EasyStack Test Executor

## Overview 概览

在 EasyStack OpenStack 环境中标准化并执行测试计划。测试必须可复现、证据驱动,
且不得影响用例声明范围外的资源。

本 skill 负责:

- 分析改动影响, 固化最小环境信息, 标准化并执行跨服务测试计划。
- 提供 Compute、Storage、Network、Image、Security 常用操作模板。
- Server 使用 Boot Volume、Floating IP 和 force delete; 测试 Image 默认为 `public`。
- 按本地时间记录步骤和资源, 收集实际 worker 日志并证明内部执行分支。
- 输出中文 Markdown 报告和 `PASS`、`FAIL`、`BLOCKED`、`INCONCLUSIVE` 四态结果。

默认不测试 OpenStack Backup。只有测试计划明确包含 Backup 时才执行。

## Scope Routing 范围路由

根据用户目标选择入口:

1. 测试计划准备: 只标准化用例、检查依赖和执行风险, 不访问环境。
2. 测试执行: 完成最小环境确认后, 按本 skill 执行并收集证据。
3. 失败分析: 用本 skill 保存测试上下文, 同时使用
   [`easystack-env-debugging`](../easystack-env-debugging/SKILL.md) 构建根因证据链。
4. 离线历史日志分析: 使用 `easystack-log-analysis`, 不用本 skill 重新执行测试。
5. 仓库 CI: 使用 `easystack-ci-test`, 不访问运行中环境。
6. Web UI E2E: 使用 `easystack-cloud-web-e2e`, 本 skill 只负责需要后台证据的部分。

## Safety And Authorization 安全与授权

环境访问和后台命令遵循 `easystack-env-debugging` 的安全门禁:

- 必须通过其 `scripts/env-access.sh` 进入环境。
- 环境发现默认只允许查看操作。
- 测试计划明确声明的资源操作属于用例授权范围。
- 计划外环境修改、服务重启、配置变更、故障注入和节点操作必须另行确认。
- 不得输出密码、Token、Secret payload、私钥或完整密钥材料。
- 不得删除非本次运行创建的资源, 除非用例明确声明其为可删除 fixture。

执行前必须明确 `cleanup_policy`、允许的破坏性操作和结果目录。未指定清理策略时,
使用 `preserve_on_failure`。

## Workflow 工作流

### Step 1: Analyze Feature Impact 分析功能影响

读取 [references/openstack-feature-impact.md](references/openstack-feature-impact.md),
生成测试义务和 coverage gap; 发散场景不自动获得执行授权。

### Step 2: Discover Minimum Environment 最小环境发现

读取 [references/environment-discovery.md](references/environment-discovery.md), 只确认
当前用例需要的信息。已有 runtime profile 时按
[references/environment-profile-cache.md](references/environment-profile-cache.md)
定向验证; 阻塞信息缺失时设置 `RUN_BLOCKED`。只准备计划时不访问环境。

### Step 3: Normalize Plan 标准化计划

读取 [references/case-normalization.md](references/case-normalization.md), 将测试义务
转换为统一用例, 不静默修改用户语义。

### Step 4: Confirm Risk And Authorization 确认风险和授权

确认资源影响和破坏性操作; 高风险行为必须同时满足用例声明和用户授权。

### Step 5: Execute Cases 执行用例

按 [references/execution-lifecycle.md](references/execution-lifecycle.md) 默认串行执行,
并使用 [references/common-operations.md](references/common-operations.md) 的模板。

### Step 6: Collect Evidence 收集证据

按 [references/log-evidence.md](references/log-evidence.md) 维护跨用例窗口, 动态发现
目标 Pod/Container, 并优先收集实际 worker 日志。

### Step 7: Verify And Report 验证和报告

按 [references/reporting.md](references/reporting.md) 记录功能、证据和清理状态;
命令返回码不能单独证明通过。

### Step 8: Apply Cleanup 执行清理

完成证据收集后逆依赖清理; 失败时保留台账并标记 `cleanup_status=PARTIAL`。

## Core Execution Rules 核心执行规则

状态机、失败处理、重试、用例门禁 (CASE_GATE) 和必守不变量以
[references/execution-lifecycle.md](references/execution-lifecycle.md) 为唯一来源; 时间窗、
UTC 日志归一化和游标推进以 [references/log-evidence.md](references/log-evidence.md) 为
唯一来源。autocompact 或中断恢复时, 先重载 execution-lifecycle.md 的 Invariants 再继续,
不依赖主上下文回忆整个 skill。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 从改动点展开关联组件、消费者和不支持路径 | [references/openstack-feature-impact.md](references/openstack-feature-impact.md) |
| 核对组件文档、API、support matrix 和 release | [references/upstream-references.md](references/upstream-references.md) |
| 最小环境确认、EasyStack 访问入口和服务发现 | [references/environment-discovery.md](references/environment-discovery.md) |
| 环境 profile 首次固化、复用和刷新 | [references/environment-profile-cache.md](references/environment-profile-cache.md) |
| Compute、Storage、Network、Image、Security 常用操作 | [references/common-operations.md](references/common-operations.md) |
| 用例 schema、依赖、歧义和执行清单 | [references/case-normalization.md](references/case-normalization.md) |
| 状态机、串并行、超时、失败和重试 | [references/execution-lifecycle.md](references/execution-lifecycle.md) |
| 跨用例窗口、多副本日志和关联证据 | [references/log-evidence.md](references/log-evidence.md) |
| 结果状态、目录布局、资源台账和清理 | [references/reporting.md](references/reporting.md) |
| 环境 profile 示例 | [examples/environment-profile.example.yaml](examples/environment-profile.example.yaml) |
| 标准化用例示例 | [examples/test-case.example.yaml](examples/test-case.example.yaml) |
| 单用例结果模板 | [examples/result-template.md](examples/result-template.md) |

## Completion Gate 完成门禁

声明测试运行完成前确认:

1. 已保存影响分析、环境 profile、标准化用例和全部已开始用例的终态。
2. 日志窗口、实例快照、覆盖状态和关键内部路径证据完整或明确标记缺失。
3. 每个步骤和资源均有本地时间、耗时、名称、UUID、结果及所属关系。
4. 功能、证据、清理、剩余资源和风险已记录, 且输出已脱敏。
5. Server 使用 Boot Volume、Floating IP 和 force delete, 或记录计划允许的例外。
6. 测试 Image visibility 为 `public`, 或记录其它 visibility 的测试目的。
7. UTC 日志保留原始 timestamp, 报告使用带明确 offset 的本地时间。
8. Run ID 格式为 `R<YYYYMMDDHHmmss>` (精确到秒) 用作输出目录 `<RESULT_ROOT>` 名称和内部引用，不在资源名中包含时间戳。

## Execution Feedback 执行反馈

执行本 skill 时, 若说明不清、同一步骤重复尝试、工具或权限阻塞、路径失效或产生
额外绕行, 任务结束时必须向用户报告:

- 触发位置和问题现象。
- 实际影响和额外开销。
- 临时处理方式。
- 可复用的优化建议。

没有实际问题时不输出空反馈。反馈中的凭据和用户数据必须脱敏。
