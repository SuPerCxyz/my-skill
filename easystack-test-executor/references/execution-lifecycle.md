# Execution Lifecycle

## Concurrency 并发

默认全局串行执行。以下任一条件成立时禁止并行:

- 日志窗口从上一个用例结束延续到当前用例结束。
- 用例共享 Cache、Volume、Snapshot、Image、Server、Host 或 Backend。
- 包含故障注入、服务重启或主机操作。
- 资源名称、依赖或清理动作可能冲突。
- Request ID 不足以可靠分离日志。

只有计划明确允许, 且资源、日志、依赖和清理完全隔离时才可并行。并行前记录隔离
依据和最大并发数。

## State Machine 状态机

每个用例按以下顺序执行:

```text
DISCOVER_CASE_CONTEXT
OPEN_LOG_WINDOW
SNAPSHOT_SERVICE_INSTANCES
PREPARE
EXECUTE
WAIT
VERIFY
CLOSE_LOG_WINDOW
COLLECT_LOGS
COLLECT_RESOURCES
RECORD_RESULT
CASE_GATE
APPLY_CLEANUP_POLICY
ADVANCE_LOG_CURSOR
```

无论失败发生在哪个阶段, 都必须进入关闭窗口、证据收集、结果记录和清理判断。
长时间运行、用例多于 1 个或可能发生 context compaction 时, 使用
[resumable-execution.md](resumable-execution.md) 的 harness 固化每次 phase 变化。

## Invariants 必守不变量

以下各项在任意阶段都不可降级, 不得用"看起来完成"替代。autocompact 或中断恢复时,
先读取运行目录中的 contract、state 和 resume, 再重读本节重新注入规则。只执行
`resume.md` 的 Next action, 不依赖主上下文回忆整个 skill。

1. 每个用例必须有二态 `执行结果` (`成功`/`失败`) 和完整诊断字段。只允许按
   `functional_status` 映射顶层结果; 时间、日志归档和清理告警不得覆盖功能结果。
   功能未执行或无法判断时 `functional_status` 不得为 `PASS`, 顶层结果为失败。
2. 每个 action step 必须有 `start_local`、`end_local`、`timezone`、`duration_ms`、
   return code 和 result; 步骤失败也要写结束时间。缺失或负耗时设置
   `timing_status=INVALID` 并报告告警, 但 step result 仍按操作实际结果记录。
3. 资源创建后立即写入用例级和运行级台账, 不等待用例结束; 至少含 type、name、UUID、
   project、status、host/backend、cleanup policy。
4. 证据收集完成后才允许清理; 清理按逆依赖顺序; 不得删除非本次运行创建的资源。
5. 用例声明验证内部执行分支时优先用 worker 日志直接证明; 无直接证据时将该路径检查
   标为 `未确认` 并设置 evidence 告警, 不从资源终态反推, 也不覆盖其它功能断言。
   不要求日志且执行成功的用例允许 `evidence_status=NOT_APPLICABLE`。
6. 不得输出密码、Token、Secret payload、私钥或完整密钥材料; 日志和报告必须脱敏。
7. 日志窗口从上一用例结束延续到当前用例结束; UTC 仅保留原始 timestamp, 展示用带
   offset 的本地时间。
8. `summary.md`、`results.csv` 和 `run.json` 的用例结果必须一致; 任一用例结果变更
   时三者同步更新。

`RECORD_RESULT` 之后执行 `CASE_GATE`: 逐条核对第 1-6 项中与本用例相关者。缺少功能
结果时回到对应验证阶段; 缺少步骤时间、日志归档或台账字段时先尝试补齐, 补齐失败则
显式写入 `INVALID`、`MISSING` 或 `PARTIAL` 告警。诊断字段有明确终态后允许进入清理和
下一用例, 不得仅因记录质量问题把 `functional_status=PASS` 改成失败。

harness 运行在 `CASE_GATE` 后生成报告并执行 `validate-run.py`。校验 exit code 非 0
表示结构或状态未闭合; warning 表示已显式记录的诊断缺口。两者都不得由模型自行改写
为 Functional failure。

## Command Records 命令记录

每条命令记录:

- Case ID 和 Step ID。
- 带 UTC offset 的本地开始和结束时间。
- `duration_ms`。
- 脱敏后的命令。
- 执行位置。
- 返回码、stdout 和 stderr。
- 可获得的 Request ID。

保存为:

```text
cases/<CASE_ID>/commands.jsonl
cases/<CASE_ID>/commands.log
```

命令返回码为 0 不能单独证明通过。异步资源必须轮询到用例声明的终态。

每个步骤还必须记录步骤级 `start_local`、`end_local`、`timezone`、`duration_ms`、
执行结果和本步骤创建或修改的资源。步骤失败时也要写结束时间, 不留下无终态记录。
本地时间采用 RFC3339 并带明确 offset, 例如 `2026-07-23T14:08:08.447+08:00`。
耗时使用 monotonic clock 计算, 不通过两个 wall-clock timestamp 相减。

## Timeouts And Polling 超时和轮询

每个异步步骤必须声明:

```text
timeout_seconds
poll_interval_seconds
success_states
failure_states
```

超时后记录最后状态和直接证据, 不无限等待。只在操作被证明幂等或原用例明确允许时
重试。

## Failure Handling 失败处理

单个用例失败时:

1. 记录失败阶段、命令、返回码和资源当前状态。
2. 关闭日志窗口并收集目标服务证据。
3. 更新用例和运行级资源台账。
4. 应用清理策略。
5. 继续执行依赖仍有效的独立用例。

不得在用例内部直接终止整个运行。

## Retry Handling 重试处理

重试不得覆盖前一次证据。每次尝试使用独立目录:

```text
cases/<CASE_ID>/attempt-01/
cases/<CASE_ID>/attempt-02/
```

重试前确认前一次操作没有仍在运行, 且不会创建重复资源或改变测试语义。无法确认时
将 `diagnostic_status` 标为 `INCONCLUSIVE` 或 `BLOCKED`, `执行结果` 标为失败, 不
盲目重试。

## Destructive Cases 破坏性用例

用例明确要求删除、重启、故障注入或主机操作时:

1. 再次核对目标对象和授权范围。
2. 记录影响、预期恢复路径和回滚方式。
3. 收集操作前状态。
4. 只操作精确目标。
5. 收集操作后状态和恢复证据。

计划外的环境变更必须停止并请求用户授权。
