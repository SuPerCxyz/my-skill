---
name: git-delivery
description: "Use when committing, amending, generating commit messages, uploading Gerrit changes, or pushing code. Auto-detects company Gerrit vs personal Git, enforces safety and scope gates before any write operation. Do not use for read-only analysis or tasks not entering the delivery phase."
---

# Git Delivery

统一处理个人 Git 项目和公司 Gerrit 项目的代码提交与交付。自动识别项目类型,
执行通用提交前门禁, 区分用户授权边界, 生成符合规范的提交信息, 并按实际授权
执行 commit、amend、`git review -r origin <branch>` 或普通 push。

## Scope Boundary 适用边界

本 skill 覆盖从"代码修改完成准备交付"到"提交 / 上传 / push 完成"的交付阶段。
不负责代码实现、bug 修复、重构或测试执行本身; 那些应由对应实现 skill 或主流程
完成。本 skill 只处理 Git 提交、提交信息、Gerrit 上传和远程推送。

## Workflow 执行流程

```text
识别用户意图
  ↓
读取仓库规则
  ↓
检查当前仓库和工作区
  ↓
识别 company-gerrit 或 personal-git
  ↓
确定提交逻辑范围
  ↓
执行验证和安全门禁
  ↓
判断新提交或 amend
  ↓
生成或检查提交信息
  ↓
检查用户授权范围
  ↓
执行 commit 或 amend
  ↓
公司项目解析真实目标分支
  ↓
执行 git review -r origin <branch>
  或按授权执行个人项目 push
  ↓
检查真实命令结果
  ↓
输出简洁交付报告
```

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------|------|
| 项目类型识别、EAS / ES 信号、冲突处理 | [project-detection.md](project-detection.md) |
| 通用提交前门禁、暂存规则、验证门禁、安全规则 | [pre-commit-gate.md](pre-commit-gate.md) |
| 用户授权边界: 生成信息 / commit / amend / git review / push / 历史改写 | [authorization.md](authorization.md) |
| 公司 Gerrit: 目标分支、Change-Id、原 Change 更新与新 Change 创建、提交信息规范、git review 门禁 | [company-gerrit.md](company-gerrit.md) |
| 个人项目: 提交边界、提交信息、amend、push | [personal-git.md](personal-git.md) |
| 多提交栈: Change 归属、非 HEAD Change 处理 | [multi-commit.md](multi-commit.md) |
| 最终输出格式与诚实报告规则 | [output-format.md](output-format.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若说明不清、重复尝试、工具或权限阻塞、路径失效或产生额外
绕行, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 实际影响和额外开销
- 临时处理方式
- 可复用的优化建议

没有实际问题时不输出空反馈。反馈中的凭据和用户数据必须脱敏。
