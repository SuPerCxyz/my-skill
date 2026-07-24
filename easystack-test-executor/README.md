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
- 按用例需要动态覆盖 Kubernetes 相关 Pod/Container 和实际 worker 日志。
- 使用带 offset 的本地时间记录步骤和资源, 保留 UTC 原始 timestamp。
- 用脱敏日志证明 API/UI 不可见的内部路径。
- 输出中文 Markdown 详细结果, 通过索引跳转到各用例, 页面只显示 `成功` 或 `失败`。
- 顶层结果只跟随 Functional status, 时间、日志归档和清理异常独立显示为告警。
- 步骤时间或关键日志异常时, 在执行结果下附一条简短说明。
- 长时间测试使用持久化 checkpoint、命令 wrapper、确定性报告生成和完成校验, context
  压缩或模型切换后可从磁盘恢复。

默认不执行 OpenStack Backup 测试, 除非测试计划明确包含 Backup。

## Quick Start 快速开始

1. 提供目标环境、改动点和原始测试计划。
2. 展开测试义务, 复用环境 profile, 标准化已授权用例。
3. 确认清理策略、破坏性操作和结果目录。
4. 长时间运行先初始化 harness, 按 `SKILL.md` 执行并逐步保存 worker 日志与证据。
5. 从结构化记录生成报告, 通过 validator 后检查失败证据、清理状态和剩余资源。

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
| [references/resumable-execution.md](references/resumable-execution.md) | 长时间运行、自动记录、断点恢复和完成校验 |
| [references/log-evidence.md](references/log-evidence.md) | 日志窗口、多副本采集和关联证据 |
| [references/reporting.md](references/reporting.md) | 结果状态、输出目录、资源台账和清理 |
| [examples/environment-profile.example.yaml](examples/environment-profile.example.yaml) | 环境 profile 示例 |
| [examples/test-case.example.yaml](examples/test-case.example.yaml) | 标准化用例示例 |
| [examples/result-record.example.json](examples/result-record.example.json) | 结构化用例结果示例 |
| [examples/result-template.md](examples/result-template.md) | 详细结果和用例索引模板 |
| [scripts/checkpoint.py](scripts/checkpoint.py) | 初始化和更新运行状态与资源台账 |
| [scripts/record-command.py](scripts/record-command.py) | 自动记录每步命令、时间和输出 |
| [scripts/render-report.py](scripts/render-report.py) | 从结构化记录生成固定格式报告 |
| [scripts/validate-run.py](scripts/validate-run.py) | 校验运行状态和报告一致性 |
| [scripts/_harness.py](scripts/_harness.py) | harness 共用实现 |
| [scripts/_validation.py](scripts/_validation.py) | validator 共用字段和时间定义 |

## Safety 安全

环境访问复用 `easystack-env-debugging/scripts/env-access.sh`。环境发现默认只读, 用例
之外的配置变更、服务重启、故障注入或节点操作必须获得明确授权。任何结果文件都不得
记录密码、Token、Secret payload、私钥或完整密钥材料。
