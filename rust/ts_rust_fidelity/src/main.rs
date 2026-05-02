use std::collections::HashMap;
use std::env;
use std::fs;
use std::io::Write;
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
    max_steps: usize,
    min_tenure: usize,
    tenure_scale: f64,
    tenure_jitter: usize,
    checkpoint_every_nfe: usize,
    frequency_penalty: f64,
}

#[derive(Clone, Debug)]
struct Checkpoint {
    time_ms: u128,
    cutsize_best: i64,
    nfe: usize,
}

#[derive(Clone, Debug)]
struct Candidate {
    score: f64,
    delta: i64,
    degree: usize,
    v: usize,
    target: usize,
    source: usize,
}

#[derive(Clone, Debug)]
struct PartitionState {
    adj: Vec<Vec<usize>>,
    part_of: Vec<usize>,
    block_size: Vec<usize>,
    k: usize,
    epsilon: f64,
    cutsize: i64,
    boundary: Vec<bool>,
}

#[derive(Clone, Debug)]
struct Rng64 {
    state: u64,
}

impl Rng64 {
    fn new(seed: u64) -> Self {
        let state = if seed == 0 {
            0x9E37_79B9_7F4A_7C15
        } else {
            seed
        };
        Self { state }
    }

    fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.state = x;
        x
    }

    fn gen_range_inclusive(&mut self, lo: usize, hi: usize) -> usize {
        if hi <= lo {
            return lo;
        }
        lo + (self.next_u64() % ((hi - lo + 1) as u64)) as usize
    }

    fn shuffle<T>(&mut self, xs: &mut [T]) {
        for i in (1..xs.len()).rev() {
            let j = self.gen_range_inclusive(0, i);
            xs.swap(i, j);
        }
    }
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

    let mut max_steps = 10_000usize;
    let mut min_tenure = 5usize;
    let mut tenure_scale = 1.0f64;
    let mut tenure_jitter = 4usize;
    let mut checkpoint_every_nfe = 100usize;
    let mut frequency_penalty = 0.01f64;

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
            "--max-steps" => {
                max_steps = value
                    .parse()
                    .map_err(|_| "invalid --max-steps".to_string())?
            }
            "--min-tenure" => {
                min_tenure = value
                    .parse()
                    .map_err(|_| "invalid --min-tenure".to_string())?
            }
            "--tenure-scale" => {
                tenure_scale = value
                    .parse()
                    .map_err(|_| "invalid --tenure-scale".to_string())?
            }
            "--tenure-jitter" => {
                tenure_jitter = value
                    .parse()
                    .map_err(|_| "invalid --tenure-jitter".to_string())?
            }
            "--checkpoint-every-nfe" => {
                checkpoint_every_nfe = value
                    .parse()
                    .map_err(|_| "invalid --checkpoint-every-nfe".to_string())?
            }
            "--frequency-penalty" => {
                frequency_penalty = value
                    .parse()
                    .map_err(|_| "invalid --frequency-penalty".to_string())?
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
        max_steps,
        min_tenure,
        tenure_scale,
        tenure_jitter,
        checkpoint_every_nfe,
        frequency_penalty,
    })
}

fn read_metis_graph(path: &PathBuf) -> Result<Vec<Vec<usize>>, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("failed to read graph: {e}"))?;
    let mut lines = content.lines().filter(|line| {
        let s = line.trim();
        !s.is_empty() && !s.starts_with('%')
    });

    let header = lines
        .next()
        .ok_or_else(|| "missing METIS header".to_string())?;
    let header_parts: Vec<&str> = header.split_whitespace().collect();
    if header_parts.len() < 2 {
        return Err("invalid METIS header".to_string());
    }

    let n: usize = header_parts[0]
        .parse()
        .map_err(|_| "invalid vertex count in METIS header".to_string())?;

    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];

    for u in 0..n {
        let Some(line) = lines.next() else {
            break;
        };
        for tok in line.split_whitespace() {
            let raw: usize = tok
                .parse()
                .map_err(|_| format!("invalid neighbor token: {tok}"))?;
            if raw == 0 {
                continue;
            }
            let v = raw - 1;
            if v >= n || v == u {
                continue;
            }
            adj[u].push(v);
            adj[v].push(u);
        }
    }

    for neigh in &mut adj {
        neigh.sort_unstable();
        neigh.dedup();
    }

    Ok(adj)
}

fn compute_cutsize(adj: &[Vec<usize>], part_of: &[usize]) -> i64 {
    let mut cut = 0i64;
    for u in 0..adj.len() {
        for &v in &adj[u] {
            if v <= u {
                continue;
            }
            if part_of[u] != part_of[v] {
                cut += 1;
            }
        }
    }
    cut
}

fn recompute_boundary(adj: &[Vec<usize>], part_of: &[usize]) -> Vec<bool> {
    let mut boundary = vec![false; adj.len()];
    for v in 0..adj.len() {
        let pv = part_of[v];
        boundary[v] = adj[v].iter().any(|&u| part_of[u] != pv);
    }
    boundary
}

