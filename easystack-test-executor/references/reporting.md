# Reporting

## Result Model 结果模型

面向用户的 `执行结果` 只允许:

- `成功`: `functional_status=PASS`, 即功能断言和必需资源操作符合预期。
- `失败`: `functional_status=FAIL`、功能未执行完成或无法判断功能结果。

内部记录保留诊断维度:

```text
functional_status
evidence_status
cleanup_status
diagnostic_status
timing_status
```

顶层结果只从 `functional_status` 映射。`evidence_status`、`timing_status` 和
`cleanup_status` 独立记录, 其异常不得把已通过的功能结果改为失败。日志或可观测性
本身是测试目标时, 将对应断言定义为 functional check; 此时该断言的实际结果可以改变
`functional_status`, 但日志文件归档不完整仍只属于 evidence 告警。

使用以下固定映射, 不允许模型自行聚合诊断字段:

```text
functional_status=PASS -> execution_result=成功
functional_status!=PASS -> execution_result=失败
```

当 `timing_status` 或 `evidence_status` 存在异常时, 在 `执行结果` 的成功/失败下一行增加
一条 `说明:`。只概括异常类型, 使用分号分隔, 不在这里展开原因或证据。例如:

```text
成功

说明: 步骤时间记录异常; 关键日志未保存。
```

没有相关异常时不输出 `说明:`。这行说明不得改变 `execution_result`。

每个 action step 记录 `start_local`、`end_local`、`timezone`、`duration_ms`、
return code 和 result。时间使用目标环境本地时区并带明确 UTC offset; 用例总耗时
不能替代步骤耗时。

## Language And Format 语言和格式

测试报告必须使用 Markdown。正文以简体中文为主, OpenStack 服务名、API、CLI、
resource type、status、field name、Request ID 和代码标识符保留英文。

报告优先直接给出结论、步骤时间、资源名称、worker 日志原文和清理结果。避免将 API
返回详情或无关 control-plane 日志大段复制到报告。

报告中的运行、用例、步骤和资源时间默认展示本地时间。UTC 仅用于日志查询边界或保留
原始日志 timestamp, 不作为默认展示列。日志证据同时展示归一化本地时间和原始时间,
避免服务日志使用 UTC 时发生错误关联。

最终 Markdown 的标题层级固定为:

1. 唯一 H1 为 `# 详细结果`。
2. H1 下方直接放置用例结果索引表。
3. 每个用例使用 `<a id="case-<CASE_ANCHOR>"></a>` 和
   `## <CASE_ID> <CASE_NAME>`。
4. 每个用例下只使用 `执行结果`、`测试目标`、`测试步骤`、`结果检查`、
   `创建的资源`、`关键日志输出` 这 6 个 H3 字段。

`CASE_ANCHOR` 从 Case ID 转为小写, 非 `[a-z0-9-]` 字符替换为 `-`, 连续 `-` 合并,
并保证本次运行内唯一。索引表的 `查看` 链接必须直接指向对应 H2 前的显式锚点。

## Functional Verification 功能验证

每个用例必须定义显式验证。按需覆盖:

- 资源终态, 不只验证资源存在。
- Request ID 与服务日志关联。
- Snapshot、clone、migration、retype、upload-to-image、rebuild 或 evacuation 的
  deterministic data 和 SHA-256。
- Server `ACTIVE`、guest readiness、登录和必要 guest command。
- 加密操作的 source key ID、requested key ID、target key ID 和 source key 不变性。
- Migration、evacuation、detach 或恢复场景的源目标主机残留。

不得记录完整 key、Secret payload 或可逆 key material。

## Resource Ledger 资源台账

资源创建后立即写入用例级和运行级台账, 不等待用例结束。至少支持:

```text
Server
Volume
Snapshot
Image
Secret
Port
Floating IP
Attachment
Migration
Cache Volume
Temporary scheduling resource
```

记录 type、name、UUID、project、status、host/backend、`created_local`、`timezone`、
owning case、owning step、依赖、cleanup policy 和 final state。报告不得只列 UUID
而省略资源名称。
Floating IP 没有 name 字段时, 使用 `floating_ip_address` 作为资源名称。Server
记录绑定的 Floating IP UUID/address 和实际 force delete 命令。

## Internal Path Evidence 内部路径证据

API 或 UI 无法展示的关键内部执行分支必须用日志直接证明。例如创建云硬盘是否进入
clone、image copy、snapshot copy、Cache hit 或 Cache miss 路径。

每项分支证据记录:

```text
step_id
expected_path
observed_path
request_id
resource_id
service
instance
pod
container
timestamp_local
raw_timestamp
source_timezone
source_path
redacted_log_excerpt
```

在用例需要验证内部路径时, 于 `result.md` 的 `关键日志输出` 贴入最小充分日志原文,
同时链接完整 `related.log`。原文必须脱敏, 并保留能识别分支的关键函数、操作名、
Request ID 和资源 ID。没有直接日志证据时将该路径检查标为 `未确认`, 并设置
`evidence_status` 告警; 不根据资源终态反推内部实现路径, 也不覆盖已经确定的
`functional_status`。

