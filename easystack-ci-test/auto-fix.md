# Auto-Fix Loop

Use this file after either `tox -e cover` or `tox -e pep8` fails. It defines the repair loop and points to the specialized files for coverage, pep8, and privsep failures.

**Prerequisite:** The shared Miniconda environment `easystack-<project>-py<version>` must be active. See [setup.md](setup.md) for the standard entry path:

```bash
MINICONDA_BASE="$HOME/miniconda3"
source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
conda activate easystack-<project>-py<version>
```

Both `tox -e cover` and `tox -e pep8` run in this same environment. **Never run `tox` directly without activating conda first.**

When fixing pep8 or coverage for a change, follow this loop for at most 3 repair-and-rerun rounds,
or stop earlier when a stop condition below is reached:

```
┌──────────────────────────────────────────────┐
│  Step 1: Run tox -e cover                    │
│  └─ FAIL (test failures)                     │
│           → Fix failing tests                │
│           → Go back to Step 1                │
│           → PASS → continue                  │
├──────────────────────────────────────────────┤
│  Step 2: Check HTML coverage for modified    │
│          files (cover/<module>_py.html)      │
│  └─ "mis" (missing) or "par" (partial) found │
│           → Write targeted unit tests        │
│           → Go back to Step 1                │
│           → None found → continue            │
├──────────────────────────────────────────────┤
│  Step 3: Run tox -e pep8                     │
│  └─ FAIL → Read flake8 output                │
│           → Fix each error in source files   │
│           → Go back to Step 1 (new tests     │
│              or code changes may break tests) │
│           → PASS → DONE ✓                    │
└──────────────────────────────────────────────┘
```

**Run cover first, pep8 last.** pep8 runs in ~40s while cover takes ~5 minutes. Deferring pep8 until the end avoids repeated waits when the cover fix loop is the longer path.

## Key Points

- New tests may introduce test failures - fix those before moving on
- Stop and report instead of continuing when the same failure remains after three repair rounds,
  the required change leaves the user-approved scope, or it requires dependency, root config,
  shared contract, schema, CI, or environment changes without approval.
- DONE only when all three conditions are met:
  1. `tox -e cover` passes (all tests pass)
  2. 本次 diff 新增或修改的 executable lines 没有 `mis` 或 `par`; touched file 中
     与本次 diff 无关的历史缺口记录为 baseline, 不自动扩大修改范围
  3. `tox -e pep8` passes
- Direct `flake8` runs are diagnostic only and never replace `tox -e pep8`.
- If completion requires changing `tox.ini`, show the proposed diff and wait for explicit
  user approval. Without approval, report the environment blocker and stop.
- To identify scope, use the confirmed Gerrit parent or user-provided local base, then add
  staged and unstaged changes:
  ```bash
  # Gerrit HEAD
  git diff HEAD^ --name-only
  # Local branch with explicit base
  git diff <BASE>...HEAD --name-only
  # Uncommitted
  git diff --name-only
  git diff --cached --name-only
  ```
  Do not infer an unknown committed base from the nearest commit message.
- After all checks pass, use [gerrit-delivery.md](gerrit-delivery.md) only when the user explicitly
  asks to amend and upload the current change.

## Useful Commands During the Loop

| Need | Command |
|------|---------|
| Run coverage | `tox -e cover` |
| Run pep8 | `tox -e pep8` |
| Isolate lint | `. .tox/pep8/bin/activate && flake8 path/to/file.py` (diagnostic only) |
| Run one test | `stestr run <pattern>` (Miniconda env already has stestr via tox) |
| List modified files | `git diff HEAD^ --name-only` + `git diff --name-only` + `git diff --cached --name-only` |
| Check coverage | See [coverage.md](coverage.md) |
| Test privsep code | See [privsep.md](privsep.md) |