fn build_initial_state(
    adj: Vec<Vec<usize>>,
    k: usize,
    epsilon: f64,
    seed: u64,
) -> Result<PartitionState, String> {
    if k == 0 {
        return Err("k must be positive".to_string());
    }
    if k > adj.len() {
        return Err("k cannot exceed the number of vertices".to_string());
    }

    let mut rng = Rng64::new(seed);
    let mut vertices: Vec<usize> = (0..adj.len()).collect();
    rng.shuffle(&mut vertices);

    let mut part_of = vec![0usize; adj.len()];
    let mut block_size = vec![0usize; k];

    for (i, &v) in vertices.iter().enumerate() {
        let block = i % k;
        part_of[v] = block;
        block_size[block] += 1;
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

fn max_block_size(state: &PartitionState) -> usize {
    ((1.0 + state.epsilon) * (state.part_of.len() as f64) / (state.k as f64)).ceil() as usize
}

fn is_move_feasible(state: &PartitionState, v: usize, target_block: usize) -> bool {
    let source = state.part_of[v];
    if source == target_block {
        return false;
    }

    let max_allowed = max_block_size(state);
    let new_source_size = state.block_size[source].saturating_sub(1);
    let new_target_size = state.block_size[target_block] + 1;

    if new_source_size == 0 {
        return false;
    }
    if new_source_size > max_allowed {
        return false;
    }
    new_target_size <= max_allowed
}

fn eval_move_delta_cut(state: &PartitionState, v: usize, target_block: usize) -> i64 {
    let source = state.part_of[v];
    if source == target_block {
        return 0;
    }

    let mut delta = 0i64;
    for &u in &state.adj[v] {
        let part_u = state.part_of[u];
        let before = if source != part_u { 1 } else { 0 };
        let after = if target_block != part_u { 1 } else { 0 };
        delta += after - before;
    }
    delta
}

fn refresh_boundary_flag(state: &mut PartitionState, x: usize) {
    let px = state.part_of[x];
    state.boundary[x] = state.adj[x].iter().any(|&u| state.part_of[u] != px);
}

fn apply_move(state: &mut PartitionState, v: usize, target_block: usize) {
    let source = state.part_of[v];
    if source == target_block {
        return;
    }

    let delta = eval_move_delta_cut(state, v, target_block);
    state.cutsize += delta;

    state.part_of[v] = target_block;
    state.block_size[source] -= 1;
    state.block_size[target_block] += 1;

    refresh_boundary_flag(state, v);
    let neighbors = state.adj[v].clone();
    for u in neighbors {
        refresh_boundary_flag(state, u);
    }
}

fn compute_tenure(n: usize, cfg: &Config, rng: &mut Rng64) -> usize {
    let scaled = (cfg.tenure_scale * (n as f64).sqrt()).round() as usize;
    let base = cfg.min_tenure.max(scaled);
    let jitter = rng.gen_range_inclusive(0, cfg.tenure_jitter);
    base + jitter
}

fn candidate_less(a: &Candidate, b: &Candidate) -> bool {
    let eps = 1e-12;
    if (a.score - b.score).abs() > eps {
        return a.score < b.score;
    }
    if a.delta != b.delta {
        return a.delta < b.delta;
    }
    if a.degree != b.degree {
        return a.degree < b.degree;
    }
    if a.v != b.v {
        return a.v < b.v;
    }
    if a.target != b.target {
        return a.target < b.target;
    }
    a.source < b.source
}

fn run_ts(
    adj: Vec<Vec<usize>>,
    cfg: &Config,
) -> Result<(PartitionState, i64, usize, Vec<Checkpoint>, String, u128), String> {
    let mut rng = Rng64::new(cfg.seed);
    let mut current = build_initial_state(adj, cfg.k, cfg.beta, cfg.seed)?;
    let mut best_part_of = current.part_of.clone();
    let mut best_cutsize = current.cutsize;

    let mut nfe = 0usize;
    let mut step = 0usize;
    let mut tabu_until: HashMap<(usize, usize), usize> = HashMap::new();
    let mut move_frequency: HashMap<(usize, usize), usize> = HashMap::new();
    let mut checkpoints = vec![Checkpoint {
        time_ms: 0,
        cutsize_best: best_cutsize,
        nfe: 0,
    }];

    let t0 = Instant::now();
    let mut status = "ok".to_string();

    while step < cfg.max_steps {
        let elapsed_ms = t0.elapsed().as_millis();
        if elapsed_ms >= cfg.budget_time_ms {
            status = "timeout".to_string();
            break;
        }

        let mut vertices: Vec<usize> = current
            .boundary
            .iter()
            .enumerate()
            .filter_map(|(idx, is_boundary)| if *is_boundary { Some(idx) } else { None })
            .collect();

        if vertices.is_empty() {
            vertices = (0..current.part_of.len()).collect();
        }
        rng.shuffle(&mut vertices);

        let mut best_move: Option<Candidate> = None;

        for v in vertices {
            let source = current.part_of[v];
            let mut targets: Vec<usize> = (0..current.k).collect();
            rng.shuffle(&mut targets);

            for target in targets {
                if target == source {
                    continue;
                }
                if !is_move_feasible(&current, v, target) {
                    continue;
                }

                let delta = eval_move_delta_cut(&current, v, target);
                nfe += 1;

                let candidate_cut = current.cutsize + delta;
                let is_tabu = tabu_until
                    .get(&(v, target))
                    .map(|until| step < *until)
                    .unwrap_or(false);
                let aspiration = candidate_cut < best_cutsize;

                if is_tabu && !aspiration {
                    continue;
                }

                let freq = *move_frequency.get(&(v, target)).unwrap_or(&0usize);
                let score = candidate_cut as f64 + cfg.frequency_penalty * freq as f64;
                let cand = Candidate {
                    score,
                    delta,
                    degree: current.adj[v].len(),
                    v,
                    target,
                    source,
                };

                if best_move
                    .as_ref()
                    .map(|old| candidate_less(&cand, old))
                    .unwrap_or(true)
                {
                    best_move = Some(cand);
                }
            }
        }

        let Some(chosen) = best_move else {
            break;
        };

        apply_move(&mut current, chosen.v, chosen.target);

        *move_frequency
            .entry((chosen.v, chosen.target))
            .or_insert(0usize) += 1;
        let tenure = compute_tenure(current.adj.len(), cfg, &mut rng);
        tabu_until.insert((chosen.v, chosen.source), step + tenure);

        if current.cutsize < best_cutsize {
            best_cutsize = current.cutsize;
            best_part_of = current.part_of.clone();
        }

        step += 1;

        if nfe > 0 && cfg.checkpoint_every_nfe > 0 && nfe % cfg.checkpoint_every_nfe == 0 {
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

    current.part_of = best_part_of;
    current.cutsize = best_cutsize;
    current.block_size = vec![0usize; current.k];
    for &b in &current.part_of {
        current.block_size[b] += 1;
    }
    current.boundary = recompute_boundary(&current.adj, &current.part_of);

    Ok((current, best_cutsize, nfe, checkpoints, status, elapsed_ms))
}

fn write_partition(path: &PathBuf, labels: &[usize]) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("failed to create part parent: {e}"))?;
    }

    let mut f = fs::File::create(path).map_err(|e| format!("failed to create part file: {e}"))?;
    for label in labels {
        writeln!(f, "{label}").map_err(|e| format!("failed to write part file: {e}"))?;
    }
    Ok(())
}

fn checkpoints_json(checkpoints: &[Checkpoint]) -> String {
    let mut parts: Vec<String> = Vec::with_capacity(checkpoints.len());
    for cp in checkpoints {
        parts.push(format!(
            "{{\"time_ms\":{},\"cutsize_best\":{},\"nfe\":{}}}",
            cp.time_ms, cp.cutsize_best, cp.nfe
        ));
    }
    format!("[{}]", parts.join(","))
}

fn labels_json(labels: &[usize]) -> String {
    labels
        .iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}

fn write_output(
    cfg: &Config,
    labels: &[usize],
    best_cutsize: i64,
    elapsed_ms: u128,
    nfe: usize,
    checkpoints: &[Checkpoint],
    status: &str,
) -> Result<(), String> {
    if let Some(parent) = cfg.out_json.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("failed to create output parent: {e}"))?;
    }

    let payload = format!(
        concat!(
            "{{",
            "\"algo\":\"ts_rust\",",
            "\"status\":\"{}\",",
            "\"elapsed_ms\":{},",
            "\"nfe\":{},",
            "\"cutsize_best\":{},",
            "\"labels\":[{}],",
            "\"checkpoints\":{},",
            "\"config\":{{",
            "\"k\":{},",
            "\"beta\":{},",
            "\"seed\":{},",
            "\"budget_time_ms\":{},",
            "\"max_steps\":{},",
            "\"min_tenure\":{},",
            "\"tenure_scale\":{},",
            "\"tenure_jitter\":{},",
            "\"checkpoint_every_nfe\":{},",
            "\"frequency_penalty\":{}",
            "}}",
            "}}\n"
        ),
        status,
        elapsed_ms,
        nfe,
        best_cutsize,
        labels_json(labels),
        checkpoints_json(checkpoints),
        cfg.k,
        cfg.beta,
        cfg.seed,
        cfg.budget_time_ms,
        cfg.max_steps,
        cfg.min_tenure,
        cfg.tenure_scale,
        cfg.tenure_jitter,
        cfg.checkpoint_every_nfe,
        cfg.frequency_penalty
    );

    fs::write(&cfg.out_json, payload).map_err(|e| format!("failed to write output JSON: {e}"))?;
    Ok(())
}

fn real_main() -> Result<(), String> {
    let cfg = parse_args()?;
    let adj = read_metis_graph(&cfg.graph_path)?;
    let (state, best_cutsize, nfe, checkpoints, status, elapsed_ms) = run_ts(adj, &cfg)?;

    write_partition(&cfg.part_path, &state.part_of)?;
    write_output(
        &cfg,
        &state.part_of,
        best_cutsize,
        elapsed_ms,
        nfe,
        &checkpoints,
        &status,
    )?;

    Ok(())
}

fn main() {
    if let Err(err) = real_main() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
