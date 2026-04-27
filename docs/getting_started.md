# Início rápido

## 1. Pré-requisitos

- Linux / Ubuntu 22.04+
- Python 3.11+
- `gpmetis` disponível no `PATH`
- `kaffpa` opcional para rodadas com KaHIP

## 2. Instalação local

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip metis

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

## 3. Smoke local

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
pytest -q
```

## 4. Build local da documentação

```bash
python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs
```

## 5. Primeiro ponto de leitura

Antes de rodar campanhas reais, leia:

- [Contrato atual do benchmark](protocol/current_benchmark_contract.md)
- [Checklist de reprodutibilidade](specs/reproducibility_checklist.md)

## 6. Primeiro comando útil

```bash
./scripts/run_phase_1.sh
```

Use esse caminho apenas quando o seu ambiente local já estiver consistente com o protocolo ativo do repositório.
