# Reporting

## Result Model 结果模型

最终状态使用:

- `PASS`: 功能符合预期, 且必需证据完整。
- `FAIL`: 实际行为与预期不符, 或操作意外失败。
- `BLOCKED`: 必需前置条件、依赖或授权不可用。
- `INCONCLUSIVE`: 存在功能信号, 但证据不足以可靠判断。

同时记录:

```text
functional_status
evidence_status
cleanup_status
```

不得将证据缺失折叠为功能通过。

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

在 `result.md` 贴入最小充分日志原文, 同时链接完整 `related.log`。原文必须脱敏,
并保留能识别分支的关键函数、操作名、Request ID 和资源 ID。没有直接日志证据时
将分支验证标为 `INCONCLUSIVE`, 不根据资源终态反推内部实现路径。

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

`<RESULT_ROOT>` 格式为 `easystack-test-<RunID>`，其中 `RunID` 为 `R<YYYYMMDDHHmmss>` (精确到秒, 24 小时制本地时间)。例如 `easystack-test-R20260723150830`。

`summary.md` 是给人看的单文件全量报告, 包含运行汇总和全部用例的执行结果与细节, 人只读这一个文件即可, 无需逐个进入 `cases/` 目录。`results.csv` 是同内容的机器可读镜像, `run.json` 是运行级元数据。`cases/<CASE_ID>/result.md` 是同一用例结果的独立副本, 供单用例深查和证据锚点引用, 内容与 `summary.md` 中对应 section 一致。三者保持一致, 不出现只存在于一处的用例状态。

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

## Per-Case Result 单用例结果

严格使用 [`../examples/result-template.md`](../examples/result-template.md)。模板字段按
本文件的结果、时间、资源、内部路径和清理规则填写; 中文解释中保留英文专业术语。

## Run Summary 运行汇总

`summary.md` 是给人看的单文件全量报告, 必须按以下顺序组织, 确保单文件即可看到每个
用例的状态、时间、完整细节和运行汇总, 无需逐个进入 `cases/` 目录:

1. 运行头: Run ID、`<RESULT_ROOT>` 绝对路径、计划版本、IANA timezone、UTC offset、
   运行 `started_local` 和 `ended_local`、清理策略。
2. 用例结果索引表: 每个用例一行, 并按 `overall_status` 排序 (`FAIL`、`BLOCKED`、
   `INCONCLUSIVE`、`PASS`)。列至少包含:
   ```text
   case_id
   title
   domain
   attempt
   overall_status
   functional_status
   evidence_status
   cleanup_status
   case_start_local
   case_end_local
   case_duration_ms
   result_link
   ```
   `result_link` 为同文件内锚点 `#case-<CASE_ID>`, 跳转到该用例详情 section。展示本地
   时间, UTC 仅用于日志窗口边界。单页列出所有用例, 不折叠也不省略。
3. 运行汇总: 四态统计、按 domain/backend/compute host 的分组结果、服务日志覆盖率和
   实例重启或替换、清理状态、剩余资源台账入口和最高优先级失败。
4. 全部用例详情: 索引表之后, 依次将每个用例按
   [`../examples/result-template.md`](../examples/result-template.md) 完整内联为一个
   `## <CASE_ID> <title>` section, 并设锚点 `case-<CASE_ID>` 供索引表跳转。步骤时间、
   资源、证据、内部路径和清理结果全部写入此 section, 不指向其它文件即可看完。
5. 每项结论的证据路径 (相对 `<RESULT_ROOT>`)。

`results.csv` 是用例结果索引表的机器可读镜像，列与上表一致，UTF-8、含表头、按
`case_id` 排序。任何用例的 `overall_status` 改变时同步更新 `summary.md` 和
`results.csv`。

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
status_counts[pass|fail|blocked|inconclusive]
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
