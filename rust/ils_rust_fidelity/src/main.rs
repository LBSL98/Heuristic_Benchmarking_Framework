use gpp_fidelity_core::{
    apply_move, boundary_vertices, build_round_robin_initial_state, eval_move_delta_cut,
    is_move_feasible, read_metis_graph, write_part_file, Block, Checkpoint, PartitionState, Rng64,
    Vertex,
};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

#[derive(Clone, Debug)]
struct Config {
    graph_path: PathBuf,
    out_json: PathBuf,
    part_path: PathBuf,
    k: usize,
    beta: f64,
    seed: u64,
    budget_time_ms: u128,
    max_iters: usize,
    perturb_moves: usize,
    checkpoint_every_iter: usize,
}

#[derive(Clone, Debug)]
struct IlsResult {
    status: String,
    elapsed_ms: u128,
    nfe: usize,
    cutsize_best: i64,
    labels: Vec<Block>,
    checkpoints: Vec<Checkpoint>,
}

fn parse_args() -> Result<Config, String> {
    let args: Vec<String> = env::args().collect();

    let mut graph_path: Option<PathBuf> = None;
    let mut out_json: Option<PathBuf> = None;
    let mut part_path: Option<PathBuf> = None;
    let mut k: Option<usize> = None;
    let mut beta: Option<f64> = None;
    let mut seed: Option<u64> = None;
    let mut budget_time_ms: Option<u128> = None;

    let mut max_iters = 100usize;
    let mut perturb_moves = 4usize;
    let mut checkpoint_every_iter = 1usize;

    let mut i = 1usize;
    while i < args.len() {
        let key = args[i].as_str();
        let value = args
            .get(i + 1)
            .ok_or_else(|| format!("missing value for {key}"))?;

        match key {
            "--graph" => graph_path = Some(PathBuf::from(value)),
            "--out-json" => out_json = Some(PathBuf::from(value)),
            "--part" => part_path = Some(PathBuf::from(value)),
            "--k" => k = Some(value.parse().map_err(|_| "invalid --k".to_string())?),
            "--beta" => beta = Some(value.parse().map_err(|_| "invalid --beta".to_string())?),
            "--seed" => seed = Some(value.parse().map_err(|_| "invalid --seed".to_string())?),
            "--budget-time-ms" => {
                budget_time_ms = Some(
                    value
                        .parse()
                        .map_err(|_| "invalid --budget-time-ms".to_string())?,
                )
            }
            "--max-iters" => {
                max_iters = value
                    .parse()
                    .map_err(|_| "invalid --max-iters".to_string())?
            }
            "--perturb-moves" => {
                perturb_moves = value
                    .parse()
                    .map_err(|_| "invalid --perturb-moves".to_string())?
            }
            "--checkpoint-every-iter" => {
                checkpoint_every_iter = value
                    .parse()
                    .map_err(|_| "invalid --checkpoint-every-iter".to_string())?
            }
            _ => return Err(format!("unknown argument: {key}")),
        }

        i += 2;
    }

    Ok(Config {
        graph_path: graph_path.ok_or_else(|| "missing --graph".to_string())?,
        out_json: out_json.ok_or_else(|| "missing --out-json".to_string())?,
        part_path: part_path.ok_or_else(|| "missing --part".to_string())?,
        k: k.ok_or_else(|| "missing --k".to_string())?,
        beta: beta.ok_or_else(|| "missing --beta".to_string())?,
        seed: seed.ok_or_else(|| "missing --seed".to_string())?,
        budget_time_ms: budget_time_ms.ok_or_else(|| "missing --budget-time-ms".to_string())?,
        max_iters,
        perturb_moves,
        checkpoint_every_iter,
    })
}

fn first_improvement_descent(
    mut state: PartitionState,
    rng: &mut Rng64,
    nfe_start: usize,
) -> (PartitionState, usize) {
    let mut nfe = nfe_start;

    loop {
        let mut improved = false;
        let mut vertices = boundary_vertices(&state);
        rng.shuffle(&mut vertices);

        for v in vertices {
            let mut targets: Vec<Block> = (0..state.k).collect();
            rng.shuffle(&mut targets);

            for target in targets {
                if target == state.part_of[v] {
                    continue;
                }
                if !is_move_feasible(&state, v, target) {
                    continue;
                }

                let delta = eval_move_delta_cut(&state, v, target);
                nfe += 1;

                if delta < 0 {
                    apply_move(&mut state, v, target);
                    improved = true;
                    break;
                }
            }

            if improved {
                break;
            }
        }

        if !improved {
            return (state, nfe);
        }
    }
}

