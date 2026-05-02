use gpp_fidelity_core::{
    apply_move, boundary_vertices, build_round_robin_initial_state, eval_move_delta_cut,
    is_move_feasible, read_metis_graph, write_part_file, Block, Checkpoint, Rng64,
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
    initial_temp: f64,
    cooling: f64,
    min_temp: f64,
    max_steps: usize,
    checkpoint_every_nfe: usize,
}

#[derive(Clone, Debug)]
struct SaResult {
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

    let mut initial_temp = 1.0f64;
    let mut cooling = 0.995f64;
    let mut min_temp = 0.001f64;
    let mut max_steps = 10_000usize;
    let mut checkpoint_every_nfe = 100usize;

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
            "--initial-temp" => {
                initial_temp = value
                    .parse()
                    .map_err(|_| "invalid --initial-temp".to_string())?
            }
            "--cooling" => cooling = value.parse().map_err(|_| "invalid --cooling".to_string())?,
            "--min-temp" => {
                min_temp = value
                    .parse()
                    .map_err(|_| "invalid --min-temp".to_string())?
            }
            "--max-steps" => {
                max_steps = value
                    .parse()
                    .map_err(|_| "invalid --max-steps".to_string())?
            }
            "--checkpoint-every-nfe" => {
                checkpoint_every_nfe = value
                    .parse()
                    .map_err(|_| "invalid --checkpoint-every-nfe".to_string())?
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
        initial_temp,
        cooling,
        min_temp,
        max_steps,
        checkpoint_every_nfe,
    })
}

fn run_sa(config: &Config) -> Result<SaResult, String> {
    let adj = read_metis_graph(&config.graph_path)?;
    let mut state = build_round_robin_initial_state(adj, config.k, config.beta, config.seed)?;
    let mut rng = Rng64::new(config.seed);

    let mut best_part_of = state.part_of.clone();
    let mut best_cutsize = state.cutsize;
    let mut nfe = 0usize;
    let mut checkpoints = vec![Checkpoint {
        time_ms: 0,
        cutsize_best: best_cutsize,
        nfe: 0,
    }];

    let mut temp = config.initial_temp.max(1e-12);
    let t0 = Instant::now();
    let mut status = "ok".to_string();

    for _step in 0..config.max_steps {
        let elapsed_ms = t0.elapsed().as_millis();
        if elapsed_ms >= config.budget_time_ms {
            status = "timeout".to_string();
            break;
        }

        let candidates = boundary_vertices(&state);
        let Some(chosen_idx) = rng.choose_index(candidates.len()) else {
            break;
        };
        let v = candidates[chosen_idx];

        let mut target_blocks: Vec<usize> = (0..config.k).collect();
        rng.shuffle(&mut target_blocks);

        for target in target_blocks {
            if !is_move_feasible(&state, v, target) {
                continue;
            }

            let delta = eval_move_delta_cut(&state, v, target);
            nfe += 1;

            let mut accept = delta <= 0;
            if !accept {
                let accept_prob = (-(delta as f64) / temp.max(1e-12)).exp();
                accept = rng.gen_f64_unit() < accept_prob;
            }

            if accept {
                apply_move(&mut state, v, target);
                if state.cutsize < best_cutsize {
                    best_cutsize = state.cutsize;
                    best_part_of = state.part_of.clone();
                }
                break;
            }
        }

        temp = config.min_temp.max(temp * config.cooling);

        if config.checkpoint_every_nfe > 0 && nfe > 0 && nfe % config.checkpoint_every_nfe == 0 {
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

    Ok(SaResult {
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

fn serialize_result(result: &SaResult) -> String {
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
        "{{\"algo\":\"sa_rust\",\"status\":\"{}\",\"elapsed_ms\":{},\"nfe\":{},\"cutsize_best\":{},\"labels\":[{}],\"checkpoints\":[{}]}}",
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
    let result = run_sa(&config)?;

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
    use gpp_fidelity_core::read_metis_graph_str;
    use std::fs;

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
    fn sa_result_has_consistent_final_checkpoint() {
        let graph = write_temp_graph("sa_path", "6 5\n2\n1 3\n2 4\n3 5\n4 6\n5\n");
        let out_json = std::env::temp_dir().join(format!("sa_out_{}.json", std::process::id()));
        let part = std::env::temp_dir().join(format!("sa_part_{}.part", std::process::id()));

        let cfg = Config {
            graph_path: graph.clone(),
            out_json,
            part_path: part,
            k: 2,
            beta: 0.10,
            seed: 42,
            budget_time_ms: 1000,
            initial_temp: 1.0,
            cooling: 0.99,
            min_temp: 0.001,
            max_steps: 50,
            checkpoint_every_nfe: 5,
        };

        let result = run_sa(&cfg).expect("run sa");
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
        let cfg = Config {
            graph_path: PathBuf::new(),
            out_json: PathBuf::new(),
            part_path: PathBuf::new(),
            k: 2,
            beta: 0.10,
            seed: 7,
            budget_time_ms: 1000,
            initial_temp: 1.0,
            cooling: 0.99,
            min_temp: 0.001,
            max_steps: 10,
            checkpoint_every_nfe: 1,
        };
        let state = build_round_robin_initial_state(adj, cfg.k, cfg.beta, cfg.seed).expect("state");
        assert_eq!(state.part_of.len(), 4);
        assert_eq!(state.block_size.iter().sum::<usize>(), 4);
    }
}
