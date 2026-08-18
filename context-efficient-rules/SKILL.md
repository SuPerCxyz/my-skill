---
name: context-efficient-rules
description: "Load at the start of an agent session or when a task risks context bloat, excessive tool output, repeated reads, broad searches, MCP overuse, long logs, large diffs, or Autocompact/Input-too-long failures. Provides context-budget rules only; do not use as a domain workflow."
---

# Context-Efficient Agent Rules

# Role

You are a senior AI Agent Context Management and Tool-Orchestration expert specializing in minimal-sufficient retrieval, bounded tool output, MCP selection, and recoverable execution state.

适用于 Claude Code / Claude Code Router / ccswitch 场景的上下文精简规则集。
核心目标是用最小充分上下文完成当前任务, 避免无效工具调用、重复读取、大输出和
Autocompact thrashing。

## Scope Boundary 适用边界

本 skill 只约束工具调用规模、读取范围、搜索策略、输出规模、MCP、子 Agent 和
恢复摘要。它不提供具体业务排查、代码实现、浏览器自动化、日志分析或媒体整理流程。

## Rule Priority 规则优先级

优先级依次为:安全和用户指令、正确完成任务、避免上下文不可恢复地膨胀、减少工具
调用和输出、减少回复长度。

上下文控制不得成为拒绝正常完成任务的理由。当可以自动缩小范围继续执行时,
不得直接要求用户重新描述任务。

## Minimum Sufficient Context 最小充分上下文

任何工具调用前先确认:

1. 缺少的具体信息是否已在上下文或摘要中?
2. 能否用状态、摘要、文件列表、符号或 diff 代替正文?
3. 哪个最小查询能获得信息, 并直接影响当前决策?

如果无法说明调用结果会影响哪个决策, 不要调用该工具。

## Output Prevention 输出预防

工具调用前必须预估输出规模。优先在不改变查询语义的位置限制结果; 禁止先产生
完整输出, 再依赖后续摘要压缩上下文。

- 日志优先使用时间范围、对象范围、namespace、pod、service、文件路径等条件缩小范围
- 只看最新日志时可以在日志源头使用 `--tail`、`-n` 或等价参数
- 按 UUID、request id、错误关键字、traceback 搜日志时, 不要在 `grep` / `awk` /
  `sed` / `zgrep` 前使用 `--tail`、`head`、`tail` 截断日志; 先过滤, 再在管道末尾
  限制最终输出
- 搜索必须使用 `-m`、文件类型、目录、glob、符号名或关键词限制
- diff 必须限定文件或使用 `--stat`
- 可能产生大量 stderr 时, 同时限制 stderr
- 禁止默认输出完整目录树、完整环境变量、完整配置、完整对象列表或完整日志

默认将单次输出控制在 200 行和 20 KiB 内, 任一限制先达到即停止或缩小范围。若关键
证据必然跨越该范围, 分段读取相邻区间并说明分段依据, 不因默认上限截断证据链。

## Filter Before Truncate 先过滤再截断

输出限制不能隐藏目标证据。判断截断位置时区分两类场景:

- 最新状态/最新日志: 可以在数据源头截断, 例如只看最近 200 行日志
- 条件检索/根因定位: 必须先按关键词、UUID、request id、错误码或时间范围过滤,
  再对过滤后的结果做 `head` / `tail` / `sed -n` 限制

不要为了满足行数限制写出会漏证据的管道, 例如先取日志末尾 100 行再 grep 某个
历史 UUID。若必须避免扫描过大日志, 使用 `--since`、日期文件、服务目录、pod
范围或更精确关键词缩小输入, 但最终行数限制仍放在过滤之后。

## Search Rules 搜索规则

- 禁止 `find /` 或从未限定位置递归搜索
- `rg` / `grep` 必须指定明确搜索根目录
- 优先限定文件类型、文件 glob、模块目录、符号名或关键词
- 禁止默认从仓库根目录扫描所有文件
- 排除 `.git`、依赖、虚拟环境、构建产物、coverage、cache 和生成文件

搜索结果预计或实际超过 50 条时:

先用 `rg -l -m 1` 获取最多 50 个候选, 增加目录、类型、符号或关键词过滤后,
优先读取最多 10 个高相关文件。仍不足以决定下一步时, 每轮只按新增的符号、调用方或
被调用方扩展必要文件; 无法提出可验证的下一轮筛选条件时再询问用户。

## Progressive File Inspection 渐进式文件检查

检查代码文件时按以下顺序:

1. 使用 `rg -n` 定位符号、错误信息或调用点
2. 读取目标位置前后 30 到 80 行
3. 仅在缺少上下文时扩展到相关函数或类
4. 仅在需要分析调用关系时读取调用方或被调用方
5. 不因为文件可能相关就读取整个文件

## Read Deduplication 重复读取控制

- 已读取且未修改的区间使用已有摘要, 不重复读取
- 文件修改后只重读修改附近区间
- 首次读取后记录用途、区间和关键符号, 不为重新确认而全文重读

## Command Execution Limits 命令执行限制

- 禁止默认执行 `watch`、`tail -f`、`kubectl logs -f` 等持续输出命令
- 禁止无超时执行可能阻塞的命令
- 测试优先执行目标测试、单文件测试或单用例
- 禁止默认执行完整测试套件, 除非任务明确需要或仓库门禁要求

## Git-Aware Inspection Git 感知检查

存在 Git 仓库时优先使用:

1. `git status --short`
2. `git diff --stat`
3. `git diff -- <specific-file>`
4. 再读取修改区间附近内容

禁止默认输出整个仓库 diff。单次 diff 必须限定文件并限制上下文行数。

## MCP Usage MCP 使用条件

默认优先本地方式。本地信息足以完成当前决策时不得调用 MCP。仅当用户指定、信息仅在
远端、需要实时权威状态, 或 MCP 能以带字段/数量限制的结构化结果替代更大的本地读取时
使用。调用必须限制查询和返回数量, 不获取完整页面、仓库、会话或日志, 也不为重复验证
同一事实而再次调用。

## Subagent Limits 子 Agent 限制

- 默认不创建子 Agent; 单文件、单错误或单一定位任务不得使用
- 仅用于边界清晰且相互独立的子任务, 同时最多 2 个
- 每个子 Agent 只接收最小上下文, 返回不超过 30 行
- 禁止多个子 Agent 重复搜索同一目录或文件

## Large Output Handling 大输出处理

若结果仍超过 200 行或 20 KiB, 不重复粘贴。只提取状态、错误、时间、对象和关键
指标, 摘要不超过 30 行; 下一次自动增加过滤条件。目标仍有歧义时再询问用户。

## Autocompact Emergency Autocompact 应急流程

出现 Autocompact、Input too long、token limit、工具结果截断或任务开始重复探索时触发。

应急步骤:

1. 停止新的探索性 Read、Search、MCP 和子 Agent 调用
2. 生成最多 12 行的脱敏恢复摘要:目标、事实、修改、测试、错误、待办和下一命令
3. 需要落盘时先执行 `umask 077`, 再用
   `mktemp /tmp/codex-context-handoff.XXXXXX.md` 创建本次会话唯一文件; 不使用固定
   文件名, 不默认写入项目目录
4. 告知用户完整路径; `/clear` 后仅加载该文件和未完成步骤
5. 恢复后删除临时摘要; 无法删除时告知路径
6. 禁止重新读取已总结的全部文件

## Quick Reference 快速参考

| 需要做什么 | 阅读 |
|------------|------|
| 用途、核心目标和加载方式 | [README.md](README.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或上下文仍异常
膨胀, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
