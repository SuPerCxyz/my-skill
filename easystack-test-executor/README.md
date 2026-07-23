# EasyStack Test Executor

用于在 EasyStack OpenStack 环境中准备和执行 Compute、Storage、Network、Image、
Security 及跨服务测试计划, 并统一环境确认、用例状态机、多副本日志、资源证据、
清理和结果输出。

## Features 功能

- 从改动点展开关联组件、生命周期、消费者、不支持路径和发散测试义务。
- 首次将 Compute、Storage、Network 环境 profile 固化到外部 runtime profile store,
  后续定向验证后复用。
- 使用 `openstack` client 和已验证模板; Server 使用 Boot Volume、Floating IP、
  force delete, 测试 Image 默认为 `public`。
- 将原始计划转换为统一用例, 默认串行处理依赖、失败隔离和重试。
- 动态覆盖 Kubernetes 相关 Pod/Container, 优先收集实际 worker 日志。
- 使用带 offset 的本地时间记录步骤和资源, 保留 UTC 原始 timestamp。
- 用脱敏日志证明 API/UI 不可见的内部路径。
- 输出中文 Markdown 和 `PASS`、`FAIL`、`BLOCKED`、`INCONCLUSIVE` 四态结果。

默认不执行 OpenStack Backup 测试, 除非测试计划明确包含 Backup。

## Quick Start 快速开始

1. 提供目标环境、改动点和原始测试计划。
2. 展开测试义务, 复用环境 profile, 标准化已授权用例。
3. 确认清理策略、破坏性操作和结果目录。
4. 按 `SKILL.md` 执行并收集 worker 日志与证据。
5. 检查运行汇总、失败证据、清理状态和剩余资源。

## Files 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 触发范围、工作流、安全门禁和文件索引 |
| [references/openstack-feature-impact.md](references/openstack-feature-impact.md) | OpenStack 功能影响分析和发散测试义务 |
| [references/upstream-references.md](references/upstream-references.md) | OpenStack 组件文档、API 和 support matrix 入口 |
| [references/environment-discovery.md](references/environment-discovery.md) | 最小环境确认和 EasyStack 服务发现 |
| [references/environment-profile-cache.md](references/environment-profile-cache.md) | 环境 profile 固化、复用和刷新 |
| [references/common-operations.md](references/common-operations.md) | Compute、Storage、Network、Image、Security 常用操作模板 |
| [references/case-normalization.md](references/case-normalization.md) | 用例标准化、依赖和歧义处理 |
| [references/execution-lifecycle.md](references/execution-lifecycle.md) | 状态机、串并行、失败和重试 |
| [references/log-evidence.md](references/log-evidence.md) | 日志窗口、多副本采集和关联证据 |
| [references/reporting.md](references/reporting.md) | 结果状态、输出目录、资源台账和清理 |
| [examples/environment-profile.example.yaml](examples/environment-profile.example.yaml) | 环境 profile 示例 |
| [examples/test-case.example.yaml](examples/test-case.example.yaml) | 标准化用例示例 |
| [examples/result-template.md](examples/result-template.md) | 单用例结果模板 |

## Safety 安全

环境访问复用 `easystack-env-debugging/scripts/env-access.sh`。环境发现默认只读, 用例
之外的配置变更、服务重启、故障注入或节点操作必须获得明确授权。任何结果文件都不得
记录密码、Token、Secret payload、私钥或完整密钥材料。
