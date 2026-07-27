# Harness Evals

这些 eval 用于回归 skill 的高风险行为, 不代替 live OpenStack 测试。

- `evals.json` 是标准 model eval, 覆盖发散分析、负向测试、严格报告、context
  compaction、event recovery 和负触发路由。
- `cases.json` 保留为早期静态 runner 的兼容输入。
- 更新主流程、影响矩阵或报告状态后, 使用同一模型分别执行每个 prompt。
- `evals.json` 使用 `expectations`; `cases.json` 仅使用 `must_include`, 不混用字段。
- 结果必须满足全部 expectation 语义, 且不得越过用户授权执行环境变更。
- 至少重复 3 次检查长任务中的格式和 phase 遵循率。
- 脚本单元测试覆盖 deterministic harness; model eval 覆盖 skill 理解和测试发散。

先验证定义:

```bash
python3 scripts/validate-evals.py
```

Model 输出保存为 `<RESULTS>/eval-<ID>/run-<N>.md`, 每个 eval 至少 3 次。完成实际
model run 和人工 grading 后执行:

```bash
python3 scripts/validate-evals.py --results <RESULTS> --repeats 3
```

命令只校验定义、重复次数、非空输出和 artifact hash, 不用关键词命中代替语义
grading。没有真实输出时不得生成或提交伪造 benchmark。
