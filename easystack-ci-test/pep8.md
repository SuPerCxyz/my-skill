# Fixing pep8 Errors

## Find Errors

```bash
. .tox/pep8/bin/activate && flake8 path/to/file.py
```

Refer to the flake8 output for exact error codes and line numbers. Fix each reported issue (line length, import order, docstring formatting, etc.).

## After Fixing

Re-run `tox -e pep8` to verify. New errors may appear - fix those too. See the [auto-fix loop](auto-fix.md) for the full cycle.
