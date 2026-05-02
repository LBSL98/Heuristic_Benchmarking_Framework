use std::fs;
use std::path::Path;

pub type Vertex = usize;
pub type Block = usize;
pub type Graph = Vec<Vec<Vertex>>;

#[derive(Clone, Debug, PartialEq)]
pub struct PartitionState {
    pub adj: Graph,
    pub part_of: Vec<Block>,
    pub block_size: Vec<usize>,
    pub k: usize,
    pub epsilon: f64,
    pub cutsize: i64,
    pub boundary: Vec<bool>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Checkpoint {
    pub time_ms: u128,
    pub cutsize_best: i64,
    pub nfe: usize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FidelityPayload {
    pub algo: String,
    pub status: String,
    pub elapsed_ms: u128,
    pub nfe: usize,
    pub cutsize_best: i64,
    pub labels: Vec<Block>,
    pub checkpoints: Vec<Checkpoint>,
}

#[derive(Clone, Debug)]
pub struct Rng64 {
    state: u64,
}

impl Rng64 {
    pub fn new(seed: u64) -> Self {
        let state = if seed == 0 {
            0x9E37_79B9_7F4A_7C15
        } else {
            seed
        };
        Self { state }
    }

    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.state = x;
        x
    }

    pub fn gen_range_inclusive(&mut self, lo: usize, hi: usize) -> usize {
        if hi <= lo {
            return lo;
        }
        lo + (self.next_u64() % ((hi - lo + 1) as u64)) as usize
    }

    pub fn gen_f64_unit(&mut self) -> f64 {
        const DENOM: f64 = u64::MAX as f64;
        (self.next_u64() as f64) / DENOM
    }

    pub fn shuffle<T>(&mut self, xs: &mut [T]) {
        for i in (1..xs.len()).rev() {
            let j = self.gen_range_inclusive(0, i);
            xs.swap(i, j);
        }
    }

    pub fn choose_index(&mut self, len: usize) -> Option<usize> {
        if len == 0 {
            None
        } else {
            Some(self.gen_range_inclusive(0, len - 1))
        }
    }
}

pub fn read_metis_graph(path: &Path) -> Result<Graph, String> {
    let content = fs::read_to_string(path).map_err(|e| format!("failed to read graph: {e}"))?;
    read_metis_graph_str(&content)
}

pub fn read_metis_graph_str(content: &str) -> Result<Graph, String> {
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

    let mut adj: Graph = vec![Vec::new(); n];

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

    normalize_graph(&mut adj);
    Ok(adj)
}

pub fn normalize_graph(adj: &mut Graph) {
    for neigh in adj {
        neigh.sort_unstable();
        neigh.dedup();
    }
}

pub fn compute_cutsize(adj: &[Vec<Vertex>], part_of: &[Block]) -> i64 {
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

pub fn recompute_boundary(adj: &[Vec<Vertex>], part_of: &[Block]) -> Vec<bool> {
    let mut boundary = vec![false; adj.len()];
    for v in 0..adj.len() {
        let pv = part_of[v];
        boundary[v] = adj[v].iter().any(|&u| part_of[u] != pv);
    }
    boundary
}

pub fn max_block_size(n: usize, k: usize, epsilon: f64) -> usize {
    ((1.0 + epsilon) * (n as f64) / (k as f64)).ceil() as usize
}

pub fn is_move_feasible(state: &PartitionState, v: Vertex, target_block: Block) -> bool {
    if v >= state.part_of.len() || target_block >= state.k {
        return false;
    }

    let source = state.part_of[v];
    if source == target_block {
        return false;
    }

    let max_size = max_block_size(state.part_of.len(), state.k, state.epsilon);
    let new_source_size = state.block_size[source].saturating_sub(1);
    let new_target_size = state.block_size[target_block] + 1;

    if new_source_size == 0 {
        return false;
    }
    if new_source_size > max_size {
        return false;
    }
    new_target_size <= max_size
}

pub fn eval_move_delta_cut(state: &PartitionState, v: Vertex, target_block: Block) -> i64 {
    if v >= state.part_of.len() {
        return 0;
    }

    let source = state.part_of[v];
    if source == target_block {
        return 0;
    }

    let mut delta = 0i64;
    for &u in &state.adj[v] {
        let part_u = state.part_of[u];
        let is_cut_before = if source != part_u { 1 } else { 0 };
        let is_cut_after = if target_block != part_u { 1 } else { 0 };
        delta += is_cut_after - is_cut_before;
    }
    delta
}

pub fn apply_move(state: &mut PartitionState, v: Vertex, target_block: Block) {
    if v >= state.part_of.len() {
        return;
    }

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

pub fn refresh_boundary_flag(state: &mut PartitionState, v: Vertex) {
    let pv = state.part_of[v];
    state.boundary[v] = state.adj[v].iter().any(|&u| state.part_of[u] != pv);
}

pub fn build_round_robin_initial_state(
    adj: Graph,
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
    let mut vertices: Vec<Vertex> = (0..adj.len()).collect();
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

pub fn boundary_vertices(state: &PartitionState) -> Vec<Vertex> {
    let mut xs = Vec::new();
    for (v, is_boundary) in state.boundary.iter().enumerate() {
        if *is_boundary {
            xs.push(v);
        }
    }
    if xs.is_empty() {
        (0..state.part_of.len()).collect()
    } else {
        xs
    }
}

pub fn write_part_file(path: &Path, labels: &[Block]) -> Result<(), String> {
    let mut body = String::new();
    for label in labels {
        body.push_str(&format!("{label}\n"));
    }
    fs::write(path, body).map_err(|e| format!("failed to write part file: {e}"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn path_graph(n: usize) -> Graph {
        let mut adj = vec![Vec::new(); n];
        for i in 0..n - 1 {
            adj[i].push(i + 1);
            adj[i + 1].push(i);
        }
        adj
    }

    #[test]
    fn metis_parser_accepts_symmetric_input_and_deduplicates() {
        let content = "4 3\n2\n1 3\n2 4\n3\n";
        let adj = read_metis_graph_str(content).expect("valid graph");
        assert_eq!(adj, vec![vec![1], vec![0, 2], vec![1, 3], vec![2]]);
    }

    #[test]
    fn metis_parser_ignores_comments_blank_lines_self_loops_and_zeroes() {
        let content = "% comment\n\n3 2\n2 1 0\n1 3\n2 3\n";
        let adj = read_metis_graph_str(content).expect("valid graph");
        assert_eq!(adj, vec![vec![1], vec![0, 2], vec![1]]);
    }

    #[test]
    fn cutsize_matches_edge_cut_definition() {
        let adj = path_graph(4);
        let part_of = vec![0, 0, 1, 1];
        assert_eq!(compute_cutsize(&adj, &part_of), 1);
    }

    #[test]
    fn boundary_matches_cut_incidence() {
        let adj = path_graph(4);
        let part_of = vec![0, 0, 1, 1];
        assert_eq!(
            recompute_boundary(&adj, &part_of),
            vec![false, true, true, false]
        );
    }

    #[test]
    fn round_robin_initial_state_is_balanced_and_consistent() {
        let adj = path_graph(10);
        let state = build_round_robin_initial_state(adj.clone(), 2, 0.03, 42).expect("state");
        let mut sizes = state.block_size.clone();
        sizes.sort_unstable();

        assert_eq!(sizes, vec![5, 5]);
        assert_eq!(state.cutsize, compute_cutsize(&adj, &state.part_of));
        assert_eq!(state.boundary, recompute_boundary(&adj, &state.part_of));
    }

    #[test]
    fn move_feasibility_prevents_empty_blocks_and_oversized_targets() {
        let adj = path_graph(4);
        let state = PartitionState {
            adj,
            part_of: vec![0, 0, 1, 1],
            block_size: vec![2, 2],
            k: 2,
            epsilon: 0.0,
            cutsize: 1,
            boundary: vec![false, true, true, false],
        };

        assert!(!is_move_feasible(&state, 0, 1));
        assert!(!is_move_feasible(&state, 0, 0));

        let state2 = PartitionState {
            part_of: vec![0, 1, 1, 1],
            block_size: vec![1, 3],
            cutsize: 1,
            boundary: vec![true, true, false, false],
            ..state
        };
        assert!(!is_move_feasible(&state2, 0, 1));
    }

    #[test]
    fn delta_and_apply_move_match_full_recomputation() {
        let adj = path_graph(5);
        let mut state = PartitionState {
            adj: adj.clone(),
            part_of: vec![0, 0, 1, 1, 1],
            block_size: vec![2, 3],
            k: 2,
            epsilon: 0.50,
            cutsize: compute_cutsize(&adj, &[0, 0, 1, 1, 1]),
            boundary: recompute_boundary(&adj, &[0, 0, 1, 1, 1]),
        };

        assert!(is_move_feasible(&state, 2, 0));
        let delta = eval_move_delta_cut(&state, 2, 0);
        apply_move(&mut state, 2, 0);

        assert_eq!(state.cutsize, compute_cutsize(&state.adj, &state.part_of));
        assert_eq!(state.cutsize, 1 + delta);
        assert_eq!(
            state.boundary,
            recompute_boundary(&state.adj, &state.part_of)
        );
        assert_eq!(state.block_size, vec![3, 2]);
    }

    #[test]
    fn boundary_vertices_falls_back_to_all_vertices() {
        let state = PartitionState {
            adj: vec![vec![], vec![], vec![]],
            part_of: vec![0, 0, 1],
            block_size: vec![2, 1],
            k: 2,
            epsilon: 0.50,
            cutsize: 0,
            boundary: vec![false, false, false],
        };

        assert_eq!(boundary_vertices(&state), vec![0, 1, 2]);
    }

    #[test]
    fn write_part_file_writes_one_label_per_line() {
        let path = std::env::temp_dir().join(format!(
            "gpp_fidelity_core_part_{}.part",
            std::process::id()
        ));

        write_part_file(&path, &[0, 1, 1, 0]).expect("write part");
        let body = fs::read_to_string(&path).expect("read part");
        let _ = fs::remove_file(&path);

        assert_eq!(body, "0\n1\n1\n0\n");
    }
}
