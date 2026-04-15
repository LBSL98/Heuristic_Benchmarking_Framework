# FORJA / MPP

> Framework reprodutível para benchmarking de algoritmos de particionamento de grafos com trilha de auditoria explícita.

[![CI](https://github.com/Gorgomel/Heuristic_Benchmarking_Framework/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Gorgomel/Heuristic_Benchmarking_Framework/actions)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/version-0.8.0-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Escopo canônico atual

- Portfólio oficial da tese: `SA`, `TS`, `ILS`, `GRASP`, `METIS`, `KaHIP`.
- `greedy` pode existir no repositório apenas como trilha exploratória/de engenharia.
- A régua universal entre famílias é **wall-clock time**.
- `fair(time)` significa mesmo orçamento temporal por instância, mesma semântica de balanceamento, mesmo ambiente controlado, hiperparâmetros congelados no piloto e validação independente.
- Nos artefatos `solver_run.v1`, os nomes canônicos de tempo são `elapsed_ms` e `checkpoints[].time_ms`.
- `time_ns` pode aparecer apenas como detalhe interno de implementação; não é nome canônico de campo serializado.

## Estrutura

```text
.
├─ configs/                # Planos YAML de experimento
├─ src/                    # Código do framework, heurísticas e wrappers
├─ tests/                  # Pytest (CI mínima sem KaHIP; suíte local mais ampla opcional)
├─ scripts/                # Orquestração e utilitários de auditoria
├─ docs/                   # Documentação MkDocs (ativa + legado rotulado)
├─ decisions/              # Camada canônica de decisões metodológicas
├─ specs/                  # Schemas e contratos de artefato
├─ audit_reports/          # Trilhas de auditoria e relatórios
└─ KaHIP/                  # Árvore vendorizada preservada por rastreabilidade
```

## Instalação

Requisitos mínimos:

- Linux/Ubuntu 22.04+
- Python 3.11+
- Git
- `gpmetis` no `PATH`

KaHIP:

- `kaffpa` continua opcional na CI mínima e em smokes locais.
- Para rodadas com KaHIP, registre a versão efetivamente reportada pelo binário em `PATH`.
- A narrativa experimental ativa do repositório usa **KaHIP 3.17** como versão oficial.
- A árvore vendorizada `./KaHIP`, quando presente, é material auxiliar de repositório e não deve ser tratada automaticamente como a fonte de verdade experimental.

Exemplo local:

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip metis

python3.11 -m venv .venv
source .venv/bin/activate
pip install .
```

## Testes

Smoke local:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 pytest -q
```

Observações:

- Se `gpmetis` estiver ausente, os testes dependentes de METIS serão pulados.
- Se `kaffpa` estiver ausente, os testes dependentes de KaHIP serão pulados.
- A CI mínima exclui testes pesados de solver externo; a suíte local pode ser mais ampla quando o ambiente estiver completo.

## Planos e fluxo

Os planos são declarativos e vivem em `configs/`.

Planos rastreados atualmente:

- `configs/plan_phase_1.yaml`: slice executável de baseline (`METIS` + `KaHIP`) com `greedy` excluído.
- `configs/plan_phase_1_pilot.yaml`: slice piloto equivalente.
- `configs/plan_phase_1_greedy_exploratory.yaml`: trilha exploratória com `greedy`, fora do benchmark oficial.
- `configs/plan_phase_1_pilot_greedy_exploratory.yaml`: variante piloto da trilha exploratória.

Uso padrão:

```bash
./scripts/run_phase_1.sh
./scripts/run_phase_1.sh configs/plan_phase_1_pilot.yaml
```

Ao interpretar resultados:

- não trate os planos exploratórios com `greedy` como benchmark oficial;
- não use NFE como régua universal entre famílias;
- valide sempre os artefatos contra `specs/jsonschema/solver_run.schema.v1.json`.

## Artefatos de resultado

O contrato ativo de saída é `solver_run.v1`:

- tempo total serializado: `elapsed_ms`
- timestamp de checkpoint: `checkpoints[].time_ms`
- NFE em checkpoint: diagnóstico opcional para metaheurísticas instrumentadas

Campos legados como `time_ns`, `runtime_ms` e `elapsed_wall_ms` não devem ser descritos como contrato serializado ativo do benchmark.

## Qualidade e reprodutibilidade

- `specs/jsonschema/solver_run.schema.v1.json` é o schema canônico do artefato de resultado.
- `decisions/03_Methodology_Canonical_consolidated.md` congela os significados de wall-clock, `fair(time)`, NFE e política de checkpoints.
- `docs/protocol/current_benchmark_contract.md` resume o contrato operacional atual para quem estiver navegando a documentação do repositório.
- `docs/specs/reproducibility_checklist.md` consolida a checklist de reprodutibilidade para piloto e campanha.

Build local da documentação, sem sujar o diretório `site/` rastreado:

```bash
python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs
```

## Dados e auditoria

- `data/results_*` permanece fora do Git.
- Instâncias sintéticas pequenas permanecem no repositório para smoke e rastreabilidade.
- Bundles de auditoria podem excluir a árvore vendorizada `KaHIP/`, desde que a versão efetiva do `kaffpa` utilizado e o commit do repositório tenham sido registrados separadamente.

## Contribuição

1. Trabalhe em branch dedicada.
2. Mantenha commits pequenos e temáticos.
3. Rode as checagens mínimas relevantes antes de abrir revisão.
4. Preserve a trilha de auditoria quando houver tensão entre limpeza visual e rastreabilidade.

## Referências rápidas

- [CHANGELOG.md](./CHANGELOG.md)
- [docs/index.md](./docs/index.md)
- `decisions/03_Methodology_Canonical_consolidated.md`
- `specs/jsonschema/solver_run.schema.v1.json`
