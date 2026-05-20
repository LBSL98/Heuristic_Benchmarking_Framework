# Consolidated results integration packet

Packet id: `1242c_consolidated_results_integration_packet`
Main commit: `b2d3d0f7e18db37ec7907ec8c62c3423005a9deb`

This packet integrates already validated evidence for writing and review. It does not execute solvers, recompute metrics, train CART, edit TeX, add datasets, or commit raw/runtime artifacts.

## Evidence block 1 — srv-noctua confirmation campaign

- Source JSON: `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001/checks/campaign_digest.json`
- Source MD: `audit_reports/multilevel_exception_mining/confirmation/srv_noctua_linux_dedicated_evidence_bundle_001/checks/campaign_digest.md`
- Planned runs: `22,400` (`22.400` in Portuguese numeric notation)
- Valid results: `22,400` (`22.400` in Portuguese numeric notation)
- Invalid results: `0`
- Raw status counts: `{'ok': 18760, 'timeout': 3640}`
- Confirmation labels: `{'competitive_confirmed': 8, 'near_tie_confirmed': 227, 'non_exception_confirmed': 11, 'strong_exception_confirmed': 202}`
- SBS algorithm: `ts_rust`
- VBS mean median cut: `80.77678571428571`
- Claim boundary: `compact_digest_for_traceability_not_full_interpretive_analysis`

## Evidence block 2 — CART diagnostic model

- Acceptance: `PASS`
- Dataset rows: `120`
- Candidate groups: `107`
- Target counts: `{'0': 47, '1': 73}`
- Baseline balanced accuracy: `0.5000`
- LOSO balanced accuracy: `0.8311`
- SGKF balanced accuracy: `0.7817`
- Claim boundary: Accepted for monograph as diagnostic, candidate-level CART analysis. Do not present as universal algorithm selector. Do not claim causal law; report as morphology-associated empirical separation within confirmed benchmark slices.

## Evidence block 3 — TigerLine bounded real-graph evidence

- Quality source: `data/instances/real/m4_broader_quality_metric_metadata/tigerline_roads_2025_06037_los_angeles_county_broader_quality_metrics_1236.yaml`
- Synthesis source: `data/instances/real/m4_broader_result_synthesis_metadata/tigerline_roads_2025_06037_los_angeles_county_bounded_result_synthesis_1238.yaml`
- Instance: `tigerline_roads_2025_06037_los_angeles_county`
- Vertices: `1199509`
- Edges: `1294674`

| k | METIS/gpmetis cut | KaHIP/kaffpa fast cut | Δ KaHIP − METIS |
|---:|---:|---:|---:|
| 2 | 62 | 99 | 37 |
| 4 | 163 | 169 | 6 |
| 8 | 344 | 372 | 28 |
| 16 | 612 | 612 | 0 |
| 32 | 1033 | 1050 | 17 |

Bounded interpretation:

Neste grafo real TigerLine de Los Angeles County, com 1.199.509 vértices e 1.294.674 arestas observadas, METIS/gpmetis obteve corte menor que KaHIP/kaffpa fast em k=2, k=4, k=8 e k=32, enquanto houve empate em k=16. As diferenças absolutas de corte foram pequenas no contexto do número total de arestas, variando de 0 a 37 arestas. Esse resultado é evidência limitada a uma instância real e a duas configurações de solvers; ele não sustenta, isoladamente, uma conclusão geral sobre dominância de famílias de algoritmos, nem treinamento CART.

## Safe claims for monograph text

- A campanha dedicada em srv-noctua produziu 22.400 resultados válidos, sem resultados inválidos, sob o protocolo confirmatório registrado.
- Nas fatias confirmadas, a modelagem CART foi aceita como análise diagnóstica interpretável, com acurácia balanceada LOSO de 0,8311 e SGKF de 0,7817.
- No grafo TigerLine de Los Angeles County, METIS/gpmetis obteve corte menor que KaHIP/kaffpa fast em quatro dos cinco valores de k avaliados e empatou em k=16; essa evidência é limitada a uma única instância real.

## Forbidden claims

- Não afirmar que o CART é um seletor universal de algoritmos.
- Não afirmar dominância geral de METIS, KaHIP ou meta-heurísticas a partir do TigerLine.
- Não afirmar que SNAP foi licenciado ou resolvido.
- Não combinar evidência local, WSL e srv-noctua como se pertencessem ao mesmo ambiente experimental.
- Não usar TigerLine isoladamente para treinar CART ou sustentar conclusão multi-dataset.
