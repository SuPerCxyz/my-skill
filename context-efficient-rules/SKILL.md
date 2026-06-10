---
name: context-efficient-rules
description: "Context-efficient agent rules for Claude Code / Claude Code Router / ccswitch. Enforces minimal context usage: no MCP by default, no large file reads, no broad searches. Provides domain-specific compact rules for Kubernetes, OpenStack, Git, log analysis, and GUI testing. Includes a CLAUDE.md / AGENTS.md embeddable snippet."
---

# Context-Efficient Agent Rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的精简 Agent 规则集。核心目标：控制上下文膨胀，避免 Autocompact thrashing 和 Input too long。

## 核心硬规则

以下规则优先级最高，任何任务开始前必须遵守。

### 工具调用限制

1. **默认不调用 MCP** — 仅在以下情况才允许调用 MCP 工具：
   - 用户明确要求使用某个 MCP 工具
   - 本地文件/命令完全无法获取所需信息
   - 调用前必须用一句话说明为什么必须用 MCP

2. **默认不读取大文件** — Read 工具使用规则：
   - 必须指定 `offset` 和 `limit`，禁止全文件读取
   - 单次读取不超过 200 行
   - 首次只读关键片段（函数签名、类定义、入口点），按需扩展

3. **默认不执行大范围搜索** — 搜索规则：
   - 禁止 `find /` 或无目录范围的 `rg`
   - `rg` / `grep` 必须指定搜索目录，且目录层级 ≤ 3
   - 搜索结果超过 50 行时，停止输出并要求用户缩小范围

4. **工具输出限制 200 行** — 任何 Bash / Read / MCP 工具输出：
   - 管道 `| head -200` 或 `| tail -200` 截断
   - 超长输出必须先摘要（提取关键行）再继续
   - 禁止将完整日志 / 完整文件内容贴入上下文

### Autocompact 防护

当出现以下信号时，立即执行应急措施：
- 系统提示 `Autocompact` 或 `compacting context`
- 用户反馈 `Input too long` / token 超限
- 单次回复生成时间明显变长

应急措施（按顺序）：
1. **立即停止扩大上下文** — 不再调用任何 Read / Search / MCP 工具
2. **输出当前进度摘要**（不超过 10 行）
3. **建议用户执行 `/clear`** 或缩小任务范围
4. 若用户拒绝 `/clear`，切换为极简模式：只做当前步骤，不做任何额外探索

### 大输出处理流程

```
工具输出 > 200 行?
  ├─ 是 → 提取关键信息（错误行、状态码、关键指标）
  │       输出摘要（≤ 30 行）
  │       询问用户是否需要查看特定部分
  └─ 否 → 正常处理
```

## 领域精简规则

不同场景有专属精简规则，按需查阅：

| 场景 | 规则文件 | 核心要点 |
|------|----------|----------|
| Kubernetes | [domain-rules/k8s.md](domain-rules/k8s.md) | 只读 kubectl get，定向日志，不 describe 全量 |
| OpenStack | [domain-rules/openstack.md](domain-rules/openstack.md) | CLI 输出截断，定向 API 查询 |
| Git | [domain-rules/git.md](domain-rules/git.md) | 浅 log，定向 diff，不 fetch 全量 |
| 日志分析 | [domain-rules/logs.md](domain-rules/logs.md) | grep 先行，tail 限制，不读完整日志 |
| GUI 测试 | [domain-rules/gui-testing.md](domain-rules/gui-testing.md) | snapshot 优先，不截图全页，定向交互 |

## CLAUDE.md / AGENTS.md 嵌入片段

以下精简版可直接粘贴到项目 `CLAUDE.md` 或 `AGENTS.md` 中：

```markdown
## Context-Efficient Rules (Claude Code / Router / ccswitch)

### 工具调用
- 默认不调用 MCP，除非本地手段无法获取信息
- 默认不读取大文件，Read 必须指定 offset/limit，单次 ≤ 200 行
- 默认不执行大范围搜索，rg/grep 必须指定目录且 ≤ 3 层
- 调用 MCP 前必须用一句话说明必要性
- 工具输出截断到 200 行以内，超长先摘要再继续

### Autocompact 防护
- 遇到 Autocompact / Input too long 时：立即停止扩大上下文
- 输出 ≤ 10 行进度摘要，建议 /clear 或缩小任务范围

### 领域规则
- K8s: kubectl get --no-headers -o wide，日志用 --tail=100，禁止 kubectl describe 全量输出
- OpenStack: CLI 输出 | head -100，用 --column 指定字段，避免 list 全量
- Git: log --oneline -20，diff 指定文件范围，禁止无范围 fetch/clone
- 日志: grep 先行定位，tail -n 200 截断，禁止 cat 完整日志文件
- GUI: snapshot 代替 screenshot，定向元素交互，禁止全页截图反复迭代
```

## 任务分流（精简版）

| 任务类型 | 流程 | 允许的工具 |
|----------|------|------------|
| 只读分析 | 直接回答 | Read(limit≤200), rg(指定目录) |
| 轻量修改 | 直接实现+验证 | Read, Edit, Bash(截断输出) |
| 中任务 | 简短 plan → 实现 → 验证 | 同上，可加 subagent |
| 大任务 | plan → 实现 → review → verify | 同上，分步执行，每步清理上下文 |

## 输出规范

- 结论前置，依据后置
- 单次输出不超过 100 行，超出则分块
- 代码示例聚焦核心逻辑，省略无关部分
- 最终总结：改了什么 / 如何验证 / 未验证项 / 风险
