# Fixing Coverage Gaps

## 0. Scope - Which Files to Check

The coverage report covers the **entire project**, but you only need to ensure
100% coverage for files modified in the current change set. This includes both:

1. The latest unmerged commit on the current branch
2. All uncommitted changes (staged and unstaged)

```bash
# List all modified files: committed (latest) + uncommitted (staged + unstaged)
git diff HEAD~1 --name-only   # files changed in latest commit
git diff --name-only          # unstaged changes
git diff --cached --name-only # staged but not committed changes
```

Every line in these modified files must be covered - zero `mis` (missing) and
zero `par` (partial) in the HTML report. Lines in untouched files are out of scope.

## 1. Find Uncovered Lines

After `tox -e cover`, check `cover/status.json`. File keys are derived from
the module path by replacing `.` with `_` and appending `_py`:

| File path | status.json key |
|-----------|-----------------|
| `cinder/privsep/cgroup.py` | `cinder_privsep_cgroup_py` |
| `cinder/volume/throttling.py` | `cinder_volume_throttling_py` |
| `cinder/tests/unit/test_cgroup.py` | `cinder_tests_unit_test_cgroup_py` |

```python
python3 -c "
import json
with open('cover/status.json') as f:
    data = json.load(f)
entry = data['files']['cinder_privsep_cgroup_py']
nums = entry['index']['nums']
stmts, missing = nums[1], nums[2]
print(f'{stmts} statements, {missing} missing')
"
```

## 2. Find Exact Missing Lines in HTML

```bash
# Missing lines (never executed)
grep 'class="mis' cover/cinder_privsep_cgroup_py.html | grep -o 'id="t[0-9]*"' | grep -o '[0-9]*'

# Partially covered lines (some branches not taken)
grep 'class="par' cover/cinder_privsep_cgroup_py.html | grep -o 'id="t[0-9]*"' | grep -o '[0-9]*'
```

## 3. Cover Error Paths

100% coverage requires testing **error paths**, not just the happy path:

- **`except` branches** - mock with `side_effect=OSError` or similar to trigger exception handlers
- **`partial` (par) lines** - both sides of an `if` condition must be exercised. If only the `true` branch runs, the `false` branch is partial. Write a separate test that flips the condition.

Example:

```python
def test_cgroup_limit_v2_os_error(self):
    with mock.patch.object(cgroup.os.path, 'isfile', return_value=True):
        with mock.patch('builtins.open',
                        side_effect=OSError('perm denied')):
            self.assertRaises(
                processutils.ProcessExecutionError,
                cgroup.cgroup_limit, 'mygroup', 'read', '253:0', 1024)
```

## 4. Mocking Multiple File Reads

`mock_open(read_data=...)` returns the same content for every file opened.
When the code opens multiple files expecting different content, use a custom function:

```python
def fake_open(path, mode='r', *args, **kwargs):
    file_map = {
        '/path/to/file_a.conf': mock.mock_open(read_data='content_a')(),
        '/path/to/file_b.conf': mock.mock_open(read_data='content_b')(),
    }
    return file_map.get(path, mock.mock_open()())

with mock.patch('builtins.open', fake_open):
    # code that opens file_a and file_b gets different content
```

## 5. Add Targeted Unit Tests

Write tests that cover the specific uncovered branches. See [privsep.md](privsep.md) for testing privsep-decorated functions.

## After Fixing

Re-run `tox -e cover` to verify. Once coverage is clean, run `tox -e pep8` (or `flake8 .`) to fix any lint errors introduced by new tests.
