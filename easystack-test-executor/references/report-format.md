# Report Format

## Fixed Hierarchy 固定层级

最终中文 Markdown 必须严格满足:

1. 唯一 H1 为 `# 详细结果`。
2. H1 后直接放用例结果索引表。
3. 每个用例标题是 H2: `## <CASE_ID> <中文用例名称>`。
4. 每个用例只有 6 个 H3, 且顺序固定:
   `执行结果`、`测试目标`、`测试步骤`、`结果检查`、`创建的资源`、`关键日志输出`。

索引 header 必须逐字为:

```markdown
| 用例 ID | 用例名称 | 测试需求 | 执行结果 | 跳转 |
```

每行依次使用 `case_id`、中文 `title`、一句中文 `requirement_summary`、成功/失败和
`[查看](#case-<anchor>)`。索引顺序取自 contract。H2 前必须有:

```html
<a id="case-<anchor>"></a>
```

anchor 由 Case ID 小写归一化产生, 本次运行内必须唯一。

## Case Fields 用例字段

`scenario_key` 是 ASCII 技术组合标识, 不作为中文名称。`title` 必须为 2-40 个字符的
中文可读名称。`requirement_summary` 必须为 6-60 个字符的一句中文需求。

每个 H3 内容:

1. `执行结果`: 第一行只写成功或失败。Timing 或 required Evidence 异常时下一段写
   `说明: 步骤时间记录异常; 关键日志未完整保存。`
2. `测试目标`: 依次写 `测试需求:`、`场景标识:` 和 `详细目标:`。
3. `测试步骤`: 按 contract 顺序记录 Step、Attempt、Command ID、操作、Start local、
   End local、Duration ms、Return code 和结果。未执行、skip、失败和重试均不得删除。
4. `结果检查`: 表格记录检查项、Expected、Actual、结果和 Evidence。
5. `创建的资源`: 表格记录 Type、Name、UUID、Created local、所属 Case/Step、
   Host/Backend、Final state 和 Cleanup。
6. `关键日志输出`: 表格记录 Local time、Raw timestamp、Service/Pod/Container、
   Request/Resource ID 和证据路径, 后附最小充分 excerpt。

optional 日志未采集时写 `可选日志未收集, 不影响功能结果。`。none 日志写
`不适用: 本用例无需日志验证。`

## Consistency 一致性

- `result.md` 必须是 `summary.md` 中该用例 section 的逐字副本。
- `results.csv` 的名称、需求、结果和 link 必须与 Markdown 一致。
- `run.json` 的 case count 和 success/failure count 必须与结果一致。
- 报告中不得增加额外 H2/H3, 运行级诊断写入结构化文件。
- 原始 stdout/stderr 和 worker logs 只保存文件, 报告仅引用脱敏的最小证据。
