# Running tox Commands

## pep8 Check

```bash
tox -e pep8
```

If tox is in a specific environment:

```bash
MINICONDA_BASE="$HOME/miniconda3"
source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
conda activate cinder-py39
tox -e pep8
```

## Coverage Testing

```bash
tox -e cover
```

## Running Individual Tests

Useful for debugging during the fix loop:

```bash
. .tox/cover/bin/activate && stestr run <test_pattern>
```

Examples:

```bash
stestr run test_image_utils
stestr run privsep.test_cgroup
stestr run test_volume_utils.CopyVolumeTestCase.test_copy_volume_with_on_execute
```

## Isolate flake8 Errors

```bash
. .tox/pep8/bin/activate && flake8 path/to/file.py
```

## Note on allowlist_externals

If `tox -e pep8` fails with `is not allowed, use allowlist_externals`, this is a local tox version mismatch — newer tox requires external scripts (like `tools/config/check_uptodate.sh`) to be listed in `tox.ini`'s `allowlist_externals`. If this happens, you can skip tox and run `flake8 .` directly to check for lint errors.
