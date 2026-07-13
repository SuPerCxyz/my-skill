# context-efficient-rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的上下文精简 Agent 规则集。它只约束工具调用、读取范围、输出规模、MCP、子 Agent 和恢复摘要, 不替代具体业务 skill。

## 核心目标

- 调用前预估输出规模, 在不改变查询语义的位置限制行数和字节数
- 条件检索日志时先过滤再截断, 避免先 `tail` 后 `grep` 漏掉历史证据
- 先定位再读取, 避免重复读取和完整文件读取
- 搜索过宽时自动缩小范围, 不立即打断用户
- 约束 MCP、Bash、Git diff、测试命令和子 Agent 使用
- Autocompact 前生成脱敏、权限为 `0600` 的可恢复摘要, 恢复后删除临时文件

## 文件结构

```
context-efficient-rules/
├── SKILL.md      # 主入口:上下文预算、输出预防、搜索/读取/MCP/子 Agent/恢复规则
└── README.md     # 本文件
```

## 使用方式

- 作为 Skill 使用:由 `AGENTS.md` 在对话开始时显式加载, 按 `SKILL.md` 中的核心硬规则执行
- 也可将 `SKILL.md` 内容复制进 `CLAUDE.md` / 项目 `AGENTS.md` 作为常驻规则
