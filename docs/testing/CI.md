````markdown
# Continuous Integration (CI)

This document describes the minimal Continuous Integration (CI) pipeline configured for the
FORJA / HPC Framework repository.

The CI is implemented via GitHub Actions and defined in:

```text
.github/workflows/ci.yml
````

---

## 1. Triggers and scope

The workflow is named **"CI (minimal)"** and is triggered on:

* any `push` to any branch (`branches: ['**']`), ignoring changes under `site/**`;
* any `pull_request` targeting `main` or `dev`, also ignoring `site/**`.

This ensures that:

* every commit pushed to the repository gets basic QA checks;
* every PR into the protected branches (`main`, `dev`) runs the same pipeline.

A `concurrency` block groups runs by `ref`:

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

so that older runs for the same branch/PR are cancelled when a new commit arrives.

---

## 2. Job: `tests`

The workflow defines a single job, `tests`, which runs on **Ubuntu 22.04**:

```yaml
jobs:
  tests:
    runs-on: ubuntu-22.04
```

The steps in this job are:

### 2.1. Checkout with Git LFS

```yaml
- name: Checkout (with LFS)
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
    lfs: true
```

This checkout:

* fetches the full history (`fetch-depth: 0`), which is useful for some tools;
* enables Git LFS, so that large files (e.g. instances under `data/instances/`) are available.

### 2.2. Ensure Git LFS and materialise blobs

```yaml
- name: Ensure Git LFS & materialize blobs
  run: |
    set -euxo pipefail
    if ! command -v git-lfs >/dev/null 2>&1; then
      sudo apt-get update
      sudo apt-get install -y git-lfs
    fi
    git lfs version
    git lfs install --local
    git lfs fetch --all
    git lfs checkout
    git lfs ls-files || true
    ls -lh data/instances/synthetic || true
    if grep -R -n "version https://git-lfs.github.com/spec/v1" data/instances/synthetic/*.json.gz >/dev/null 2>&1; then
      echo "ERROR: still seeing LFS pointers in *.json.gz" >&2
      exit 2
    fi
```

Purpose:

* guarantee that Git LFS is installed and configured;
* fetch and checkout all LFS objects;
* list LFS-tracked files and the synthetic instance directory;
* **fail fast** if any `*.json.gz` under `data/instances/synthetic/` is still an LFS pointer
  instead of a real gzip payload.

This prevents corrupted or placeholder instances from entering the test pipeline.

### 2.3. GZIP sanity check

```yaml
- name: GZIP sanity (gzip -t)
  run: |
    set -e
    shopt -s nullglob
    files=(data/instances/synthetic/*.json.gz)
    if [ ${#files[@]} -eq 0 ]; then
      echo "No *.json.gz in data/instances/synthetic" >&2
      exit 2
    fi
    for f in "${files[@]}"; do
      echo "Testing gzip: $f"
      if ! gzip -t "$f"; then
        echo "Corrupted file or LFS pointer: $f" >&2
        head -c 64 "$f" | sed 's/[^[:print:]]/./g' || true
        exit 2
      fi
    done
    echo "GZIP OK"
```

This step:

* ensures there is at least one `*.json.gz` in the synthetic instances directory;
* runs `gzip -t` on each file, failing if any is invalid;
* prints a small diagnostic prefix for corrupted files.

Together with the previous step, this enforces **LFS + gzip integrity** for the synthetic panel.

### 2.4. Python setup

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: "pip"
    cache-dependency-path: |
      pyproject.toml
      setup.cfg
      setup.py
```

This configures Python 3.11 with pip caching, keying the cache on the dependency descriptors.

### 2.5. System dependencies (METIS)

```yaml
- name: System deps (METIS for gpmetis)
  run: |
    sudo apt-get update
    sudo apt-get install -y metis
    gpmetis -h | head -n1 || true
```

This installs the `metis` package and checks that `gpmetis` is callable. KaHIP is not installed
in this minimal job; tests that require it are excluded by the pytest selection.

### 2.6. Python dependencies (pip-only)

```yaml
- name: Install Python deps (pip only)
  run: |
    python -m pip install --upgrade pip
    pip install -U pytest
    pip install .
```

This:

* upgrades `pip`;
* installs `pytest`;
* installs the current project into the environment via `pip install .`.

Unlike local development, CI does not use Poetry here; this keeps the workflow minimal while
still respecting `pyproject.toml`.

### 2.7. Run tests

```yaml
- name: Run tests
  env:
    OMP_NUM_THREADS: "1"
    OPENBLAS_NUM_THREADS: "1"
    MKL_NUM_THREADS: "1"
  run: pytest -q -k "not (kahip or solvers_external)"
```

The final step:

* enforces **single-threaded execution** for numerical backends (OMP / BLAS / MKL);
* runs pytest in quiet mode;
* **excludes** tests related to KaHIP and heavy external-solver integration, keeping the pipeline
  fast and robust across environments.

A more exhaustive suite (including KaHIP and extended solver tests) is expected to be run
locally by developers when the appropriate solvers are installed.

---

## 3. Relation to branch policy and contributions

The repository follows a simple contribution workflow:

* feature branches are created from `dev`;
* pull requests target `dev` (not `main`);
* CI must pass before merging;
* `dev` is merged into `main` via pull request, and the `main` branch is protected.

The CI workflow acts as a **gatekeeper** for:

* LFS / gzip integrity of synthetic instances;
* basic installation viability (`pip install .`);
* the core test suite (with external-solver-heavy tests excluded in this minimal job).

Developers are encouraged to:

* run tests locally via Poetry (`poetry run pytest ...`);
* use `pre-commit` hooks for fast feedback on style and basic QA;
* keep `.github/workflows/ci.yml` and `docs/testing/*.md` aligned when the testing strategy evolves.

```
```
