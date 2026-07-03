---
name: context-efficient-rules
description: "Load at the start of an agent session or when a task risks context bloat, excessive tool output, repeated reads, broad searches, MCP overuse, long logs, large diffs, or Autocompact/Input-too-long failures. Provides context-budget rules only; do not use as a domain workflow."
---

# Context-Efficient Agent Rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的上下文精简规则集。
核心目标是用最小充分上下文完成当前任务, 避免无效工具调用、重复读取、大输出和
Autocompact thrashing。

## Scope Boundary 适用边界

本 skill 只约束工具调用规模、读取范围、搜索策略、输出规模、MCP、子 Agent 和
恢复摘要。它不提供具体业务排查、代码实现、浏览器自动化、日志分析或媒体整理流程。

## Rule Priority 规则优先级

1. 安全和用户明确指令
2. 正确完成当前任务
3. 防止上下文不可恢复地膨胀
4. 减少工具调用和输出
5. 减少回复长度

上下文控制不得成为拒绝正常完成任务的理由。当可以自动缩小范围继续执行时,
不得直接要求用户重新描述任务。

## Minimum Sufficient Context 最小充分上下文

任何工具调用前先确认:

1. 当前缺少的具体信息是什么?
2. 哪个最小查询可以获得该信息?
3. 该信息是否已经存在于当前上下文或已有摘要中?
4. 是否可用状态、摘要、文件列表、符号定位或 diff 代替正文读取?
5. 结果会直接影响哪个决策?

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

推荐限制:

- 单次输出不超过 200 行
- 同时不超过 20 KiB
- 任一限制先达到即停止或缩小范围

## Filter Before Truncate 先过滤再截断

输出限制不能隐藏目标证据。判断截断位置时区分两类场景:

- 最新状态/最新日志: 可以在数据源头截断, 例如只看最近 200 行日志
- 条件检索/根因定位: 必须先按关键词、UUID、request id、错误码或时间范围过滤,
  再对过滤后的结果做 `head` / `tail` / `sed -n` 限制

不要为了满足行数限制写出会漏证据的管道, 例如先取日志末尾 100 行再 grep 某个
历史 UUID。若必须避免扫描过大日志, 使用 `--since`、日期文件、服务目录、pod
范围或更精确关键词缩小输入, 但最终行数限制仍放在过滤之后。

## Search Rules 搜索规则

默认不做大范围搜索。

- 禁止 `find /` 或从未限定位置递归搜索
- `rg` / `grep` 必须指定明确搜索根目录
- 优先限定文件类型、文件 glob、模块目录、符号名或关键词
- 禁止默认从仓库根目录扫描所有文件
- 禁止搜索 `.git`、依赖目录、构建产物、缓存和生成文件

默认排除:

```text
.git
node_modules
vendor
dist
build
target
coverage
__pycache__
.venv
.tox
tox
```

搜索结果预计或实际超过 50 条时:

1. 不展示完整结果
2. 自动增加目录、文件类型、符号名或关键词限制
3. 先用 `rg -l -m 1` 获取候选文件列表
4. 根据相关度选取最多 10 个文件
5. 仍无法判断目标时, 再询问用户

示例:

```bash
rg -l -m 1 'VolumeDriver' cinder/ -g '*.py' | head -50
```

## Progressive File Inspection 渐进式文件检查

检查代码文件时按以下顺序:

1. 使用 `rg -n` 定位符号、错误信息或调用点
2. 读取目标位置前后 30 到 80 行
3. 仅在缺少上下文时扩展到相关函数或类
4. 仅在需要分析调用关系时读取调用方或被调用方
5. 不因为文件可能相关就读取整个文件

示例:

```bash
rg -n 'def attach_volume|class .*Driver' cinder/volume/drivers -g '*.py'
```

## Read Deduplication 重复读取控制

- 已读取且未修改的文件区间不得重复读取
- 后续需要引用时使用已有摘要, 不重新调用 Read
- 文件修改后只重新读取修改附近区间
- 不为了“重新确认”完整读取此前已经分析过的内容
- 每个文件首次读取后记录用途、已读区间、关键符号和可能相关但未读区间

## Command Execution Limits 命令执行限制

