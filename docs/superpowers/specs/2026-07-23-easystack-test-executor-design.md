# EasyStack Test Executor Design

## Goal 目标

创建 `easystack-test-executor` skill, 用于在 EasyStack OpenStack 环境中标准化并
执行 Nova、Cinder 和跨服务测试计划。执行过程必须可复现、证据驱动, 且不得影响
测试声明范围外的环境和资源。

## Scope 范围

首版覆盖:

- OpenStack 功能影响分析和发散测试义务。
- 最小充分环境确认。
- 环境 profile 首次采集、固化复用和 freshness check。
- Compute、Storage、Network 常用操作模板。
- 自然语言、Markdown 或脚本测试计划标准化。
- 默认串行的用例状态机和依赖处理。
- 跨用例时间窗与多副本日志收集规则。
- 命令、资源、请求 ID、验证和清理证据。
- 每个步骤的开始、结束、耗时和执行结果。
- 创建资源的名称、UUID、所属步骤和依赖关系。
- API/UI 不可见执行分支的日志原文和证据位置。
- 中文 Markdown 测试报告, OpenStack 专业术语保留英文。
- `PASS`、`FAIL`、`BLOCKED`、`INCONCLUSIVE` 四态结果。
- Nova、Cinder、Barbican、Glance、Neutron 等关联服务。

默认不覆盖 Backup 测试。只有测试计划明确要求时才纳入。

首版不实现完整测试调度器、日志守护进程或环境修改脚本。Agent 根据 skill 规则和
目标环境能力执行, 避免在缺少真实用例需求时过早固化自动化实现。

## Architecture 架构

采用渐进式披露:

```text
easystack-test-executor/
├── SKILL.md
├── README.md
├── references/
│   ├── environment-discovery.md
│   ├── environment-profile-cache.md
│   ├── common-operations.md
│   ├── openstack-feature-impact.md
│   ├── upstream-references.md
│   ├── case-normalization.md
│   ├── execution-lifecycle.md
│   ├── log-evidence.md
│   └── reporting.md
└── examples/
    ├── environment-profile.example.yaml
    ├── test-case.example.yaml
    └── result-template.md
```

`SKILL.md` 只保留触发范围、工作流、硬门禁和文件索引。细节按任务阶段加载, 避免
原始压缩包中超长单文件带来的上下文浪费。

## EasyStack Integration EasyStack 集成

环境访问、认证、pod 发现和只读安全门禁复用 `easystack-env-debugging`:

- 进入环境必须使用其 `scripts/env-access.sh`。
- 默认只执行查看操作。
- 需要故障根因分析时联合加载对应日志和组件文档。
- 测试计划授权的资源操作仅限具体用例范围。
- 计划外环境变更仍需用户明确授权。

环境确认只收集当前测试需要的信息。`openstack` namespace、`busybox-openstack`
CLI pod、`application/component` 标签以及服务多副本部署仅作为发现提示, 必须由
目标环境实时确认, 不硬编码成所有环境事实。

首次环境发现后将 Compute、Storage、Network 创建资源所需的稳定信息写入
skill 外部的 `/tmp/easystack-test-executor-profiles/<environment-key>.yaml`。后续
运行直接复用并对引用 ID 做定向 freshness check; pod 名称、restart count 和其它
动态日志目标仍在每次用例前后实时发现。环境 profile 属于 runtime data, 不进入
skill、源码仓库、用户 home 目录或分发包。

## Execution Flow 执行流程

```text
识别改动点并展开功能影响
-> 确认最小环境信息
-> 标准化用例
-> 检查依赖、风险和授权
-> 打开日志窗口
-> 执行单个用例
-> 验证功能结果
-> 关闭窗口并收集全部目标副本证据
-> 写入资源台账和结果
-> 按策略清理
-> 推进日志游标
```

首个窗口从运行开始时间计算, 后续窗口从上一个用例结束时间计算。一个用例失败后,
继续执行依赖仍有效的独立用例。

Image 和 Security Group 资源操作统一使用 `openstack` client。所有 Server 先创建
具名 Boot Volume, 再使用 `--volume` 启动; 禁止 image-backed ephemeral root。新建
Server 默认创建并绑定 Floating IP, 只有原始计划明确禁用时才能跳过。Server 清理
必须使用目标环境已验证的 force delete 命令, 不允许回退到普通 soft delete。

## Feature Impact Analysis 功能影响分析

执行前从 API、control plane、资源生命周期、消费者、compute 操作、storage、
security、failure recovery、upgrade、observability 和 cleanup 维度分析改动影响。
每个影响项区分 upstream capability、EasyStack support、environment enabled 和
test expectation。

不支持路径也必须生成负向测试义务。例如 Nova upstream support matrix 将 Ironic 的
encrypted block volume attachment 标记为 missing, 但 Ironic 在特定条件下支持普通
Cinder boot-from-volume。因此测试需要分别验证普通卷能力和加密卷正确拒绝、状态
一致性、无残留 attachment 及跨 Nova、Cinder、Ironic、Barbican 的证据。

## Safety And Errors 安全与异常

- 不记录密码、Token、Secret payload、私钥或完整密钥材料。
- 不静默修改测试预期、后端、镜像或清理策略。
- 证据不完整时不得判定 `PASS`。
- 内部执行分支没有直接日志证据时不得声称已验证。
- 日志默认优先数据路径 worker, 如 `cinder-volume`、`nova-compute`; API 日志只在
  Request ID、policy、输入校验或 HTTP 错误需要时补充。
- 清理只能在证据收集完成后执行。
- 不删除非本次运行创建的资源, 除非用例明确声明其为可删除 fixture。
- 缺少阻塞信息时停止用例执行并标记 `RUN_BLOCKED`。

## Validation 验证

实现完成后执行:

1. 检查 frontmatter 名称、双引号 description 和触发边界。
2. 检查 `SKILL.md` 与 `README.md` 文件索引覆盖全部参考文件。
3. 检查内部 Markdown 链接。
4. 检查 `SKILL.md` 与 `README.md` 的全角 Unicode 标点。
5. 检查根 `README.md` 按字母序登记新 skill。
6. 静态演练环境缺失、单用例失败、多副本日志缺失和清理受限场景。

不在设计验证阶段创建 OpenStack 资源或执行破坏性环境操作。
