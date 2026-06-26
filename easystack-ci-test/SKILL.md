---
name: easystack-ci-test
description: "Use for EasyStack OpenStack repository CI validation and fixes: tox cover, tox pep8, flake8, coverage gaps, stestr, privsep tests, and Miniconda/tox setup. Do not use for live Kubernetes environment debugging, eslog/offline log analysis, Web UI E2E testing, or general non-EasyStack projects."
---

# EasyStack CI Test

EasyStack OpenStack 项目使用 tox 进行 CI 测试。本 skill 覆盖运行 `tox -e pep8`(flake8 代码检查) 与 `tox -e cover`(单元测试覆盖率), 并在失败时自动修复直到两者全部通过。

## Scope Boundary 适用边界

适用于 EasyStack OpenStack 代码仓库内的 CI 验证、测试失败修复、覆盖率补齐和 tox 环境准备。若任务目标是运行中环境排查, 读取离线 eslog, 操作 EasyStack Cloud Web 页面, 或操作 Windows 桌面, 应选择对应的专用 skill。

## Code Scope 代码范围

运行 `tox -e pep8` 或 `tox -e cover` 时, 测试范围是以下**合并状态**:

1. 当前分支上 `git log` 所示最近一个未合并 commit
2. 全部未提交改动(已 `git add` 暂存 + 工作区未暂存)

开发过程中代码可能部分已 `git add` 或仍在修改中。测试应覆盖这些改动的整合状态 - 把工作区视为待验证的完整代码库。

## Quick Start 快速开始

1. 先按 [setup.md](setup.md) 定位 Miniconda、激活或创建 `easystack-<project>-py<version>` 环境。
2. 如果找不到 Miniconda, 让用户补充安装路径、安装 Miniconda, 或明确确认不使用虚拟环境直接运行 CI。
3. 环境激活后运行 tox; 任一失败时按 [auto-fix.md](auto-fix.md) 循环修复, 直到两者全部通过。

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
