# Environment Setup

## Virtual Environment

tox.ini specifies `basepython = python3`. Create a matching venv:

```bash
python3 -m venv .tox-env
.tox-env/bin/pip install tox -q
```

## Conda Environment

```bash
conda create -n cinder-py39 python=3.9 -y
conda activate cinder-py39
pip install tox
```

## System Dependencies

Install if tox fails building psycopg2 from source:

```bash
sudo apt-get update && sudo apt-get install -y libpq-dev
```
