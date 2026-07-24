# EasyStack CI 测试

运行 EasyStack 旗下 OpenStack 项目的通用 CI 测试并修复问题。测试通过且用户明确
要求上传时, amend 当前 Gerrit commit 并通过指定 remote 更新同一 `Change-Id`。

## 功能

- `tox -e cover` 覆盖率检查
- `tox -e pep8` flake8 代码风格检查
- `flake8` 只用于诊断, 最终必须通过 tox; 修改 `tox.ini` 前需用户明确同意
- 自动修复循环:cover -> pep8 -> 定向修复, 达到停止条件时报告阻塞
- 覆盖率缺口修复指导
- privsep 函数测试处理
- `git commit --amend` + `git review -r <remote>` 更新当前 Gerrit change

## 快速开始

先按 [setup.md](setup.md) 激活 Miniconda 环境。缺少环境或依赖时, 获得用户确认后
再安装。环境已激活后运行:

```bash
tox -e cover   # 覆盖率检查(先跑,约 5 分钟)
tox -e pep8    # 代码风格检查(后跑,约 40 秒)
```

任一失败后按 [自动修复循环](auto-fix.md) 工作流处理。两项通过且用户明确要求上传
时, 再按 [Gerrit 续提交流程](gerrit-delivery.md) 更新当前 change。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口,快速参考 |
| [setup.md](setup.md) | 环境配置(先定位 Miniconda 安装目录,再创建/激活环境、系统依赖) |
| [tox.md](tox.md) | tox 命令参考(pep8、cover、stestr) |
| [pep8.md](pep8.md) | pep8/flake8 错误修复指南 |
| [coverage.md](coverage.md) | 覆盖率修复与 HTML 报告查看 |
| [auto-fix.md](auto-fix.md) | 自动修复循环工作流(cover → pep8 循环直到通过) |
| [privsep.md](privsep.md) | privsep entrypoint-decorated 函数测试指南 |
| [gerrit-delivery.md](gerrit-delivery.md) | amend 当前 commit 并更新同一 Gerrit change |
