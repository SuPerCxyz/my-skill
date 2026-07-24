# 详细结果

| 用例 ID | 用例名称 | 测试需求 | 执行结果 | 跳转 |
|---------|----------|----------|----------|------|
| <CASE_ID> | <简短中文名称> | <一句简短中文测试需求> | <成功或失败> | [查看](#case-<CASE_ANCHOR>) |

<a id="case-<CASE_ANCHOR>"></a>
## <CASE_ID> <简短中文名称>

### 执行结果

<成功或失败>

说明: <仅在步骤时间或关键日志存在异常时简要填写; 无异常时删除本行>

### 测试目标

测试需求: <与索引完全相同的一句简短中文测试需求>

场景标识: `<SCENARIO_KEY>`

详细目标: <说明被测功能、影响范围和关键预期>

### 测试步骤

| Step | Attempt | Command ID | 详细操作或命令 | Start local | End local | Duration ms | Return code | 结果 |
|------|---------|------------|----------------|-------------|-----------|-------------|-------------|------|
| <STEP_ID> | attempt-01 | <COMMAND_ID> | <脱敏后的操作或命令> | <RFC3339+offset> | <RFC3339+offset> | <N> | <RC> | <成功或失败> |

### 结果检查

| 检查项 | Expected | Actual | 结果 | Evidence |
|--------|----------|--------|------|----------|
| <CHECK> | <EXPECTED> | <ACTUAL> | <成功、失败、告警或不适用> | <相对证据路径或关联 ID> |

功能断言决定 `执行结果`; 时间、日志和清理质量异常使用 `告警`, 不覆盖已确定的
功能结果。

### 创建的资源

| Type | Name | UUID | Created local | 所属 Step | Host 或 Backend | Final state | Cleanup |
|------|------|------|---------------|-----------|-----------------|-------------|---------|
| <RESOURCE_TYPE> | <RESOURCE_NAME> | <UUID> | <RFC3339+offset> | <STEP_ID> | <HOST_OR_BACKEND> | <STATE> | <RESULT> |

### 关键日志输出

| Local time | Raw timestamp | Service/Pod/Container | Request 或 Resource ID | 证据路径 |
|------------|---------------|-----------------------|------------------------|----------|
| <RFC3339+offset> | <RAW_TIMESTAMP> | <SERVICE/POD/CONTAINER> | <REQUEST_OR_RESOURCE_ID> | <RELATIVE_PATH> |

```text
<证明关键执行路径或失败原因的最小充分脱敏日志原文>
```

内部执行分支无法由 API 或 UI 直接确认时, 必须在本节写明 Expected path、Observed
path、worker instance 和日志结论。不需要日志时写 `不适用: 本用例无需日志验证`。
日志为 optional 且未采集时写 `可选日志未收集, 不影响功能结果。`, 不写关键日志
缺失说明。
按上述结构重复添加其余用例的索引行和 H2 section。

`用例名称` 必须是 2-40 个字符的中文可读名称, `测试需求` 必须是 6-60 个字符的单行
中文句子。禁止使用 `-`、`N/A`、`TBD`、纯英文组合名或其它占位符。
