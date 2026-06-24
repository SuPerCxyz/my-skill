---
name: easystack-ci-test
description: "Use when running CI tests for EasyStack OpenStack projects: tox cover (coverage) and pep8 (flake8). Auto-fixes failures in a loop until both pass and modified code is 100% covered. Python version is inferred from tox.ini basepython."
---

# EasyStack CI Test

EasyStack OpenStack 项目使用 tox 进行 CI 测试。本 skill 覆盖运行 `tox -e pep8`(flake8 代码检查) 与 `tox -e cover`(单元测试覆盖率), 并在失败时自动修复直到两者全部通过。

## Quick Reference 快速参考 - 文件索引

| 需要做什么 | 阅读 |
|------------|------|
| 环境配置(Miniconda 虚拟环境自动创建/激活) | [setup.md](setup.md) |
| 运行 tox 命令(pep8, cover, stestr) | [tox.md](tox.md) |
| 修复 pep8 / flake8 错误 | [pep8.md](pep8.md) |
| 修复覆盖率缺口, 查看 HTML 报告 | [coverage.md](coverage.md) |
| 测试 privsep entrypoint 装饰的函数 | [privsep.md](privsep.md) |
| 自动修复循环工作流(cover -> pep8 循环) | [auto-fix.md](auto-fix.md) |

## Quick Start 快速开始

### Step 0: 定位 Miniconda 安装位置

在常见路径搜索 Miniconda3:

```bash
# Find conda in common paths
CONDA_PATHS=(
  "$HOME/miniconda3"
  "$HOME/miniconda"
  "/opt/miniconda3"
  "/opt/miniconda"
  "$HOME/anaconda3"
)
for p in "${CONDA_PATHS[@]}"; do
  [ -d "$p" ] && echo "found: $p" && break
done || echo "miniconda3 not found in common paths"

# Alternative: search with locate/find
# locate -b miniconda3 2>/dev/null | head -5
# find / -maxdepth 4 -name "conda.sh" -type f 2>/dev/null | head -5
```

- **找到** -> 记录路径, 然后按 Step 1 激活 conda 环境。
- **未找到** -> 向用户确认:

  > 未找到 Miniconda3。请确认:
  > 1. 提供 Miniconda3 的安装路径
  > 2. 安装 Miniconda3 后继续
  > 3. 不使用虚拟环境直接运行 CI(使用系统 Python)

  - 用户选择 **安装** -> 提供安装命令或引导用户自行安装
  - 用户选择 **不使用虚拟环境** -> 确认后直接跳转到 [`tox.md`](tox.md) 运行 tox

### Step 1: 激活 conda 环境(如可用)

按 [setup.md](setup.md) 执行:
1. 从当前目录推断项目名
2. 找到 Miniconda 安装目录并 source 其 `conda.sh`
3. 从 `tox.ini` 的 `basepython` 字段检测 Python 版本
4. 激活或创建名为 `easystack-<project>-py<version>` 的环境(例如 `py39`, `py312`)
5. 在环境中安装 `tox`

```bash
# Example: in a cinder project with python3.9
# env name: easystack-cinder-py39
MINICONDA_BASE="$HOME/miniconda3"
source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
conda activate easystack-cinder-py39  # if exists
# or create + activate + install tox

# Then run tox (always after conda activate, never directly)
tox -e cover   # 覆盖率检查(先跑, 约 5 分钟)
tox -e pep8    # 代码风格检查(后跑, 约 40 秒)
```

> 永远先激活 Miniconda 环境再运行 `tox`。直接用系统 Python 运行 `tox` 会用错解释器或缺失依赖。

任一失败时, 按 [auto-fix.md](auto-fix.md) 中的自动修复循环处理, 直到两者全部通过。

## Code Scope 代码范围

运行 `tox -e pep8` 或 `tox -e cover` 时, 测试范围是以下**合并状态**:

1. 当前分支上 `git log` 所示最近一个未合并 commit
2. 全部未提交改动(已 `git add` 暂存 + 工作区未暂存)

开发过程中代码可能部分已 `git add` 或仍在修改中。测试应覆盖这些改动的整合状态 - 把工作区视为待验证的完整代码库。