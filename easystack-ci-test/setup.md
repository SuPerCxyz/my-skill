# Environment Setup

Use this file before running any tox command in an EasyStack OpenStack repository. It explains how to choose and activate the shared Miniconda environment used by the rest of this skill.

## Activate Environment

All tox commands (pep8 and cover) run in a **single shared Miniconda environment** named:

```
easystack-<project>-py<version>
```

### Step 1: Detect project name

Infer the project name from the current directory:

```bash
PROJECT=$(basename "$PWD")
```

For example, in `/home/user/cinder`, project name is `cinder`.

### Step 2: Find the Miniconda installation directory

Do not assume `conda` is already on `PATH`. First locate the Miniconda installation, then
source its activation script and use the bundled `bin/conda` binary:

```bash
MINICONDA_BASE=""
for candidate in \
    "$HOME/miniconda3" \
    "$HOME/miniconda" \
    "/opt/miniconda3" \
    "/opt/miniconda" \
    "/usr/local/miniconda3" \
    "/usr/local/miniconda"
do
    if [ -x "${candidate}/bin/conda" ]; then
        MINICONDA_BASE="${candidate}"
        break
    fi
done

if [ -z "${MINICONDA_BASE}" ]; then
    echo "Cannot find Miniconda installation directory"
    return 1 2>/dev/null || exit 1
fi

source "${MINICONDA_BASE}/etc/profile.d/conda.sh"
CONDA="${MINICONDA_BASE}/bin/conda"
```

If Miniconda is installed in a non-standard location, add that path to the candidate list.

### Step 3: Detect Python version

Infer the Python version from `tox.ini` and map to a fixed conda Python:

```bash
# Extract basepython major version, e.g. python3 -> 3, python2 -> 2
PY_MAJOR=$(grep -oP 'basepython\s*=\s*python\K[0-9]+' tox.ini | head -1 | tr -d '[:space:]')
# Fallback: if no basepython found, default to 3
PY_MAJOR=${PY_MAJOR:-3}

# Map to fixed Python version for conda env creation
if [ "$PY_MAJOR" = "2" ]; then
    PYTHON_VER="2.7"
else
    PYTHON_VER="3.9"
fi
# Convert 2.7 -> py27, 3.9 -> py39 for env name
PY_SHORT="py${PYTHON_VER//./}"
```

### Step 4: Build env name, activate or create

```bash
ENV_NAME="easystack-${PROJECT}-${PY_SHORT}"

if "${CONDA}" env list | grep -q "^${ENV_NAME} "; then
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
