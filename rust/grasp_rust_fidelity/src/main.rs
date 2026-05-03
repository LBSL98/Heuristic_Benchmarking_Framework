use gpp_fidelity_core::{
    apply_move, boundary_vertices, compute_cutsize, eval_move_delta_cut, is_move_feasible,
    max_block_size, read_metis_graph, recompute_boundary, write_part_file, Block, Checkpoint,
    Graph, PartitionState, Rng64, Vertex,
};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

const UNASSIGNED: usize = usize::MAX;

#[derive(Clone, Debug)]
struct Config {
    graph_path: PathBuf,
    out_json: PathBuf,
    part_path: PathBuf,
    k: usize,
    beta: f64,
    seed: u64,
    budget_time_ms: u128,
    alpha: f64,
    max_iters: usize,
    checkpoint_every_iter: usize,
}

#[derive(Clone, Debug)]
struct GraspResult {
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

    let mut alpha = 0.30f64;
    let mut max_iters = 100usize;
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
            "--alpha" => alpha = value.parse().map_err(|_| "invalid --alpha".to_string())?,
            "--max-iters" => {
                max_iters = value
                    .parse()
                    .map_err(|_| "invalid --max-iters".to_string())?
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
        alpha,
        max_iters,
        checkpoint_every_iter,
    })
}

fn choose_from(rng: &mut Rng64, xs: &[Block]) -> Result<Block, String> {
    let idx = rng
        .choose_index(xs.len())
        .ok_or_else(|| "cannot choose from empty candidate list".to_string())?;
    Ok(xs[idx])
}

