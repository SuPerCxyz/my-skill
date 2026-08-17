## Why

离线日志 skill 的主入口仍使用旧报告字段, 且解压文档对已有输出目录给出相反指令。跨域规则还无条件扩大到所有基础设施和操作历史日志, 与按证据构建最小调查链的目标不一致。

## What Changes

- 在离线调查主流程开始时先读取共享报告格式并规划证据链。
- 将离线报告入口同步到包含 `通俗说明` 和分层根因的当前报告契约。
- 统一同名 `ecs.*` 输出目录的覆盖式增量合并语义。
- 将跨域日志范围从固定全量扫描改为根据问题域和已发现信号逐层扩展。
- 将时间线项目明确为 `事件 N` 标签, 避免与章节裸数字序号冲突。

## Capabilities

### New Capabilities

- `offline-log-analysis-workflow`: 定义离线 bundle 解压合并、调查前置契约、证据驱动的日志范围扩展和报告输出一致性。

### Modified Capabilities

<!-- 既有 incident-root-cause-reporting requirement 不变, 本次仅使离线实现符合它。 -->

## Impact

影响 `easystack-log-analysis` 的主入口、解压说明和跨域分析指南。不修改解压脚本、共享报告模板、在线环境访问流程、依赖或运行时配置。
