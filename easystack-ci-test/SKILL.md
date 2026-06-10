---
name: easystack-ci-test
description: "Run tox cover and pep8 tests for EasyStack OpenStack projects. Runs cover first, then pep8 at the end to save time. Auto-fixes failures in a loop until both pass and modified code is 100% covered. Python version is inferred from tox.ini (`basepython`): python2 maps to python2.7, python3 maps to python3.9."
---

# EasyStack CI Test Guide

EasyStack OpenStack projects use tox for CI testing. This skill covers running `tox -e pep8` (flake8 linting) and `tox -e cover` (unit test coverage), plus auto-fixing failures until both pass.

## Quick Reference - File Index

| When you need... | Read |
|------------------|------|
| Environment setup (Miniconda env auto-create/activate) | [setup.md](setup.md) |
| Running tox commands (pep8, cover, stestr) | [tox.md](tox.md) |
| Fixing pep8 / flake8 errors | [pep8.md](pep8.md) |
| Fixing coverage gaps, checking HTML reports | [coverage.md](coverage.md) |
| Testing privsep entrypoint-decorated functions | [privsep.md](privsep.md) |
| Auto-fix loop workflow (cover → pep8 cycle) | [auto-fix.md](auto-fix.md) |

## Quick Start

### Step 0: Locate Miniconda installation

Search for Miniconda3 in common locations:

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

- **If found** → Note the path, then follow Step 1 to activate the conda environment.
- **If not found** → Ask the user:

  > ⚠️ 未找到 Miniconda3。请确认：
  > 1. 提供 Miniconda3 的安装路径
  > 2. 安装 Miniconda3 后继续
  > 3. 不使用虚拟环境直接运行 CI（使用系统 Python）

  - 用户选择 **安装** → 提供安装命令或引导用户自行安装
  - 用户选择 **不使用虚拟环境** → 确认后直接跳转到 [`tox.md`](tox.md) 运行 tox

### Step 1: Activate conda environment (if available)

Follow [setup.md](setup.md) to:
1. Detect project name from current directory
2. Find the Miniconda installation directory and source its `conda.sh`
3. Detect Python version from `tox.ini` (`basepython` field)
4. Activate or create env named `easystack-<project>-py<version>` (e.g. `py39`, `py312`)
5. Install `tox` in the env

```bash
# Example: in a cinder project with python3.9
# env name: easystack-cinder-py39
MINICONDA_BASE="$HOME/miniconda3"
source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
conda activate easystack-cinder-py39  # if exists
# or create + activate + install tox

# Then run tox (always after conda activate, never directly)
tox -e cover   # Coverage check (run first, takes ~5 min)
tox -e pep8    # Lint check (run last, takes ~40 sec)
```

> ⚠ **Always activate the Miniconda environment before running `tox`.** Running
> `tox` directly from the system Python will use the wrong interpreter or miss
> dependencies.

When either fails, follow the [auto-fix loop](auto-fix.md) until both pass.

## Code Scope

When running `tox -e pep8` or `tox -e cover`, the scope is the **combined state** of:

1. The latest unmerged commit shown by `git log` on the current branch
2. All uncommitted changes (both staged via `git add` and unstaged working tree modifications)

During development, code may be partially `git add`ed or still being modified. The tests should cover the integrated state of all these changes together - treat the working tree as the complete codebase to validate.
