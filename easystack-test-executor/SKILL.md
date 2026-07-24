---
name: easystack-test-executor
description: "Use when planning EasyStack OpenStack Compute, Storage, Network, Image, Security, Bare Metal, or cross-service tests, or executing them in a live environment with OpenStack CLI actions, worker logs, cleanup, and Chinese Markdown evidence. Combine `easystack-env-debugging` for backend root cause or runtime changes. Exclude Backup unless explicit."
---

# EasyStack Test Executor

## Overview 概览

在 EasyStack OpenStack 环境中标准化并执行测试计划。测试必须可复现、证据驱动,
且不得影响用例声明范围外的资源。

覆盖 Compute、Storage、Network、Image、Security、Bare Metal 和跨服务功能测试。
默认排除 Backup。输出为中文 Markdown, 专业术语保留英文。

## Scope Routing 范围路由

计划准备不访问环境。Live resource 功能和回归测试使用本 skill; backend 根因分析、
runtime code、overlay 或 patch 路径验证联合 `easystack-env-debugging`;
offline log、repository CI 和 Web UI E2E 分别路由到
`easystack-log-analysis`、`easystack-ci-test` 和 `easystack-cloud-web-e2e`。

## Safety And Authorization 安全与授权

- 已安装 `easystack-env-debugging` 时通过其 `env-access.sh` 访问; standalone 模式
  只使用用户提供且已授权的等价入口。
- Discovery 默认只读。计划外修改、重启、故障注入和节点操作必须另行授权。
- Contract 必须绑定 authorization scope 和 destructive operations。
- 只清理本次运行创建的资源或显式 fixture。默认 `preserve_on_failure`。
- 不保存密码、Token、Secret payload、私钥或完整密钥材料。

## Workflow 工作流

1. 读取 impact 文档和相关 catalog, 生成 impact obligations、负向路径和 coverage gap。
2. 复用 `/tmp/easystack-test-executor-profiles/` profile, 仅 freshness check 引用项。
3. 标准化 plan, 固化 profile、impact、authorization、cleanup 和 declarative checks。
4. 使用 `compile-plan.py` 生成 immutable V3 contract。
5. 每次只执行 `checkpoint.py next` 返回的 `launcher_argv`; 禁止手工选择 action。
6. Action 必须通过 `run-action.py`; 禁止 V3 使用 `record-command.py` 或手填 PASS/FAIL。
7. 按 contract 收集 worker logs、资源和 evidence, 再派生 immutable verdict。
8. verdict 后执行 cleanup, 生成 final result、报告并运行 `validate-run.py`。

## Core Execution Rules 核心执行规则

Autocompact、模型切换或中断后, 只读取 `<RESULT_ROOT>/resume.md`, 再执行
`checkpoint.py next`; 不从对话恢复进度。`allowed_action`、`bound_argv`、gate reason
和 artifact 均以 contract/event ledger 为准。

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| Impact 主流程和跨服务发散 | [openstack-feature-impact.md](references/openstack-feature-impact.md), [impact-cross-service.md](references/impact-cross-service.md) |
| Compute、Storage、Network/Image/Security 影响 | [impact-compute.md](references/impact-compute.md), [impact-storage.md](references/impact-storage.md), [impact-network-image-security.md](references/impact-network-image-security.md) |
| Upstream 能力核对 | [upstream-references.md](references/upstream-references.md) |
| 环境发现和 profile cache | [environment-discovery.md](references/environment-discovery.md), [environment-profile-cache.md](references/environment-profile-cache.md) |
| 操作规则和按需 catalog | [common-operations.md](references/common-operations.md), [compute.json](catalogs/compute.json), [storage.json](catalogs/storage.json), [network-image-security.json](catalogs/network-image-security.json), [baremetal.json](catalogs/baremetal.json) |
| Plan 标准化 | [case-normalization.md](references/case-normalization.md) |
| V3 状态机和恢复 | [execution-lifecycle.md](references/execution-lifecycle.md), [resumable-execution.md](references/resumable-execution.md) |
| Worker logs 和证据 | [log-evidence.md](references/log-evidence.md) |
| 结果语义和严格 Markdown | [reporting.md](references/reporting.md), [report-format.md](references/report-format.md) |
| V3 plan 和 profile 示例 | [test-case.example.yaml](examples/test-case.example.yaml), [environment-profile.example.yaml](examples/environment-profile.example.yaml) |

## Completion Gate 完成门禁

只有满足以下条件才能声明完成:

1. `checkpoint.py next` 返回 `run_complete`。
2. `validate-run.py` 返回 0; warning 已在报告说明。
3. 每个 Action 有 terminal event、时间和 Command ID 或明确 skip reason。
4. Required logs 有严格 correlation 和 artifact hash; optional/none 有明确状态。
5. verdict、cleanup、remaining resources 和 final result 已对账。
6. Markdown 索引、中文标题、简短测试需求和 H2 anchor 一致。
7. `执行结果` 只映射 Functional status; timing/evidence/cleanup 仅作为说明。

## Execution Feedback 执行反馈

执行本 skill 时, 若说明不清、同一步骤重复尝试、工具或权限阻塞、路径失效或产生
额外绕行, 任务结束时必须向用户报告:

- 触发位置和问题现象。
- 实际影响和额外开销。
- 临时处理方式。
- 可复用的优化建议。

没有实际问题时不输出空反馈。反馈中的凭据和用户数据必须脱敏。
