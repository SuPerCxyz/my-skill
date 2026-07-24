# Resumable Execution

## Purpose 目标

长时间测试不得依赖对话上下文保存步骤时间、资源和日志状态。使用本目录的脚本将
执行契约、当前状态和原始记录持续写入 `<RESULT_ROOT>`, 再从结构化记录生成报告。

模型负责分析和操作选择; 脚本负责不可遗漏的记录、恢复和格式校验。

## Start A Run 初始化运行

从 skill 根目录执行:

```bash
python3 scripts/checkpoint.py init \
  --result-root /tmp/easystack-test-<RUN_ID> \
  --run-id <RUN_ID> \
  --timezone <IANA_TIMEZONE> \
  --cleanup-policy preserve_on_failure \
  --case <CASE_ID>
```

使用环境 profile 中的 IANA timezone, 不使用无 offset 的缩写。初始化会生成:

```text
execution-contract.json
run-state.json
resume.md
resources-all.json
```

`execution-contract.json` 是本次运行的固定规则快照。已有非空目录时初始化会失败,
避免覆盖证据。测试中 skill 内容变化时, 最终校验会失败, 应先核对变更再决定恢复方式。

## Record Every Action 记录每个操作

每个改变资源或验证状态的 action 必须通过 wrapper 执行:

```bash
python3 scripts/record-command.py \
  --result-root <RESULT_ROOT> \
  --case-id <CASE_ID> \
  --step-id <STEP_ID> \
  --attempt attempt-01 \
  --description "<STEP_DESCRIPTION>" \
  --execute-location "<NODE_OR_CONTAINER>" \
  -- openstack volume create ...
```

wrapper 不使用 shell, 需要 pipeline 时显式执行 `bash -lc '<COMMAND>'`。它自动保存:

- 带 offset 的本地开始和结束时间。
- monotonic `duration_ms`、return code 和结果。
- 脱敏后的命令、stdout、stderr 和 Request ID。
- `commands.jsonl`、`commands.log` 及每一步独立输出文件。

重试时递增 `--attempt`, 不覆盖前一次输出; 所有 attempt 仍追加到用例级
`commands.jsonl`, renderer 会按实际执行顺序展示。

不得绕过 wrapper 后再人工估算步骤时间。wrapper 返回原命令的 return code, 所以失败
不会被记录工具隐藏。

资源创建成功后立即登记:

```bash
python3 scripts/checkpoint.py resource \
  --result-root <RESULT_ROOT> \
  --case-id <CASE_ID> \
  --step-id <STEP_ID> \
  --type Volume \
  --name <RESOURCE_NAME> \
  --uuid <RESOURCE_UUID> \
  --project <PROJECT_ID> \
  --status creating \
  --host-backend <HOST_OR_BACKEND>
```

Floating IP 使用 address 作为 `name`。不得把凭据放入命令参数或结果文件。

## Checkpoint Protocol 断点协议

每次状态机 phase 变化、资源创建以及日志窗口关闭后更新 checkpoint:

```bash
python3 scripts/checkpoint.py update \
  --result-root <RESULT_ROOT> \
  --case-id <CASE_ID> \
  --phase <PHASE> \
  --next-action "<ONLY_NEXT_ACTION>" \
  --functional-status <PASS_OR_FAIL> \
  --timing-status <VALID_OR_INVALID> \
  --evidence-status <TERMINAL_STATUS> \
  --cleanup-status <TERMINAL_STATUS> \
  --diagnostic-status <TERMINAL_STATUS>
```

未到终态的状态参数可以省略。进入下一用例前, 当前用例依次完成日志收集、
`RECORD_RESULT`、`CASE_GATE`、清理判断和游标推进, 最后写入 `phase=COMPLETE`。

## Recovery After Compaction 压缩后恢复

发生 autocompact、中断或模型切换时, 停止新的环境操作, 依次读取:

1. `<RESULT_ROOT>/execution-contract.json`
2. `<RESULT_ROOT>/run-state.json`
3. `<RESULT_ROOT>/resume.md`
4. [execution-lifecycle.md](execution-lifecycle.md) 的 `Invariants 必守不变量`

只执行 `resume.md` 的 Next action。不得通过聊天历史猜测当前 phase, 不得重做已记录为
完成的资源操作。若磁盘记录和聊天描述冲突, 以结构化记录为准并报告冲突。

`resume.md` 只保存恢复所需的最小状态, 每次 checkpoint 都会重写。需要检查完整状态时:

```bash
python3 scripts/checkpoint.py show --result-root <RESULT_ROOT>
```

## Structured Case Result 结构化用例结果

完成验证后写入 `cases/<CASE_ID>/result.json`, 字段结构参考
[../examples/result-record.example.json](../examples/result-record.example.json)。

- `functional_status` 只能按功能断言设置为 `PASS` 或 `FAIL`。
- 步骤记录不完整时设置 `timing_status=INVALID`, 不修改已经确定的 Functional status。
- `required` 日志缺失时设置 `evidence_status=MISSING` 或 `INVALID`。
- `optional` 日志未采集时设置 `evidence_status=PARTIAL`。
- `none` 日志设置 `evidence_status=NOT_APPLICABLE`。
- `logs` 只引用最小充分、已脱敏的 worker 日志和证据文件。

用例结果中的 `checks`、`logs` 和状态由模型根据证据填写; 步骤和资源表由 renderer
优先从 `commands.jsonl` 和 `resources.json` 读取, 避免重复手工录入。

## Render And Validate 生成和校验

每个用例完成后执行一次, 运行结束前再执行一次:

```bash
python3 scripts/render-report.py --result-root <RESULT_ROOT>
python3 scripts/validate-run.py --result-root <RESULT_ROOT>
```

renderer 确定性生成 `result.md`、`summary.md`、`results.csv` 和 `run.json`。不要手工
改生成文件; 修改 `result.json` 或其它结构化记录后重新生成。

validator 的 exit code 语义:

- `0`: 结构和状态闭合; 可能仍输出 evidence 或 timing warning。
- `1`: 存在阻止声明完成的结构错误。
- `2`: 输入目录或执行契约缺失。

明确写入 `INVALID`、`MISSING` 或 `PARTIAL` 后, 诊断缺口以 warning 保留, 不把
`functional_status=PASS` 改成失败。未显式记录缺口、报告格式不一致、用例缺失或 phase
未到 `COMPLETE` 时返回非零。

## Completion Rule 完成规则

只有 `validate-run.py` 返回 0 才能声明本次运行已完成。若有 warning, 在交付说明中
列出受影响用例; 最终 Markdown 的 `执行结果` 仍只按 Functional status 显示成功或失败。