- 禁止默认执行 `watch`、`tail -f`、`kubectl logs -f` 等持续输出命令
- 禁止无超时执行可能阻塞的命令
- 测试优先执行目标测试、单文件测试或单用例
- 禁止默认执行完整测试套件, 除非任务明确需要或仓库门禁要求
- 日志命令必须指定时间范围、对象范围, 或在过滤后限制最终输出
- 按关键词/UUID 搜日志时, 最终 `head` / `tail` 放在 `grep` / `zgrep` 之后
- 禁止递归输出完整目录树
- 禁止输出完整环境变量、完整配置和完整对象列表
- 命令可能产生大量 stderr 时, 应同时限制 stderr

示例:

```bash
timeout 60 pytest tests/unit/test_driver.py::TestDriver::test_attach -q
journalctl -u ironic-conductor --since '10 minutes ago' -n 200 --no-pager
kubectl logs pod-name --since=10m --tail=200
journalctl -u cinder-volume --since '2 hours ago' --no-pager | grep -F '<volume-id>' | tail -200
kubectl logs pod-name --since=2h 2>&1 | grep -F '<resource-id>' -B 5 -A 20 | tail -200
command 2>&1 | grep -F '<keyword>' | head -200
```

## Git-Aware Inspection Git 感知检查

存在 Git 仓库时优先使用:

1. `git status --short`
2. `git diff --stat`
3. `git diff -- <specific-file>`
4. 再读取修改区间附近内容

禁止默认输出整个仓库 diff。单次 diff 必须限定文件并限制上下文行数。

示例:

```bash
git diff --unified=20 -- path/to/file.py | head -200
```

## MCP Usage MCP 使用条件

默认优先使用本地文件和本地命令。满足以下任一条件时可以使用 MCP:

- 用户明确指定 MCP
- 信息仅存在于远端服务、浏览器、桌面或连接系统中
- MCP 能以明显更少输出直接获得结构化结果
- 本地方式需要大范围搜索、抓取或解析才能得到同等信息
- 需要查询实时状态或权威远端状态

禁止仅为了“多验证一次”而重复调用 MCP。

调用 MCP 时必须:

- 使用最小查询范围
- 限定返回数量
- 禁止获取完整页面、完整仓库、完整会话或完整日志
- 仅当 MCP 调用涉及隐私、外部写操作或明显扩大任务范围时, 才向用户说明原因

## Subagent Limits 子 Agent 限制

- 默认不创建子 Agent
- 单一代码定位、单文件修改或单错误排查不得使用子 Agent
- 只有任务能明确拆分为相互独立部分时才允许使用
- 同时运行的子 Agent 不超过 2 个
- 每个子 Agent 只接收完成子任务所需的最小上下文
- 子 Agent 返回结果不得超过 30 行
- 禁止多个子 Agent 重复搜索同一目录或分析同一文件

## Large Output Handling 大输出处理

调用前判断输出是否可能超过 200 行或 20 KiB。

```text
可能超限?
  ├─ 是
  │  ├─ 增加时间、目录、文件、对象、关键词或数量限制
  │  ├─ 优先获取 count、stat、文件列表或错误摘要
  │  ├─ 只获取最多 50 个候选结果
  │  └─ 再读取最多 10 个高相关结果
  └─ 否
     └─ 正常调用
```

如果工具仍返回超限内容:

1. 不在回复中重复粘贴
2. 提取错误、状态码、时间、对象名和关键指标
3. 摘要不超过 30 行
4. 自动缩小下一次调用范围
5. 只有目标仍有歧义时才询问用户

## Autocompact Emergency Autocompact 应急流程

出现以下信号时触发:

- 系统出现 Autocompact 或 compacting context
- 出现 Input too long 或 token limit 提示
- 连续多次摘要后仍无法继续调用工具
- 工具结果被截断
- 任务开始重复读取或重复搜索已经分析过的内容

应急步骤:

1. 立即停止新的探索性 Read、Search、MCP 和子 Agent 调用
2. 输出或保存恢复摘要, 最多 12 行, 包含当前目标、已确认事实、已修改文件、
   已执行测试、当前错误、未完成事项和下一条建议命令
3. 可将恢复摘要写入 `/tmp/claude-context-handoff.md`, 不默认写入项目目录
4. 用户执行 `/clear` 后, 仅加载该恢复摘要
5. 禁止重新读取已经总结过的所有文件
6. 仅恢复当前未完成步骤
