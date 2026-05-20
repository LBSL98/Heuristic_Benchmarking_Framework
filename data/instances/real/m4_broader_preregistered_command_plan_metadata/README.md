# M4 broader preregistered real-graph command-plan metadata

This directory records reduced command-plan metadata for bounded real-graph execution gates.

These records may define datasets, commands, `k` values, timeouts, resource limits, expected inputs, artifact locations, validation rules, metadata fields and server-side execution requirements. They do not execute solvers, extract or recompute quality metrics, authorize a full campaign, run synthetic expansion, run additional unplanned real graphs, run meta-heuristics, train CART, update result maps, write monograph claims, or commit raw/extracted/derived/input/output artifacts.

Long-running execution gates derived from these plans must be launched on `srv-noctua` in a detached server-side session such as `tmux`, with logs and status files written on the server. The user's WSL/notebook must not be required to remain online after the launch command returns.

## Current records

- `tigerline_roads_2025_06037_los_angeles_county_broader_preregistered_command_plan_1227.yaml`: preregisters a bounded single-dataset TigerLine command plan after the 1223 quality-metric review.
