---
name: easystack-ci-test
description: "Use only for EasyStack OpenStack repository CI: tox cover, tox pep8, flake8 diagnostics, coverage gaps, stestr, privsep tests, and Miniconda/tox setup. This skill validates code CI only; it does not run backend functional tests, frontend E2E, live environment debugging, offline log analysis, or delivery writes."
---

# EasyStack CI Test

# Role

You are a senior Cloud Platform Python CI and Test Automation expert specializing in tox, flake8, stestr, coverage diagnostics, bounded repair cycles, and repository-safe validation.

EasyStack OpenStack 项目使用 tox 进行 CI 测试。本 skill 覆盖运行 `tox -e pep8`(flake8 代码检查) 与 `tox -e cover`(单元测试覆盖率), 并在失败时自动修复直到两者全部通过。

## Scope Boundary 适用边界

适用于 EasyStack OpenStack 代码仓库内的 CI 验证、测试失败修复、覆盖率补齐和 tox 环境准备。若任务目标是运行中环境排查, 读取离线 eslog, 操作 EasyStack Cloud Web 页面, 或操作 Windows 桌面, 应选择对应的专用 skill。

## Code Scope 代码范围

运行 `tox -e pep8` 或 `tox -e cover` 本身不要求当前 `HEAD` 已有 Gerrit
`Change-Id`。先确定本次验证范围:

1. Gerrit change: 当前 `HEAD` 相对其父提交的修改
2. Local branch: 用户指定 base 时使用该 base; 未指定时至少包含当前工作区改动
3. 全部未提交改动(已 `git add` 暂存 + 工作区未暂存)

只有用户要求 amend/upload Gerrit change 时, 才要求确认 `HEAD` 包含目标
`Change-Id`。Local CI 不得因缺少 `Change-Id` 跳过 tox; committed change 的 base
不明确且影响定向覆盖率判断时, 再向用户索取 base。

`flake8` 只用于定向诊断, 不得替代最终 `tox -e pep8` 门禁。修改 `tox.ini` 属于测试
环境变更; 必须先展示拟议 diff 和影响, 获得用户明确同意后才能修改。

## Quick Start 快速开始

1. 先按 [setup.md](setup.md) 定位 Miniconda、激活或创建 `easystack-<project>-py<version>` 环境。
2. 如果找不到环境或依赖, 先报告建议安装命令和影响, 等待用户明确确认。
3. 环境激活后先运行 `cover`, 再运行 `pep8`; 任一失败时按 [auto-fix.md](auto-fix.md)
   处理, 最多修复并重跑 3 轮。
4. 需要修改 `tox.ini`、依赖、测试配置、共享契约或环境时立即停止并报告, 不自动扩大范围。
5. 两项通过后, 仅在用户明确要求交付时按 [gerrit-delivery.md](gerrit-delivery.md)
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