fn perturb_state(state: &mut PartitionState, rng: &mut Rng64, moves: usize) {
    let mut vertices: Vec<Vertex> = (0..state.part_of.len()).collect();

    for _ in 0..usize::max(1, moves) {
        rng.shuffle(&mut vertices);
        let mut moved = false;

        for &v in &vertices {
            let mut targets: Vec<Block> = (0..state.k).collect();
            rng.shuffle(&mut targets);

            for target in targets {
                if target == state.part_of[v] {
                    continue;
                }
                if !is_move_feasible(state, v, target) {
                    continue;
                }

                apply_move(state, v, target);
                moved = true;
                break;
            }

            if moved {
                break;
            }
        }
    }
}

fn run_ils(config: &Config) -> Result<IlsResult, String> {
    let adj = read_metis_graph(&config.graph_path)?;
    let initial = build_round_robin_initial_state(adj, config.k, config.beta, config.seed)?;
    let mut rng = Rng64::new(config.seed);

    let (mut current, mut nfe) = first_improvement_descent(initial, &mut rng, 0);
    let mut best = current.clone();
    let mut best_cutsize = current.cutsize;

    let mut checkpoints = vec![Checkpoint {
        time_ms: 0,
        cutsize_best: best_cutsize,
        nfe,
    }];

    let t0 = Instant::now();
    let mut status = "ok".to_string();

    for iteration in 0..config.max_iters {
        let elapsed_ms = t0.elapsed().as_millis();
        if elapsed_ms >= config.budget_time_ms {
            status = "timeout".to_string();
            break;
        }

        let mut candidate = current.clone();
        perturb_state(&mut candidate, &mut rng, config.perturb_moves);
        let (candidate_after_descent, nfe_after_descent) =
            first_improvement_descent(candidate, &mut rng, nfe);
        candidate = candidate_after_descent;
        nfe = nfe_after_descent;

        if candidate.cutsize <= current.cutsize {
            current = candidate.clone();
        }

        if candidate.cutsize < best_cutsize {
            best = candidate.clone();
            best_cutsize = candidate.cutsize;
        }

        if config.checkpoint_every_iter > 0 && (iteration + 1) % config.checkpoint_every_iter == 0 {
            checkpoints.push(Checkpoint {
                time_ms: t0.elapsed().as_millis(),
                cutsize_best: best_cutsize,
                nfe,
            });
        }
    }

    let elapsed_ms = t0.elapsed().as_millis();
    let needs_final = checkpoints
        .last()
        .map(|cp| cp.nfe != nfe || cp.cutsize_best != best_cutsize)
        .unwrap_or(true);

    if needs_final {
        checkpoints.push(Checkpoint {
            time_ms: elapsed_ms,
            cutsize_best: best_cutsize,
            nfe,
        });
    }

    Ok(IlsResult {
        status,
        elapsed_ms,
        nfe,
        cutsize_best: best_cutsize,
        labels: best.part_of,
        checkpoints,
    })
}

fn json_escape(value: &str) -> String {
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

fn serialize_result(result: &IlsResult) -> String {
    let labels = result
        .labels
        .iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",");

    let checkpoints = result
        .checkpoints
        .iter()
        .map(|cp| {
            format!(
                "{{\"time_ms\":{},\"cutsize_best\":{},\"nfe\":{}}}",
                cp.time_ms, cp.cutsize_best, cp.nfe
            )
        })
        .collect::<Vec<_>>()
        .join(",");

    format!(
        "{{\"algo\":\"ils_rust\",\"status\":\"{}\",\"elapsed_ms\":{},\"nfe\":{},\"cutsize_best\":{},\"labels\":[{}],\"checkpoints\":[{}]}}",
        json_escape(&result.status),
        result.elapsed_ms,
        result.nfe,
        result.cutsize_best,
        labels,
        checkpoints
    )
}

