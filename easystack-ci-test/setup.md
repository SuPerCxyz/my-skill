# Environment Setup

## Activate Environment

All tox commands (pep8 and cover) run in a **single shared conda environment** named:

```
easystack-<project>-py<version>
```

### Step 1: Detect project name

Infer the project name from the current directory:

```bash
PROJECT=$(basename "$PWD")
```

For example, in `/home/user/cinder`, project name is `cinder`.

### Step 2: Detect Python version

Infer the Python version from `tox.ini`:

```bash
# Extract basepython, e.g. python3.9 -> 3.9
PYTHON_VER=$(grep -oP 'basepython\s*=\s*python\K.+' tox.ini | head -1 | tr -d '[:space:]')
# Fallback: if no basepython found, default to 3.9
PYTHON_VER=${PYTHON_VER:-3.9}
# Convert 3.9 -> py39, 3.12 -> py312 for env name
PY_SHORT="py${PYTHON_VER//./}"
```

### Step 3: Build env name, activate or create

```bash
ENV_NAME="easystack-${PROJECT}-${PY_SHORT}"

if conda env list | grep -q "^${ENV_NAME} "; then
    echo "Found existing conda env: ${ENV_NAME}"
    conda activate "${ENV_NAME}"
else
    echo "Creating conda env: ${ENV_NAME} (python=${PYTHON_VER})"
    conda create -n "${ENV_NAME}" python="${PYTHON_VER}" -y
    conda activate "${ENV_NAME}"
    pip install tox -q
fi
```

After activation, `tox` is available in PATH. Run `tox -e cover` and `tox -e pep8` directly.

## System Dependencies

Install if tox fails building psycopg2 from source:

```bash
sudo apt-get update && sudo apt-get install -y libpq-dev
```