用例不需要日志验证且执行过程没有失败时, 不强制收集服务日志。在 `关键日志输出`
明确写 `不适用: 本用例无需日志验证`, 并设置 `evidence_status=NOT_APPLICABLE`。

## Cleanup Policies 清理策略

支持:

```text
preserve_all
preserve_on_failure
cleanup_on_success
cleanup_all
explicit_per_case
```

清理只能在证据收集后进行, 并按逆依赖顺序执行。不得删除非本次运行创建的资源,
除非用例明确声明它是可删除 fixture。

清理失败时保留资源记录并设置:

```text
cleanup_status=PARTIAL
```

## Output Layout 输出目录

`<RESULT_ROOT>` 格式为 `easystack-test-<RunID>`, 其中 `RunID` 为
`R<YYYYMMDDHHmmss>` (精确到秒, 24 小时制本地时间)。例如
`easystack-test-R20260723150830`。

`summary.md` 是给人看的单文件详细结果, 人只读这一个文件即可查看索引和全部用例。
`results.csv` 是索引及诊断字段的机器可读记录, `run.json` 保存运行级元数据。
`cases/<CASE_ID>/result.md` 保存对应 H2 用例 section 的独立副本, 供单用例深查和证据
锚点引用。各处的 `执行结果` 必须一致。

```text
<RESULT_ROOT>/
├── environment.yaml
├── environment-summary.md
├── service-inventory.json
├── feature-impact.yaml
├── normalized-cases.yaml
├── run.json
├── summary.md
├── results.csv
├── resources-all.json
├── log-coverage.csv
├── run-logs/
└── cases/
    └── <CASE_ID>/
        ├── case.yaml
        ├── result.md
        ├── result.json
        ├── resources.json
        ├── correlation.json
        ├── commands.jsonl
        ├── commands.log
        ├── verification/
        ├── openstack/
        ├── host/
        └── logs/
            ├── window.json
            ├── inventory-before.json
            ├── inventory-after.json
            ├── collection-status.csv
            ├── raw/
            ├── merged.log
            ├── related.log
            └── errors.log
```

## Detailed Results 详细结果

严格使用 [`../examples/result-template.md`](../examples/result-template.md) 生成
`summary.md`。文件从 `# 详细结果` 开始, 紧接用例结果索引表, 再依次写入所有 H2
用例 section。不得在 H1 和索引表之间插入运行头或其它 section。

使用 resumable harness 时, 先填写 `cases/<CASE_ID>/result.json`, 再运行
`scripts/render-report.py`; 不手工修改生成的 `result.md`、`summary.md`、
`results.csv` 或 `run.json`。运行结束前使用 `scripts/validate-run.py` 检查索引、
标题层级、状态映射和结构化文件一致性。

索引表每个用例一行, 按 `case_id` 排序, 至少包含:

```text
case_id
title
execution_result
result_link
```

`execution_result` 只显示 `成功` 或 `失败`。`result_link` 使用归一化后的
`#case-<CASE_ANCHOR>`, 必须能跳转到对应 H2 前的显式锚点。索引中不得遗漏已开始的
用例。

每个 H2 用例 section 只包含以下 6 个 H3, 顺序固定:

1. `执行结果`: 第一行只按 `functional_status` 写 `成功` 或 `失败`; 步骤时间或关键
   日志存在异常时, 下一行必须增加一条简短 `说明:`, 没有异常时不添加。
2. `测试目标`: 写明被测功能、影响范围和关键预期。
3. `测试步骤`: 逐步记录详细操作、开始时间、结束时间、耗时、return code 和结果。
4. `结果检查`: 记录 Expected、Actual、检查结果和证据路径。Functional check 使用
   `成功` 或 `失败`; 时间、证据和清理质量使用 `告警` 或 `不适用`, 不覆盖功能结果。
5. `创建的资源`: 记录资源类型、名称、UUID、创建时间、所属步骤、host/backend、
   final state 和 cleanup 结果。
6. `关键日志输出`: 用例需要内部路径证据或发生失败时, 贴入最小充分 worker 日志,
   同时记录本地时间、原始 timestamp、Pod/Container、关联 ID 和证据路径; 不需要
   日志时明确写 `不适用`。

运行元数据、影响统计和完整诊断字段写入 `run.json`、`results.csv` 及其它结构化
文件, 不在最终 Markdown 中新增 H2/H3。`cases/<CASE_ID>/result.md` 只保存对应 H2
section, 内容必须与 `summary.md` 一致。

`results.csv` 至少包含 `case_id`、`title`、`execution_result`、`functional_status`、
`evidence_status`、`timing_status`、`cleanup_status`、`diagnostic_status`、用例本地时间和
`result_link`。任何结果改变时同步更新 `summary.md`、`results.csv` 和 `run.json`。

`run.json` 至少包含运行级元数据:

```text
run_id
result_root
plan_version
timezone
utc_offset
started_local
ended_local
total_cases
result_counts[success|failure]
diagnostic_counts[blocked|inconclusive]
cleanup_policy
remaining_resources
summary_path
results_csv_path
```

`log-coverage.csv` 至少包含:

```text
case_id
service
window_start_local
window_end_local
timezone
instances_before
instances_after
instances_expected
instances_collected
previous_streams_expected
previous_streams_collected
restart_detected
replacement_detected
evidence_status
```