fn run() -> Result<(), String> {
    let config = parse_args()?;
    let result = run_ils(&config)?;

    if let Some(parent) = config.part_path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("failed to create part parent: {e}"))?;
    }
    if let Some(parent) = config.out_json.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("failed to create json parent: {e}"))?;
    }

    write_part_file(&config.part_path, &result.labels)?;
    fs::write(&config.out_json, serialize_result(&result))
        .map_err(|e| format!("failed to write output json: {e}"))?;

    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use gpp_fidelity_core::{compute_cutsize, read_metis_graph_str, recompute_boundary};
    use std::fs;

    fn path_graph(n: usize) -> Vec<Vec<Vertex>> {
        let mut adj = vec![Vec::new(); n];
        for i in 0..n - 1 {
            adj[i].push(i + 1);
            adj[i + 1].push(i);
        }
        adj
    }

    fn write_temp_graph(name: &str, body: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "{}_{}_{}.graph",
            name,
            std::process::id(),
            Instant::now().elapsed().as_nanos()
        ));
        fs::write(&path, body).expect("write graph");
        path
    }

    #[test]
    fn first_improvement_descent_never_worsens_cut() {
        let adj = path_graph(12);
        let state = build_round_robin_initial_state(adj.clone(), 3, 0.10, 42).expect("state");
        let initial_cut = state.cutsize;
        let mut rng = Rng64::new(42);

        let (result_state, nfe) = first_improvement_descent(state, &mut rng, 0);

        assert!(nfe > 0);
        assert!(result_state.cutsize <= initial_cut);
        assert_eq!(
            result_state.cutsize,
            compute_cutsize(&adj, &result_state.part_of)
        );
        assert_eq!(
            result_state.boundary,
            recompute_boundary(&result_state.adj, &result_state.part_of)
        );
    }

    #[test]
    fn perturb_state_keeps_partition_consistent() {
        let adj = path_graph(10);
        let mut state = build_round_robin_initial_state(adj.clone(), 2, 0.10, 7).expect("state");
        let mut rng = Rng64::new(7);

        perturb_state(&mut state, &mut rng, 3);

        assert_eq!(state.part_of.len(), 10);
        assert_eq!(state.block_size.iter().sum::<usize>(), 10);
        assert_eq!(state.cutsize, compute_cutsize(&adj, &state.part_of));
        assert_eq!(state.boundary, recompute_boundary(&adj, &state.part_of));
    }

    #[test]
    fn ils_result_has_consistent_final_checkpoint() {
        let graph = write_temp_graph("ils_path", "6 5\n2\n1 3\n2 4\n3 5\n4 6\n5\n");
        let out_json = std::env::temp_dir().join(format!("ils_out_{}.json", std::process::id()));
        let part = std::env::temp_dir().join(format!("ils_part_{}.part", std::process::id()));

        let cfg = Config {
            graph_path: graph.clone(),
            out_json,
            part_path: part,
            k: 2,
            beta: 0.10,
            seed: 42,
            budget_time_ms: 1000,
            max_iters: 30,
            perturb_moves: 2,
            checkpoint_every_iter: 1,
        };

        let result = run_ils(&cfg).expect("run ils");
        let last = result.checkpoints.last().expect("last checkpoint");

        assert_eq!(last.cutsize_best, result.cutsize_best);
        assert_eq!(last.nfe, result.nfe);
        assert_eq!(result.labels.len(), 6);
        assert!(result
            .checkpoints
            .windows(2)
            .all(|w| w[0].time_ms <= w[1].time_ms));
        assert!(result
            .checkpoints
            .windows(2)
            .all(|w| w[0].cutsize_best >= w[1].cutsize_best));
        assert!(result.checkpoints.windows(2).all(|w| w[0].nfe <= w[1].nfe));

        let _ = fs::remove_file(graph);
    }

    #[test]
    fn parser_surface_is_compatible_with_core() {
        let adj = read_metis_graph_str("4 3\n2\n1 3\n2 4\n3\n").expect("graph");
        let state = build_round_robin_initial_state(adj, 2, 0.10, 7).expect("state");
        assert_eq!(state.part_of.len(), 4);
        assert_eq!(state.block_size.iter().sum::<usize>(), 4);
    }
}
