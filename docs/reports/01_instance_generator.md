# Instance generator: design and validation

This report documents the synthetic instance generator used in the FORJA / HPC Framework project.
The generator is responsible for producing graphs with controlled properties, which are later used
to benchmark partitioning algorithms under fair and reproducible conditions.

The generator is implemented as a Python module under:

```text
src/generator/
````

and exposed via a command-line interface (CLI) described in the *API → Instance generator CLI*
section of this site.

---

## 1. Goals and design principles

The instance generator is designed to support the following goals:

1. **Control**
   Allow experiments to target specific regimes of:

   * number of vertices `n`;
   * edge density / sparsity;
   * degree or “speed” heterogeneity (coefficient of variation);
   * other structural features relevant to the algorithm-selection study.

2. **Reproducibility**
   Ensure that a panel of graphs can be reconstructed from:

   * a versioned configuration file (YAML);
   * a fixed code revision;
   * explicit random seeds.

3. **Compatibility**
   Produce instances that conform to the input JSON schema used by the rest of the framework,
   so that no ad-hoc conversion is needed before running solvers.

The generator is not a general-purpose random graph library; it is tailored to the needs of the
graph partitioning experiments in this project.

---

## 2. Input and output formats

### 2.1. Input JSON schema

Generated instances are stored as JSON documents (optionally gzip-compressed, `*.json.gz`)
that conform to the **input schema**:

```text
specs/schema_input.json
```

This schema defines, among other things:

* basic metadata (instance identifier, generator configuration);
* the list of vertices and their attributes (e.g. weights);
* the list of edges and their attributes;
* invariants required by the partitioning operators (e.g. no self-loops, indexing conventions).

Downstream components (core operators, external solvers) assume that this schema is satisfied.
Sanity tests in `tests/test_instances_sanity.py` and related modules enforce this contract.

### 2.2. Output location and naming convention

By convention, synthetic instances are stored under:

```text
data/instances/synthetic/
```

A typical filename encodes the main regime parameters, for example:

* `n2000_p50.json.gz` – about 2000 vertices, target density around 0.50;
* `n2000_dense_fast.json.gz` – a denser regime with different heterogeneity;
* `n3000_p35_cv045.json.gz` – explicit mention of CV bands in the filename.

These files are small enough to be versioned as part of the repository (or via Git LFS),
and are used both as examples and as part of the Phase 1 experimental panel.

---

## 3. Regimes and configuration (`configs/instances_to_generate.yaml`)

Rather than generating graphs purely ad hoc from individual CLI calls, this project relies on a
**configuration-driven approach**.

The file:

```text
configs/instances_to_generate.yaml
```

defines a set of **regimes** to be generated. Each regime typically specifies:

* target number of nodes;
* target density or related metric;
* degree / “speed” heterogeneity bands (via coefficient of variation);
* number of instances per regime;
* random seeds or ranges.

The exact field names and structure are documented inside the YAML file itself. The generator
reads this configuration and materialises each regime as one or more JSON instances under
`data/instances/`.

This design allows:

* regenerating the same panel of instances on a new machine, given the YAML and a fixed code revision;
* extending the panel (e.g. adding new regimes) without changing the generator logic;
* documenting the experimental landscape in a single, version-controlled file.

---

## 4. CLI usage (high-level)

The generator exposes a CLI entry point under the `generator` module. After installing the
project (preferably via Poetry), the general pattern is:

```bash
poetry run python -m generator.cli --help
```

The `--help` output describes the available subcommands and options, including:

* how to select the number of nodes;
* how to control density or related parameters;
* how to pick heterogeneity regimes (e.g. CV bands);
* how to set seeds for reproducibility;
* how to choose the output path and compression.

For generating a small number of instances manually, a simple one-shot invocation is usually
sufficient (for example, targeting a specific `n` and density). For full experimental panels,
the recommended workflow is to:

1. edit `configs/instances_to_generate.yaml` to define or adjust regimes;
2. use a pipeline script under `scripts/` to iterate over those regimes and call the generator
   CLI programmatically;
3. verify the resulting panel via the test suite (see Section 5).

The exact argument names and subcommands may evolve with the project; the CLI `--help` output is
the authoritative source for the current version.

---

## 5. Validation and test coverage

A dedicated set of tests under `tests/` validates both individual instances and the behaviour of
the generator across regimes. Key modules include:

* `tests/test_generator.py`
  Basic properties of generated instances and integration with the CLI.

* `tests/test_degree_cv_bands.py`
  Ensures that generated instances fall within the intended **coefficient-of-variation bands**
  for degree or “speed” distributions, as specified by the configuration.

* `tests/test_degree_cv_cap.py`
  Enforces **ceiling constraints** on variability, preventing the generator from producing
  instances that are too heterogeneous for the experimental design.

* `tests/test_instances_sanity.py`
  General structural sanity checks (e.g. no malformed edges, consistent indexing), aligned with
  the expectations encoded in `specs/schema_input.json`.

* `tests/test_modularity_gate_regression.py`
  Regression tests related to modularity estimates and gates used to filter or classify instances
  by community structure.

Together, these tests act as a safety net: changes to the generator or to the configuration are
flagged early if they break the intended regimes or violate basic invariants.

---

## 6. Relation to the experimental protocol

The instance generator is a **preparatory stage** for the experimental protocol described in:

* `docs/protocol/proto_v3.1.1.md`;
* `configs/plan_phase_1*.yaml` (experiment plans);
* the Phase 1 campaign report (`docs/reports/02_experimental_campaign.md`).

The typical high-level workflow is:

1. **Generate or refresh** the synthetic panel under `data/instances/` using the generator and
   `configs/instances_to_generate.yaml`.
2. **Run experiments** (e.g. Phase 1) via the `hpc_framework` CLI and the appropriate plan file.
3. **Pack, validate and aggregate** results into manifests and CSV tables.

By keeping generator configuration, instance files, plans and results all under version control
(or tracked via Git LFS and audit bundles), the project ensures that the experimental landscape
is fully specified and can be reconstructed when needed.

```
```
