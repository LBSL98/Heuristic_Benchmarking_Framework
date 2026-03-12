# FORJA — Evolutive Benchmarking Baseline v1.0 (revisable)

> This baseline is the initial, **revisable** yardstick for FORJA. It codifies fairness, budgets, metrics, and provenance. It can be updated after the pilot; record changes in the Revision History.

**Date:** 2025-09-24

## 1) Purpose and problem
- *Goal:* compare graph partitioning algorithms under a strict, reproducible protocol.
- *Problem:* k-way partitioning on unweighted graph G=(V,E), minimize **edge-cut** under **cardinality balance** with tolerance β.
- *Objective:* \(cut(P) = |{(u,v)\in E : part(u) \neq part(v)}|\)
- *Balance constraint:* \(\forall i,\ \big| |V_i| - |V|/k \big| / (|V|/k) \le \beta\)

**Primary metrics**
- `cut(P)` (minimize), effective imbalance `δ(P)` (%)
**Complementary**
- normalized cut `cut/|E|`, boundary size `|∂P|`, per-part volume, wall time (ms)

## 2) Fairness rule (anytime + budgets)
- **k:** {4, 8, 16} (k=32 is a future extension)
- **β:** {1%, 3%, 5%}
- **Primary budget (NFE):** `NFE_max = 50 · |E|` *per run*
- **Time cap:** `t_max = 0.5 · |E| ms` (stop on whichever comes first)
- **Anytime checkpoints (by NFE):** `{1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5, 3e5, …}` up to `NFE_max`
- **Seeds:** pilot = 1 (42); main campaign = **10 replicas** per (algorithm, instance). Use a master-seed and deterministic derivation.

> *Note:* Values are initial defaults; they **may be tuned** after the pilot, but changes must be documented and applied uniformly.

## 3) Algorithm portfolio (versions & defaults)
- **METIS 5.1.0** (`gpmetis`) — **required**
  - `-ufactor = round(1000·β)`, `-ptype=kway`
- **KaHIP 3.14** (`kaffpa`) — optional in CI; required locally for final experiments
  - `-k`, `-imbalance = 100·β`, `--preconfiguration=fast`
- **Greedy + 1-swap local refinement** (respects balance). Connectivity is **not** enforced globally to stay comparable to METIS/KaHIP.
- **Metaheuristics (future, e.g., SA/GA/MEALPY)** — **cold start** (random k-balanced init). Warm-start is reserved for ablation studies.

## 4) Dataset and naming
- **Synthetic v1.0:** current canonical set in repo (8–12 instances spanning n, p, CV)
- **Planned extension:** factorial grid `n ∈ {2000,3000,3500} × p ∈ {0.35,0.40,0.50} × CV ∈ {0.15,0.30,0.45}` with 2 seeds/point
- **Real (RoadNet-CA):** 3–5 induced subgraphs via BFS with target sizes (~10k, ~20k), defined after pilot
- **Canonical naming:** `n{N}_p{P}_cv{CV}_seed{S}.json.gz` (0-based ids, unit weights)

## 5) Provenance and reproducibility
- **Threads:** `OMP=1`, `OPENBLAS=1`, `MKL=1`
- **Per-run capture:**
  - `git_sha`, `hostname`, `started_at`, `finished_at`, `k`, `β`,
  - `budget` (`NFE_max`, `t_max`), `seed`, `cmdline`, `exit_code`
  - `checkpoints`: list of `(NFE, cut, time_ms)`
- **Label normalization:** map labels to contiguous `0..k-1`; if remapped, store the mapping in the manifest
- **Versions logged:** Python, FORJA pkg, METIS, KaHIP, OS, CPU
- **Results contract (`solver_run.v1`):** fields for metrics, budgets, checkpoints, and artifact paths (consistent with analysis scripts).

## 6) Analysis and statistics
- **Performance profiles (Dolan–Moré)** (ratio to best per instance)
- **Anytime curves** `cut × NFE`
- **TTT (time-to-target)** with gaps to best-known: {0%, 1%, 2%, 5%}; explicit censoring
- **Inference:** Friedman + Nemenyi (multi-algo), Wilcoxon (paired). Multiple testing correction: Holm (BH if justified)
- **Stratification:** terciles for density, modularity Q, |V|, CV

---

### Revision history
- v1.0 (2025-09-24) — initial evolutive baseline