fn construct_greedy_randomized_state(
    adj: Graph,
    k: usize,
    epsilon: f64,
    rng: &mut Rng64,
    alpha: f64,
) -> Result<PartitionState, String> {
    if k == 0 {
        return Err("k must be positive".to_string());
    }
    if k > adj.len() {
        return Err("k cannot exceed the number of vertices".to_string());
    }
    if !(0.0..=1.0).contains(&alpha) {
        return Err("alpha must be in [0,1]".to_string());
    }

    let n = adj.len();
    let mut vertices: Vec<Vertex> = (0..n).collect();
    rng.shuffle(&mut vertices);

    let cap = max_block_size(n, k, epsilon);
    let base_quota = n / k;
    let remainder = n % k;
    let target_size: Vec<usize> = (0..k)
        .map(|b| base_quota + if b < remainder { 1 } else { 0 })
        .collect();

    let mut part_of = vec![UNASSIGNED; n];
    let mut block_size = vec![0usize; k];

    for (block, &v) in vertices.iter().take(k).enumerate() {
        part_of[v] = block;
        block_size[block] += 1;
    }

    for &v in vertices.iter().skip(k) {
        let mut candidates: Vec<(usize, Block)> = Vec::new();

        for block in 0..k {
            if block_size[block] >= cap {
                continue;
            }
            if block_size[block] >= target_size[block] {
                continue;
            }

            let score = adj[v]
                .iter()
                .filter(|&&u| part_of[u] != UNASSIGNED && part_of[u] != block)
                .count();

            candidates.push((score, block));
        }

        let chosen = if candidates.is_empty() {
            let remaining_capacity: Vec<isize> = (0..k)
                .map(|block| target_size[block] as isize - block_size[block] as isize)
                .collect();

            let positive_blocks: Vec<Block> = (0..k)
                .filter(|&block| remaining_capacity[block] > 0)
                .collect();

            if !positive_blocks.is_empty() {
                let min_size = positive_blocks
                    .iter()
                    .map(|&block| block_size[block])
                    .min()
                    .ok_or_else(|| "no positive block candidates".to_string())?;
                let tied: Vec<Block> = positive_blocks
                    .into_iter()
                    .filter(|&block| block_size[block] == min_size)
                    .collect();
                choose_from(rng, &tied)?
            } else {
                let min_size = block_size
                    .iter()
                    .copied()
                    .min()
                    .ok_or_else(|| "no block candidates".to_string())?;
                let tied: Vec<Block> = (0..k)
                    .filter(|&block| block_size[block] == min_size)
                    .collect();
                choose_from(rng, &tied)?
            }
        } else {
            let s_min = candidates
                .iter()
                .map(|(score, _block)| *score)
                .min()
                .ok_or_else(|| "empty candidates".to_string())?;
            let s_max = candidates
                .iter()
                .map(|(score, _block)| *score)
                .max()
                .ok_or_else(|| "empty candidates".to_string())?;
            let threshold = s_min as f64 + alpha * ((s_max - s_min) as f64);

            let rcl: Vec<Block> = candidates
                .iter()
                .filter(|(score, _block)| (*score as f64) <= threshold + 1e-12)
                .map(|(_score, block)| *block)
                .collect();

            choose_from(rng, &rcl)?
        };

        part_of[v] = chosen;
        block_size[chosen] += 1;
    }

    if part_of.contains(&UNASSIGNED) {
        return Err("construction left unassigned vertices".to_string());
    }

    let cutsize = compute_cutsize(&adj, &part_of);
    let boundary = recompute_boundary(&adj, &part_of);

    Ok(PartitionState {
        adj,
        part_of,
        block_size,
        k,
        epsilon,
        cutsize,
        boundary,
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

fn run_grasp(config: &Config) -> Result<GraspResult, String> {
    let adj = read_metis_graph(&config.graph_path)?;
    let mut rng = Rng64::new(config.seed);
    let t0 = Instant::now();

    let initial = construct_greedy_randomized_state(
        adj.clone(),
        config.k,
        config.beta,
        &mut rng,
        config.alpha,
    )?;
    let (initial_after_descent, mut nfe) = first_improvement_descent(initial, &mut rng, 0);

    let mut best_part_of = initial_after_descent.part_of.clone();
    let mut best_cutsize = initial_after_descent.cutsize;

    let mut checkpoints = vec![Checkpoint {
        time_ms: 0,
        cutsize_best: best_cutsize,
        nfe,
    }];

    let mut status = "ok".to_string();

    for iteration in 1..config.max_iters {
        let elapsed_ms = t0.elapsed().as_millis();
        if elapsed_ms >= config.budget_time_ms {
            status = "timeout".to_string();
            break;
        }

        let candidate = construct_greedy_randomized_state(
            adj.clone(),
            config.k,
            config.beta,
            &mut rng,
            config.alpha,
        )?;
        let (candidate_after_descent, nfe_after_descent) =
            first_improvement_descent(candidate, &mut rng, nfe);
        nfe = nfe_after_descent;

        if candidate_after_descent.cutsize < best_cutsize {
            best_part_of = candidate_after_descent.part_of.clone();
            best_cutsize = candidate_after_descent.cutsize;
        }

        if config.checkpoint_every_iter > 0 && iteration % config.checkpoint_every_iter == 0 {
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

    Ok(GraspResult {
        status,
        elapsed_ms,
        nfe,
        cutsize_best: best_cutsize,
        labels: best_part_of,
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

fn serialize_result(result: &GraspResult) -> String {
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
        "{{\"algo\":\"grasp_rust\",\"status\":\"{}\",\"elapsed_ms\":{},\"nfe\":{},\"cutsize_best\":{},\"labels\":[{}],\"checkpoints\":[{}]}}",
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
    let result = run_grasp(&config)?;

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
    use gpp_fidelity_core::{read_metis_graph_str, recompute_boundary};
    use std::fs;

    fn path_graph(n: usize) -> Graph {
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
    fn construction_is_balanced_and_consistent() {
        let adj = path_graph(10);
        let mut rng = Rng64::new(42);

        let state =
            construct_greedy_randomized_state(adj.clone(), 2, 0.03, &mut rng, 0.30).expect("state");

        let mut sizes = state.block_size.clone();
        sizes.sort_unstable();

        assert_eq!(sizes, vec![5, 5]);
        assert_eq!(state.cutsize, compute_cutsize(&adj, &state.part_of));
        assert_eq!(state.boundary, recompute_boundary(&adj, &state.part_of));
    }

    #[test]
    fn construction_rejects_invalid_alpha() {
        let adj = path_graph(6);
        let mut rng = Rng64::new(42);

        assert!(construct_greedy_randomized_state(adj, 2, 0.10, &mut rng, 1.50).is_err());
    }

    #[test]
    fn first_improvement_descent_never_worsens_cut() {
        let adj = path_graph(12);
        let mut rng = Rng64::new(42);
        let state =
            construct_greedy_randomized_state(adj.clone(), 3, 0.10, &mut rng, 0.30).expect("state");
        let initial_cut = state.cutsize;

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
    fn grasp_result_has_consistent_final_checkpoint() {
        let graph = write_temp_graph("grasp_path", "6 5\n2\n1 3\n2 4\n3 5\n4 6\n5\n");
        let out_json = std::env::temp_dir().join(format!("grasp_out_{}.json", std::process::id()));
        let part = std::env::temp_dir().join(format!("grasp_part_{}.part", std::process::id()));

        let cfg = Config {
            graph_path: graph.clone(),
            out_json,
            part_path: part,
            k: 2,
            beta: 0.10,
            seed: 42,
            budget_time_ms: 1000,
            alpha: 0.30,
            max_iters: 30,
            checkpoint_every_iter: 1,
        };

        let result = run_grasp(&cfg).expect("run grasp");
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
        let mut rng = Rng64::new(7);
        let state = construct_greedy_randomized_state(adj, 2, 0.10, &mut rng, 0.30).expect("state");
        assert_eq!(state.part_of.len(), 4);
        assert_eq!(state.block_size.iter().sum::<usize>(), 4);
    }
}
