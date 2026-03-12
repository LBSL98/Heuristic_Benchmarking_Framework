# CLI: `generator.cli` (synthetic instance generator)

The `generator` module implements the **synthetic instance generator** used throughout the project.
It is responsible for creating graphs with controlled properties, such as:

- number of vertices;
- edge density or related connectivity parameters;
- degree / “speed” heterogeneity (coefficient-of-variation bands);
- other structural features relevant for the experimental design.

Generated instances are stored as JSON documents (optionally gzip-compressed) that conform to the
input schema:

```text
specs/schema_input.json
````

These files are later consumed by the core operators and external solvers via the
`hpc_framework` runner.

---

## Invoking the CLI

After installing the project (preferably via Poetry), the generator can be inspected with:

```bash
poetry run python -m generator.cli --help
```

This command prints the available subcommands and options, including:

* how to choose the number of nodes;
* how to control density / sparsity;
* how to select variability regimes (e.g. degree or “speed” heterogeneity);
* how to fix RNG seeds;
* how to select the output path and compression.

The exact flag names and defaults may evolve with the project; the `--help` output is the
authoritative source for the current version.

---

## Output format and location

By convention, synthetic instances are stored under:

```text
data/instances/synthetic/
```

For example, a file named:

```text
data/instances/synthetic/n2000_p50.json.gz
```

encodes a graph with roughly 2000 vertices and a target density of about 0.50,
together with any additional attributes required by the experimental protocol (e.g. vertex weights).

Each JSON instance is validated against `specs/schema_input.json` during the pipeline, ensuring that:

* required fields are present and properly typed;
* user-defined regimes (e.g. number of nodes, density bands) are honoured within tolerance;
* the graph structure is consistent (e.g. no malformed edges, basic connectivity checks).

---

## Batch generation via configuration

While individual instances can be generated directly from the CLI, the typical workflow for
experiments is **batch-oriented**:

1. A configuration file (e.g. `configs/instances_to_generate.yaml`) defines regimes and targets:

   * node counts;
   * density / sparsity regimes;
   * heterogeneity bands;
   * number of instances per regime.

2. A pipeline script (e.g. one of the helpers under `scripts/`) reads this configuration and
   calls the generator CLI repeatedly, materialising a panel of instances under `data/instances/`.

3. Experiment plans (such as `configs/plan_phase_1.yaml`) refer to these generated instances
   when defining the instance panel for each phase.

The exact pipeline script and YAML layout are documented in more detail in the *Instance generator*
report under `docs/reports/`.

---

## Design goals

The generator is designed to support the following goals:

* **Control**: allow precise control over graph regimes used in benchmarking.
* **Reproducibility**: expose explicit seeding and configuration so that panels can be
  reconstructed from YAML and logs.
* **Compatibility**: produce instances that are immediately compatible with the partitioning
  pipeline (no ad-hoc conversion steps).

For details of the underlying models and validation procedures, refer to:

* `docs/reports/01_instance_generator.md` (conceptual overview and validation);
* `specs/bounds.json` and related specification files.

```
```
