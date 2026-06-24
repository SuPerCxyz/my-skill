# EasyStack CI 测试

运行 EasyStack 旗下 OpenStack 项目的通用 CI 测试并自动修复问题。

## 功能

- `tox -e cover` 覆盖率检查
- `tox -e pep8` flake8 代码风格检查
- 自动修复循环:cover → pep8 → 修复 → 重复直到全部通过
- 覆盖率缺口修复指导
- privsep 函数测试处理

## 快速开始

```bash
tox -e cover   # 覆盖率检查(先跑，约 5 分钟)
tox -e pep8    # 代码风格检查(后跑，约 40 秒)
```

任一失败后按 [自动修复循环](auto-fix.md) 工作流处理，直到两项全部通过。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，快速参考 |
| [setup.md](setup.md) | 环境配置(先定位 Miniconda 安装目录，再创建/激活环境、系统依赖) |
| [tox.md](tox.md) | tox 命令参考(pep8、cover、stestr) |
| [pep8.md](pep8.md) | pep8/flake8 错误修复指南 |
| [coverage.md](coverage.md) | 覆盖率修复与 HTML 报告查看 |
| [auto-fix.md](auto-fix.md) | 自动修复循环工作流(cover → pep8 循环直到通过) |
| [privsep.md](privsep.md) | privsep entrypoint-decorated 函数测试指南 |
