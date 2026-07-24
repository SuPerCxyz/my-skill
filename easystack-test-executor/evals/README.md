# Harness Evals

这些 eval 用于回归 skill 的高风险行为, 不代替 live OpenStack 测试。

- `evals.json` 是标准 model eval, 覆盖发散分析、负向测试、严格报告、context
  compaction、event recovery 和负触发路由。
- `cases.json` 保留为早期静态 runner 的兼容输入。
- 更新主流程、影响矩阵或报告状态后, 使用同一模型分别执行每个 prompt。
- 结果必须包含全部 `must_include` 语义, 且不得越过用户授权执行环境变更。
- 至少重复 3 次检查长任务中的格式和 phase 遵循率。
- 脚本单元测试覆盖 deterministic harness; model eval 覆盖 skill 理解和测试发散。
