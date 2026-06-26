---
name: context-efficient-rules
description: "Load at the start of an agent session or when a task risks context bloat, excessive tool output, broad searches, or unnecessary MCP usage. Provides context-budget rules only; do not use as a domain workflow for coding, debugging, UI automation, log analysis, or media organization."
---

# Context-Efficient Agent Rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的精简 Agent 规则集。核心目标:控制上下文膨胀，避免 Autocompact thrashing 和 Input too long。

## Scope Boundary 适用边界

使用本 skill 管理工具调用规模、搜索范围、读取行数和长输出处理。它只约束上下文使用方式, 不提供具体业务排查、代码实现、浏览器自动化、Windows 桌面操作、日志分析或媒体库整理流程。

## Core Hard Rules 核心硬规则

以下规则优先级最高，任何任务开始前必须遵守。

### Tool Call Limits 工具调用限制

1. **默认不调用 MCP** — 仅在以下情况才允许调用 MCP 工具:
   - 用户明确要求使用某个 MCP 工具
   - 本地文件/命令完全无法获取所需信息
   - 调用前必须用一句话说明为什么必须用 MCP

2. **默认不读取大文件** — Read 工具使用规则:
   - 必须指定 `offset` 和 `limit`，禁止全文件读取
   - 单次读取不超过 200 行
   - 首次只读关键片段(函数签名、类定义、入口点)，按需扩展

3. **默认不执行大范围搜索** — 搜索规则:
   - 禁止 `find /` 或无目录范围的 `rg`
   - `rg` / `grep` 必须指定搜索目录，且目录层级 ≤ 3
   - 搜索结果超过 50 行时，停止输出并要求用户缩小范围

4. **工具输出限制 200 行** — 任何 Bash / Read / MCP 工具输出:
   - 管道 `| head -200` 或 `| tail -200` 截断
   - 超长输出必须先摘要(提取关键行)再继续
   - 禁止将完整日志 / 完整文件内容贴入上下文

### Autocompact Protection Autocompact 防护

当出现以下信号时，立即执行应急措施:
- 系统提示 `Autocompact` 或 `compacting context`
- 用户反馈 `Input too long` / token 超限
- 单次回复生成时间明显变长

应急措施(按顺序):
1. **立即停止扩大上下文** — 不再调用任何 Read / Search / MCP 工具
2. **输出当前进度摘要**(不超过 10 行)
3. **建议用户执行 `/clear`** 或缩小任务范围
4. 若用户拒绝 `/clear`，切换为极简模式:只做当前步骤，不做任何额外探索

### Large Output Handling 大输出处理流程

```
工具输出 > 200 行?
  ├─ 是 → 提取关键信息(错误行、状态码、关键指标)
  │       输出摘要(≤ 30 行)
  │       询问用户是否需要查看特定部分
  └─ 否 → 正常处理
```
