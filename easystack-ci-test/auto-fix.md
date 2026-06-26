# Auto-Fix Loop

Use this file after either `tox -e cover` or `tox -e pep8` fails. It defines the repair loop and points to the specialized files for coverage, pep8, and privsep failures.

**Prerequisite:** The shared Miniconda environment `easystack-<project>-py<version>` must be active. See [setup.md](setup.md) for the standard entry path:

```bash
MINICONDA_BASE="$HOME/miniconda3"
source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
conda activate easystack-<project>-py<version>
```

Both `tox -e cover` and `tox -e pep8` run in this same environment. **Never run `tox` directly without activating conda first.**

When fixing pep8 or coverage for a change, follow this loop until both pass:

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
- DONE only when all three conditions are met:
  1. `tox -e cover` passes (all tests pass)
  2. cover HTML shows zero `mis` and zero `par` lines for all modified files
  3. `tox -e pep8` passes
- To identify which files were modified (latest commit + uncommitted changes):
  ```bash
  # All three combined: committed + staged + unstaged
  git diff HEAD~1 --name-only
  git diff --name-only
  git diff --cached --name-only
  ```
  Use this combined list to scope your HTML coverage checks.

## Useful Commands During the Loop

| Need | Command |
|------|---------|
| Run coverage | `tox -e cover` |
| Run pep8 | `tox -e pep8` |
| Isolate lint | `flake8 path/to/file.py` (Miniconda env already has flake8 via tox) |
| Run one test | `stestr run <pattern>` (Miniconda env already has stestr via tox) |
| List modified files | `git diff HEAD~1 --name-only` + `git diff --name-only` + `git diff --cached --name-only` |
| Check coverage | See [coverage.md](coverage.md) |
| Test privsep code | See [privsep.md](privsep.md) |
