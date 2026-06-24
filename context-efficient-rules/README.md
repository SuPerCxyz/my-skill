# context-efficient-rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的上下文精简 Agent 规则集。

## 核心目标

- 控制上下文膨胀，避免 Autocompact thrashing 和 Input too long
- 默认不调用 MCP、不读大文件、不做大范围搜索
- 工具输出限制 200 行以内，大输出先摘要再继续
- 含工具调用限制、Autocompact 防护、大输出处理流程等核心硬规则

## 文件结构

```
context-efficient-rules/
├── SKILL.md      # 主入口:核心硬规则(工具调用限制、Autocompact 防护、大输出处理)
└── README.md     # 本文件
```

## 使用方式

- 作为 Skill 使用:由 `AGENTS.md` 在对话开始时显式加载，按 `SKILL.md` 中的核心硬规则执行
- 也可将 `SKILL.md` 内容复制进 `CLAUDE.md` / 项目 `AGENTS.md` 作为常驻规则
