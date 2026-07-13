---
name: easystack-ci-test
description: "Use when validating and fixing EasyStack OpenStack repository CI: tox cover, tox pep8, flake8, coverage gaps, stestr, privsep tests, Miniconda/tox setup, and updating the current Gerrit change after tests pass. Do not use for live environments, offline logs, Web UI E2E, or non-EasyStack projects."
---

# EasyStack CI Test

EasyStack OpenStack 项目使用 tox 进行 CI 测试。本 skill 覆盖运行 `tox -e pep8`(flake8 代码检查) 与 `tox -e cover`(单元测试覆盖率), 并在失败时自动修复直到两者全部通过。

## Scope Boundary 适用边界

适用于 EasyStack OpenStack 代码仓库内的 CI 验证、测试失败修复、覆盖率补齐和 tox 环境准备。若任务目标是运行中环境排查, 读取离线 eslog, 操作 EasyStack Cloud Web 页面, 或操作 Windows 桌面, 应选择对应的专用 skill。

## Code Scope 代码范围

运行 `tox -e pep8` 或 `tox -e cover` 时, 当前 `HEAD` 必须是用户准备继续更新的
Gerrit change。测试范围是以下**合并状态**:

1. 当前 `HEAD` commit 相对其父提交的修改
2. 全部未提交改动(已 `git add` 暂存 + 工作区未暂存)

不要根据“最近一个未合并 commit”猜测范围。先确认 `HEAD` commit message 包含目标
Gerrit `Change-Id`; 无法确认时先向用户索取目标 change, 不创建新 commit。

## Quick Start 快速开始

1. 先按 [setup.md](setup.md) 定位 Miniconda、激活或创建 `easystack-<project>-py<version>` 环境。
2. 如果找不到环境或依赖, 先报告建议安装命令和影响, 等待用户明确确认。
3. 环境激活后运行 tox; 任一失败时按 [auto-fix.md](auto-fix.md) 循环修复。
4. 两项通过后, 仅在用户明确要求提交时按 [gerrit-delivery.md](gerrit-delivery.md)
   amend 当前 commit, 保留原 `Change-Id`, 再运行 `git review -r <remote>`。

```bash
tox -e cover   # 覆盖率检查(先跑, 约 5 分钟)
tox -e pep8    # 代码风格检查(后跑, 约 40 秒)
```

> 永远先激活 Miniconda 环境再运行 `tox`。直接用系统 Python 运行 `tox` 会用错解释器或缺失依赖。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------|------|
| 环境配置(Miniconda 虚拟环境自动创建/激活) | [setup.md](setup.md) |
| 运行 tox 命令(pep8, cover, stestr) | [tox.md](tox.md) |
| 自动修复循环工作流(cover -> pep8 循环) | [auto-fix.md](auto-fix.md) |
| 修复 pep8 / flake8 错误 | [pep8.md](pep8.md) |
| 修复覆盖率缺口, 查看 HTML 报告 | [coverage.md](coverage.md) |
| 测试 privsep entrypoint 装饰的函数 | [privsep.md](privsep.md) |
| 测试通过后更新当前 Gerrit change | [gerrit-delivery.md](gerrit-delivery.md) |

## Execution Feedback 执行反馈

执行本 skill 时, 若规则不明确、工具限制导致绕行、同一步骤反复执行或流程无法顺利
推进, 任务结束时必须向用户报告:

- 触发位置和问题现象
- 造成的中断、重复次数或额外开销
- 实际采用的临时处理
- 建议补充或修改的 skill 规则

没有实际问题时不输出空反馈。反馈不得包含密码、token、cookie 或未脱敏的用户数据。
