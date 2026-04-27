# Quickstart

## 1. Requirements

- Linux / Ubuntu 22.04+
- Python 3.11+
- `gpmetis` available in `PATH`
- `kaffpa` optional for KaHIP runs

## 2. Local install

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip metis

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

## 3. Local smoke test

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
pytest -q
```

## 4. Local docs build

```bash
python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs
```

## 5. Read this before real runs

Before launching real campaigns, read:

- [Current benchmark contract](protocol/current_benchmark_contract.md)
- [Reproducibility checklist](specs/reproducibility_checklist.md)

## 6. First useful command

```bash
./scripts/run_phase_1.sh
```

At this stage, some deeper reference pages may still fall back to Portuguese until reviewed English versions are added.
