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
- 长时间运行的持久化 checkpoint、命令记录、报告生成和完成校验。
- 跨用例时间窗与多副本日志收集规则。
- 命令、资源、请求 ID、验证和清理证据。
- 每个步骤的开始、结束、耗时和执行结果。
- 创建资源的名称、UUID、所属步骤和依赖关系。
- API/UI 不可见执行分支的日志原文和证据位置。
- 中文 Markdown 测试报告, OpenStack 专业术语保留英文。
- 用例索引强制输出中文名称和一句简短测试需求, 技术组合保留为 scenario key。
- 最终 Markdown 只显示 `成功` 或 `失败`, 内部保留功能、证据、清理和诊断状态。
- Nova、Cinder、Barbican、Glance、Neutron 等关联服务。

默认不覆盖 Backup 测试。只有测试计划明确要求时才纳入。

首版不实现完整测试调度器、日志守护进程或环境修改脚本。只提供无第三方依赖的
resumable harness, 将不可遗漏的时间、状态和报告格式从提示词约束下沉为机器校验。

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
│   ├── resumable-execution.md
│   ├── log-evidence.md
│   └── reporting.md
├── examples/
    ├── environment-profile.example.yaml
    ├── test-case.example.yaml
    ├── result-record.example.json
    └── result-template.md
└── scripts/
    ├── _harness.py
    ├── _validation.py
    ├── checkpoint.py
    ├── record-command.py
    ├── render-report.py
    └── validate-run.py
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
- 顶层 `执行结果` 只跟随 Functional status; 时间、日志归档和清理异常独立记录为告警。
- 步骤时间或关键日志异常时, 在 `执行结果` 下增加一条简短说明。
- 内部执行分支没有直接日志证据时不得声称已验证。
- 用例需要内部路径证据或失败诊断时优先数据路径 worker, 如 `cinder-volume`、
  `nova-compute`; API 日志只在
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

## Deterministic Harness V3 确定性执行器 V3

长任务不能依赖模型记忆工作流。V3 将模型限制为计划分析、环境判断和异常解释,
将动作选择、命令执行、结果推导、资源捕获、恢复和完成门禁下沉到脚本。

### Immutable Plan 不可变计划

`compile-plan.py` 读取标准化用例、环境 profile、impact analysis 和 authorization,
生成完整 `execution-contract.json`。Contract 固化:

- Case 顺序、依赖、能力分类和 impact references。
- 每个 Action 的 argv、执行位置、timeout、允许返回码和 capture 规则。
- Declarative checks、日志要求、log targets 和 cleanup policy。
- Profile、impact、authorization、skill 和 source plan digest。

Contract 外的 Case 和 Step 不得执行。运行中 skill 变化只产生版本漂移告警; 运行仍按
冻结 contract 验证。V2 运行只读兼容, 不允许继续执行旧式任意命令。

### Enforced State Machine 强制状态机

状态变化写入 append-only `events.jsonl`, 每个事件包含 sequence、previous hash、
timestamp、Case、Step、event type 和 payload。`run-state.json` 和 `resume.md` 是事件
投影, 不是唯一事实来源。

模型不能直接指定 phase、Action status 或 Next action。`checkpoint.py next` 返回唯一
action type、完整 launcher argv 和门禁原因。`run-action.py` 只执行 contract 中冻结的
argv, 根据 expected outcome 自动写入终态。

Lifecycle 使用两阶段结果:

```text
ACTIONS -> COLLECT_LOGS -> COLLECT_RESOURCES -> DERIVE_VERDICT
-> APPLY_CLEANUP_POLICY -> FINALIZE_RESULT -> CASE_GATE -> COMPLETE
```

`case-verdict.json` 在 cleanup 前生成且不可修改。`result.json` 在 cleanup 后生成,
只补充 cleanup、完整性和最终时间信息。

### Reconciliation 对账

完成门禁从 append-only event ledger 重建并对账以下事实:

1. Contract 中的每个 Action 都有自动终态、时间和唯一 Command ID。
2. Required Functional check 由 evaluator 决定, 模型不得手工聚合。
3. Command、resource 和 result projection 与 event payload 一致。
4. 每个 evidence file 的 path、size 和 SHA256 与 artifact manifest 一致。
5. Required log target 有窗口、Pod UID、container、关联键和真实 evidence file。

顶层 `执行结果` 仍只显示成功或失败。独立的 `execution_quality` 使用 `COMPLETE`、
`COMPLETE_WITH_WARNINGS` 或 `INVALID`, 记录时间、证据和清理完整性。

### Command Safety 命令安全

每条命令使用唯一 Command ID 和独立输出文件, 支持 timeout、process group 终止、
流式输出、Request ID 提取和追加记录。Action 只接受 argv array, 禁止 shell 拼接。
允许返回码支持 negative test。Resource capture 与 Action event 一次提交, 台账由事件
重建, 避免命令成功后模型漏记 UUID。

### Recovery 恢复

任何新 turn、context compaction 或模型切换后先执行:

```text
checkpoint.py next --result-root <RESULT_ROOT> --format json
```

输出只包含当前 Case、phase、Action、完整 launcher argv、未满足门禁和最近事件。
恢复不重新解释聊天历史。

### Environment And Logs 环境和日志

环境 profile 使用稳定 environment key、权限检查、schema 校验和 environment
fingerprint。日志工具保存 Pod 前后快照、current/previous stream、UTC 原始时间、
本地归一化时间、关联结果和覆盖状态。

### Knowledge Modules 知识模块

OpenStack 发散测试按 Compute、Block Storage、Network、Image、Security Group、
Encryption/Barbican 和 Bare Metal/Ironic 分模块维护。每个模块包含生命周期、消费者、
不支持路径、失败恢复、证据目标和清理义务。

### Automated Verification 自动验证

使用标准库单元测试覆盖 transition、resume、expected non-zero、timeout、artifact
tamper、结果推导、cleanup policy、日志关联、资源投影、partial run、Markdown
snapshot 和 anchor collision。标准 `evals/evals.json` 覆盖长任务压缩恢复和弱模型
漏步骤场景。

## Context Budget 上下文预算

`SKILL.md` 目标不超过 120 行和 6 KB, 只保留触发边界、硬门禁、主流程和文档路由。
参考文档按环境、执行、报告和 OpenStack domain 分组, 每次仅加载相关文件。重复命令
模板改为 machine-readable catalog, 不在多个 Markdown 文件中复制。
