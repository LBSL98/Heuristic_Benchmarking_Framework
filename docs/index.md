# FORJA / MPP Docs

Esta documentação foi reorganizada para separar o **contrato ativo** do repositório dos materiais
preservados apenas por **rastreabilidade histórica**.

## Use como fonte ativa

- `protocol/current_benchmark_contract.md`
- `specs/reproducibility_checklist.md`
- `testing/TESTING.md`
- `testing/CI.md`
- `testing/TRACEABILITY.md`

Essas páginas refletem o estado canônico atual do benchmark no repositório:

- portfólio oficial da tese = `SA`, `TS`, `ILS`, `GRASP`, `METIS`, `KaHIP`
- `greedy` apenas como fluxo exploratório
- comparação universal por wall-clock / `fair(time)`
- contrato serializado com `elapsed_ms` e `checkpoints[].time_ms`
- KaHIP 3.17 como narrativa experimental oficial, sem inferir a verdade experimental da árvore vendorizada `./KaHIP`

## Legado / quarentena

Algumas páginas antigas foram preservadas para auditoria, mas não devem orientar o fluxo atual.
Elas aparecem explicitamente sob a seção **Legacy / Quarantine** na navegação do site.

Quando houver conflito entre documentação legada e contrato ativo:

1. prevalecem os arquivos canônicos em `decisions/` e `specs/`;
2. prevalece a página `protocol/current_benchmark_contract.md` dentro deste site;
3. materiais legados ficam preservados apenas como trilha histórica.
