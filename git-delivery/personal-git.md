# Personal Git Rules 个人项目规则

个人项目优先读取并遵循项目级 Agent 规则、`CONTRIBUTING.md`、README、最近提交
历史、分支规范、发布规范、lint / test / build 脚本。

## 提交边界

一个提交应尽量对应一个可描述、可验证、可评审、可回滚的逻辑变更。

通常应拆分: 无关 bug 修复和新功能、行为变更和无关重构、大范围格式化和功能
修改、依赖升级和无关业务改动、多个互不相关的功能。

通常可以放在同一提交: 功能实现及其直接测试、bug 修复及其回归测试、配置修改
及对应文档、重构及证明行为不变的测试。

## 提交信息

优先遵循仓库已有风格。仓库明显使用 Conventional Commits 时沿用, 例如:

```text
feat: add usage date filters
fix: prevent duplicate session records
```

仓库没有明确风格时, 默认使用:

```text
<简洁、明确的 summary>

<必要时说明修改原因、关键逻辑和影响>
```

个人项目默认不添加 Gerrit `Change-Id`、EAS footer 和 Gerrit `Depends-On`。

## amend

只有以下情况下才考虑 amend: 用户明确要求修改最近提交、当前修改明确属于最近
提交、最近提交尚未共享或用户明确理解历史改写影响、amend 不会影响其他协作者、
仓库流程允许修改提交历史。未经授权不得为了整理历史而擅自 amend、rebase 或
force push。

## push

执行 push 前必须检查: 目标 remote、目标分支、是否存在意外提交、是否可能覆盖
远程历史、当前范围验证是否完成、用户是否明确授权。默认禁止 force push。
