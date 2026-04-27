# FORJA
## Framework reproduzível para benchmarking de particionamento de grafos

> Infraestrutura experimental auditável para comparação justa entre solvers multilevel e meta-heurísticas sob um protocolo congelado de `fair(time)`.

[![CI](https://github.com/LBSL98/Heuristic_Benchmarking_Framework/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/LBSL98/Heuristic_Benchmarking_Framework/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-0A7BBB?logo=materialformkdocs&logoColor=white)](https://lbsl98.github.io/Heuristic_Benchmarking_Framework/)
[![Release](https://img.shields.io/badge/release-benchmark--main--ready--2026--04--27-6f42c1)](https://github.com/LBSL98/Heuristic_Benchmarking_Framework/releases/tag/benchmark-main-ready-2026-04-27)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

FORJA é o backbone experimental da monografia sobre seleção explicável de algoritmos para particionamento de grafos. O repositório foi estruturado para que comparações entre famílias heterogêneas não dependam de conveniência editorial, mas de um protocolo explícito de execução, validação, rastreabilidade e auditoria.

Em vez de misturar métricas de esforço, ambientes e contratos de saída, o projeto congela uma superfície metodológica única para o benchmark: mesmo orçamento temporal por instância, mesma semântica de balanceamento, execução mono-thread controlada, validação independente e cadeia de artefatos reconstruível.

## O que este repositório entrega

- benchmark reproduzível para o portfólio canônico da tese: `SA`, `TS`, `ILS`, `GRASP`, `METIS` e `KaHIP`;
- runner único para execução, medição, persistência e validação de artefatos;
- contratos canônicos para tempo, checkpoints, status e schema de saída;
- planos YAML rastreáveis para piloto, calibração e campanhas comparativas;
- documentação navegável via MkDocs;
- camada explícita de decisões, open issues, ledger experimental e mapa de claims.

## Estado público atual

O corte público atual do repositório é a tag [`benchmark-main-ready-2026-04-27`](https://github.com/LBSL98/Heuristic_Benchmarking_Framework/releases/tag/benchmark-main-ready-2026-04-27).

Esse estado significa:

- o piloto benchmarkado foi executado e aprovado;
- a cadeia de artefatos fechou sem erros de schema;
- a campanha principal ficou metodologicamente admissível sob o mesmo protocolo congelado;
- a campanha principal ainda **não** foi iniciada.

## Princípios metodológicos centrais

- **Régua universal de esforço:** `wall-clock time`, serializado como `elapsed_ms`.
- **Checkpoint canônico:** `checkpoints[].time_ms`.
- **`fair(time)`:** mesmo orçamento temporal por instância, mesma semântica de balanceamento, mesmo ambiente controlado, hiperparâmetros congelados e mesma validação independente.
- **NFE:** métrica diagnóstica interna quando instrumentação existe; não é a régua universal entre famílias.
- **Repetição estocástica:** feita por slice `(instância, algoritmo, orçamento)` com colapso posterior antes da análise comparativa e da rotulação ASP.

## Começando rápido

### 1. Requisitos mínimos

- Linux / Ubuntu 22.04+
- Python 3.11+
- Git
- `gpmetis` disponível no `PATH`

Observações sobre KaHIP:

- `kaffpa` é opcional na CI mínima e em smokes locais;
- para rodadas com KaHIP, registre a versão realmente usada no `PATH`;
- a narrativa experimental ativa do repositório usa **KaHIP 3.17** como referência oficial.

### 2. Instalação local

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip metis

python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

### 3. Smoke local

```bash
OMP_NUM_THREADS=1 \
OPENBLAS_NUM_THREADS=1 \
MKL_NUM_THREADS=1 \
pytest -q
```

Notas:

- se `gpmetis` estiver ausente, testes dependentes de METIS serão pulados;
- se `kaffpa` estiver ausente, testes dependentes de KaHIP serão pulados;
- a CI pública é mínima; a suíte local pode ser mais ampla quando o ambiente estiver completo.

### 4. Build local da documentação

```bash
python -m mkdocs build --strict --site-dir /tmp/forja-mkdocs
```

### 5. Execução por planos

Os planos experimentais são declarativos e vivem em `configs/`.

Exemplos:

```bash
./scripts/run_phase_1.sh
./scripts/run_phase_1.sh configs/plan_phase_1_pilot.yaml
```

Também existem planos separados para:

- baselines da campanha principal;
- meta-heurísticas da campanha principal;
- baselines do piloto;
- meta-heurísticas do piloto;
- trilhas de calibração e confirmação de hiperparâmetros.

## Documentação

- Site da documentação: [https://lbsl98.github.io/Heuristic_Benchmarking_Framework/](https://lbsl98.github.io/Heuristic_Benchmarking_Framework/)
- Página inicial da documentação no repositório: [`docs/index.md`](./docs/index.md)
- Contrato operacional atual: [`docs/protocol/current_benchmark_contract.md`](./docs/protocol/current_benchmark_contract.md)
- Checklist de reprodutibilidade: [`docs/specs/reproducibility_checklist.md`](./docs/specs/reproducibility_checklist.md)

## Fontes canônicas do projeto

A interpretação metodológica do repositório não deve depender só da prosa do README. As referências normativas centrais são:

- [`decisions/01_Decision_Log.md`](./decisions/01_Decision_Log.md)
- [`decisions/03_Methodology_Canonical_consolidated.md`](./decisions/03_Methodology_Canonical_consolidated.md)
- [`decisions/06_Experiment_Ledger.md`](./decisions/06_Experiment_Ledger.md)
- [`decisions/07_Open_Issues.md`](./decisions/07_Open_Issues.md)
- [`decisions/08_Results_to_Text_Map.md`](./decisions/08_Results_to_Text_Map.md)
- [`specs/jsonschema/solver_run.schema.v1.json`](./specs/jsonschema/solver_run.schema.v1.json)

## Estrutura do repositório

```text
.
├─ configs/                # Planos YAML de execução, calibração e campanhas
├─ src/                    # Código do framework, heurísticas e wrappers
├─ tests/                  # Testes automatizados e smoke coverage
├─ scripts/                # Orquestração e utilitários de auditoria
├─ docs/                   # Documentação MkDocs
├─ decisions/              # Camada canônica de decisões e governança
├─ specs/                  # Schemas e contratos de artefato
├─ audit_reports/          # Trilhas de auditoria e relatórios técnicos
└─ KaHIP/                  # Árvore vendorizada preservada por rastreabilidade
```

## Reprodutibilidade e auditoria

FORJA não trata reprodutibilidade como apêndice. O projeto explicita:

- execução mono-thread;
- contratos de saída validados por schema;
- distinção entre artefatos ativos e trilhas exploratórias;
- freeze metodológico antes da campanha principal;
- ledger experimental para rastrear o que pode ou não sustentar texto da monografia.

## Como contribuir

1. Trabalhe em branch dedicada.
2. Preserve commits temáticos e auditáveis.
3. Execute as checagens mínimas relevantes antes de abrir PR.
4. Não promova trilhas exploratórias a benchmark oficial sem atualização canônica explícita.
5. Quando houver conflito entre limpeza visual e rastreabilidade, registre a decisão em vez de esconder a tensão.

## Links rápidos

- [Release atual](https://github.com/LBSL98/Heuristic_Benchmarking_Framework/releases/tag/benchmark-main-ready-2026-04-27)
- [Documentação online](https://lbsl98.github.io/Heuristic_Benchmarking_Framework/)
- [CHANGELOG](./CHANGELOG.md)
- [Contrato de benchmark atual](./docs/protocol/current_benchmark_contract.md)
- [Schema do artefato `solver_run.v1`](./specs/jsonschema/solver_run.schema.v1.json)
