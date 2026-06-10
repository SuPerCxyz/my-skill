# context-efficient-rules

适用于 Claude Code / Claude Code Router / ccswitch 场景的上下文精简 Agent 规则集。

## 核心目标

- 控制上下文膨胀，避免 Autocompact thrashing 和 Input too long
- 默认不调用 MCP、不读大文件、不做大范围搜索
- 工具输出限制 200 行以内，大输出先摘要再继续
- 为 K8s / OpenStack / Git / 日志 / GUI 测试提供领域专属精简规则

## 文件结构

```
context-efficient-rules/
├── SKILL.md                         # 主入口：核心硬规则 + CLAUDE.md 嵌入片段
├── README.md                        # 本文件
└── domain-rules/
    ├── k8s.md                       # Kubernetes 精简规则
    ├── openstack.md                 # OpenStack 精简规则
    ├── git.md                       # Git 精简规则
    ├── logs.md                      # 日志分析精简规则
    └── gui-testing.md              # GUI 测试精简规则
```

## 使用方式

1. 作为 Skill 使用：Claude Code 自动识别 `SKILL.md`，按规则执行
2. 嵌入 CLAUDE.md / AGENTS.md：复制 `SKILL.md` 中 "CLAUDE.md / AGENTS.md 嵌入片段" 部分
3. 领域规则按需加载：只需在执行对应领域任务时读取对应 `domain-rules/*.md`
