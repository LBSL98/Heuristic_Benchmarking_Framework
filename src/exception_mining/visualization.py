"""Render auditable SVG previews from exception-mining bundle artifacts."""

from __future__ import annotations

import gzip
import html
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

ColorEncoding = Literal["degree", "planted_block", "solver_partition", "none"]
RenderScope = Literal["auto", "full", "sample"]

DEFAULT_WIDTH = 900
DEFAULT_HEIGHT = 900
DEFAULT_NODE_RADIUS = 5.0

CATEGORICAL_PALETTE = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ab",
]


@dataclass(frozen=True)
class RenderResult:
    """Summary of one rendered exception-mining graph preview."""

    bundle_path: str
    output_path: str
    report_path: str
    image_scope: str
    color_by: str
    layout_algorithm: str
    layout_seed: int | None
    rendered_nodes: int
    rendered_edges: int
    illustrative: bool


@dataclass(frozen=True)
class _RenderData:
    nodes: list[int]
    edges: list[tuple[int, int]]
    positions: dict[int, tuple[float, float]]
    degrees: dict[int, int]
    labels: dict[int, str]
    warnings: list[str]


def render_bundle_preview(
    bundle_path: Path,
    output_path: Path | None = None,
    report_path: Path | None = None,
    *,
    scope: RenderScope = "auto",
    color_by: ColorEncoding = "degree",
    solver_partition_path: Path | None = None,
    validated_solver_artifact: bool = False,
    title: str | None = None,
) -> RenderResult:
    """Render one static SVG preview from stored exception-mining bundle artifacts.

    The function consumes only saved bundle artifacts. It does not call the graph
    generator, recompute layouts, run solvers, infer winners, or create empirical
    benchmark claims.
    """

    bundle_path = bundle_path.resolve()
    if not bundle_path.is_dir():
        raise FileNotFoundError(f"bundle path is not a directory: {bundle_path}")

    layout = _read_json_object(bundle_path / "graph_preview_layout.json")
    sample = _read_json_object(bundle_path / "graph_preview_sample.json")
    metadata = _read_json_object(bundle_path / "visualization_metadata.json")
    instance = _read_instance(bundle_path / "instance.json.gz")
    full_edges = _read_edgelist(bundle_path / "graph_edges.edgelist")

    resolved_scope = _resolve_scope(scope, layout, sample)
    data = _prepare_render_data(
        instance=instance,
        layout=layout,
        sample=sample,
        full_edges=full_edges,
        scope=resolved_scope,
        color_by=color_by,
        solver_partition_path=solver_partition_path,
    )

    if output_path is None:
        output_path = bundle_path / f"graph_preview_{resolved_scope}_{color_by}.svg"
    if report_path is None:
        report_path = bundle_path / f"visualization_report_{resolved_scope}_{color_by}.json"

    output_path = output_path.resolve()
    report_path = report_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    layout_algorithm = str(layout.get("layout_algorithm", "unknown"))
    layout_seed = _optional_int(layout.get("layout_seed"))
    sampling_policy = str(sample.get("sampling_policy", "unknown"))

    solver_artifact_used = solver_partition_path is not None
    illustrative = not (solver_artifact_used and validated_solver_artifact)

    report: dict[str, Any] = {
        "bundle_path": str(bundle_path),
        "output_path": str(output_path),
        "image_type": "svg",
        "image_scope": resolved_scope,
        "sampling_policy": sampling_policy,
        "layout_algorithm": layout_algorithm,
        "layout_seed": layout_seed,
        "layout_parameters": layout.get("layout_parameters", {}),
        "color_by": color_by,
        "available_encodings": metadata.get("available_encodings", []),
        "rendered_nodes": len(data.nodes),
        "rendered_edges": len(data.edges),
        "solver_partition_path": str(solver_partition_path) if solver_partition_path else None,
        "validated_solver_artifact": validated_solver_artifact,
        "illustrative": illustrative,
        "warnings": data.warnings,
        "notes": (
            "Preview generated from stored artifacts. It is illustrative unless paired "
            "with a declared validated solver partition artifact."
        ),
    }

    svg = _render_svg(
        data=data,
        report=report,
        title=title or _default_title(bundle_path, resolved_scope, color_by),
    )
    output_path.write_text(svg, encoding="utf-8")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return RenderResult(
        bundle_path=str(bundle_path),
        output_path=str(output_path),
        report_path=str(report_path),
        image_scope=resolved_scope,
        color_by=color_by,
        layout_algorithm=layout_algorithm,
        layout_seed=layout_seed,
        rendered_nodes=len(data.nodes),
        rendered_edges=len(data.edges),
        illustrative=illustrative,
    )


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return cast(dict[str, Any], data)


def _read_instance(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("instance.json.gz must contain a JSON object")
    return cast(dict[str, Any], data)


def _read_edgelist(path: Path) -> list[tuple[int, int]]:
    if not path.exists():
        raise FileNotFoundError(path)

    edges: list[tuple[int, int]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"{path.name} line {line_no} has fewer than two columns")
        try:
            u = int(parts[0])
            v = int(parts[1])
        except ValueError as exc:
            raise ValueError(f"{path.name} line {line_no} endpoints must be integers") from exc
        edges.append((u, v))
    return edges


def _resolve_scope(
    scope: RenderScope, layout: dict[str, Any], sample: dict[str, Any]
) -> Literal["full", "sample"]:
    if scope == "full":
        return "full"
    if scope == "sample":
        return "sample"

    layout_scope = str(layout.get("layout_scope", "")).lower()
    sampling_policy = str(sample.get("sampling_policy", "")).lower()
    if layout_scope == "full" or sampling_policy == "full_graph":
        return "full"
    return "sample"


def _prepare_render_data(
    *,
    instance: dict[str, Any],
    layout: dict[str, Any],
    sample: dict[str, Any],
    full_edges: list[tuple[int, int]],
    scope: Literal["full", "sample"],
    color_by: ColorEncoding,
    solver_partition_path: Path | None,
) -> _RenderData:
    warnings: list[str] = []

    node_positions = _parse_positions(layout.get("node_positions"))
    instance_nodes = _parse_instance_nodes(instance.get("nodes"))

    if scope == "sample":
        sampled_nodes = _parse_int_list(sample.get("sampled_nodes"), "sampled_nodes")
        nodes = sampled_nodes
        sample_edges = _parse_edge_list(sample.get("sampled_edges"), "sampled_edges")
        edges = [edge for edge in sample_edges if edge[0] in nodes and edge[1] in nodes]
    else:
        nodes = instance_nodes or sorted(node_positions)
        node_set = set(nodes)
        edges = [edge for edge in full_edges if edge[0] in node_set and edge[1] in node_set]

    missing_positions = [node for node in nodes if node not in node_positions]
    if missing_positions:
        raise ValueError(
            "layout does not contain positions for all rendered nodes; "
            f"missing first nodes: {missing_positions[:10]}"
        )

    positions = {node: node_positions[node] for node in nodes}
    degrees = _full_degrees(full_edges, nodes)
    labels = _labels_for_encoding(
        instance=instance,
        nodes=nodes,
        degrees=degrees,
        color_by=color_by,
        solver_partition_path=solver_partition_path,
        warnings=warnings,
    )
    return _RenderData(
        nodes=nodes,
        edges=edges,
        positions=positions,
        degrees=degrees,
        labels=labels,
        warnings=warnings,
    )


def _parse_positions(value: Any) -> dict[int, tuple[float, float]]:
    if not isinstance(value, dict):
        raise ValueError("graph_preview_layout.json key 'node_positions' must be an object")

    positions: dict[int, tuple[float, float]] = {}
    for raw_node, raw_position in value.items():
        if not isinstance(raw_position, list) or len(raw_position) < 2:
            raise ValueError(f"invalid position for node {raw_node!r}")
        node = int(raw_node)
        positions[node] = (float(raw_position[0]), float(raw_position[1]))
    return positions


def _parse_instance_nodes(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []

    nodes: list[int] = []
    for item in value:
        if isinstance(item, int):
            nodes.append(item)
        elif isinstance(item, dict):
            raw_id = item.get("id", item.get("node", item.get("vertex")))
            if raw_id is not None:
                nodes.append(int(raw_id))
    return sorted(set(nodes))


def _parse_int_list(value: Any, field_name: str) -> list[int]:
    if not isinstance(value, list):
        raise ValueError(f"graph_preview_sample.json key '{field_name}' must be a list")
    return [int(item) for item in value]


def _parse_edge_list(value: Any, field_name: str) -> list[tuple[int, int]]:
    if not isinstance(value, list):
        raise ValueError(f"graph_preview_sample.json key '{field_name}' must be a list")

    edges: list[tuple[int, int]] = []
    for index, item in enumerate(value):
        if not isinstance(item, list) or len(item) < 2:
            raise ValueError(f"{field_name}[{index}] must contain at least two endpoints")
        edges.append((int(item[0]), int(item[1])))
    return edges


def _full_degrees(edges: list[tuple[int, int]], nodes: list[int]) -> dict[int, int]:
    degrees = dict.fromkeys(nodes, 0)
    for u, v in edges:
        if u in degrees:
            degrees[u] += 1
        if v in degrees:
            degrees[v] += 1
    return degrees


def _labels_for_encoding(
    *,
    instance: dict[str, Any],
    nodes: list[int],
    degrees: dict[int, int],
    color_by: ColorEncoding,
    solver_partition_path: Path | None,
    warnings: list[str],
) -> dict[int, str]:
    if color_by == "none":
        return dict.fromkeys(nodes, "all")

    if color_by == "degree":
        return {node: str(degrees.get(node, 0)) for node in nodes}

    if color_by == "planted_block":
        planted = _planted_labels(instance)
        if not planted:
            warnings.append("requested planted_block coloring, but no planted labels were found")
            return dict.fromkeys(nodes, "missing")
        return {node: str(planted.get(node, "missing")) for node in nodes}

    if color_by == "solver_partition":
        if solver_partition_path is None:
            raise ValueError("--solver-partition is required when --color-by solver_partition")
        solver_labels = _read_solver_partition(solver_partition_path)
        return {node: str(solver_labels.get(node, "missing")) for node in nodes}

    raise ValueError(f"unsupported color encoding: {color_by}")


def _planted_labels(instance: dict[str, Any]) -> dict[int, str]:
    labels: dict[int, str] = {}

    top_level = instance.get("planted_partition")
    if isinstance(top_level, dict):
        for key, value in top_level.items():
            labels[int(key)] = str(value)
    elif isinstance(top_level, list):
        for index, value in enumerate(top_level):
            labels[index] = str(value)

    nodes = instance.get("nodes")
    if isinstance(nodes, list):
        for item in nodes:
            if not isinstance(item, dict):
                continue
            raw_id = item.get("id", item.get("node", item.get("vertex")))
            if raw_id is None:
                continue
            for key in ("planted_block", "generated_block", "community", "block"):
                if key in item and item[key] is not None:
                    labels[int(raw_id)] = str(item[key])
                    break

    return labels


def _read_solver_partition(path: Path) -> dict[int, str]:
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {int(key): str(value) for key, value in data.items()}
        if isinstance(data, list):
            return {index: str(value) for index, value in enumerate(data)}
        raise ValueError("solver partition JSON must be an object or list")

    labels: dict[int, str] = {}
    for index, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            labels[int(parts[0])] = parts[1]
        else:
            labels[index] = parts[0]
    return labels


def _render_svg(data: _RenderData, report: dict[str, Any], title: str) -> str:
    scaled = _scale_positions(data.positions, DEFAULT_WIDTH, DEFAULT_HEIGHT)
    colors = _colors_for_labels(data.labels)

    metadata = html.escape(json.dumps(report, ensure_ascii=False, sort_keys=True))
    escaped_title = html.escape(title)
    footer = _footer_text(report)

    edge_lines = []
    for u, v in data.edges:
        if u not in scaled or v not in scaled:
            continue
        x1, y1 = scaled[u]
        x2, y2 = scaled[v]
        edge_lines.append(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            'stroke="#b8b8b8" stroke-width="1" stroke-opacity="0.55" />'
        )

    node_lines = []
    for node in data.nodes:
        x, y = scaled[node]
        label = data.labels.get(node, "missing")
        color = colors.get(label, "#4e79a7")
        degree = data.degrees.get(node, 0)
        node_lines.append(
            f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{DEFAULT_NODE_RADIUS:.3f}" '
            f'fill="{color}" stroke="#222222" stroke-width="0.6">'
            f"<title>node={node}; label={html.escape(label)}; degree={degree}</title>"
            "</circle>"
        )

    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{DEFAULT_WIDTH}" '
                f'height="{DEFAULT_HEIGHT}" viewBox="0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}" '
                'role="img">'
            ),
            f"<metadata>{metadata}</metadata>",
            f"<title>{escaped_title}</title>",
            '<rect width="100%" height="100%" fill="white" />',
            f'<text x="24" y="32" font-size="18" font-family="monospace">{escaped_title}</text>',
            '<g id="edges">',
            *edge_lines,
            "</g>",
            '<g id="nodes">',
            *node_lines,
            "</g>",
            (
                f'<text x="24" y="{DEFAULT_HEIGHT - 28}" font-size="12" '
                f'font-family="monospace">{html.escape(footer)}</text>'
            ),
            "</svg>",
            "",
        ]
    )


def _scale_positions(
    positions: dict[int, tuple[float, float]], width: int, height: int
) -> dict[int, tuple[float, float]]:
    if not positions:
        raise ValueError("cannot render graph with no node positions")

    xs = [position[0] for position in positions.values()]
    ys = [position[1] for position in positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)
    margin = 70.0

    scaled: dict[int, tuple[float, float]] = {}
    for node, (x, y) in positions.items():
        sx = margin + ((x - min_x) / span_x) * (width - 2.0 * margin)
        sy = margin + ((max_y - y) / span_y) * (height - 2.0 * margin)
        scaled[node] = (sx, sy)
    return scaled


def _colors_for_labels(labels: dict[int, str]) -> dict[str, str]:
    unique_labels = sorted(set(labels.values()), key=_label_sort_key)

    if _all_numeric(unique_labels):
        numeric = [float(label) for label in unique_labels]
        min_value = min(numeric)
        max_value = max(numeric)
        if math.isclose(min_value, max_value):
            return {unique_labels[0]: "#4e79a7"}
        return {
            label: _continuous_color((float(label) - min_value) / (max_value - min_value))
            for label in unique_labels
        }

    return {
        label: CATEGORICAL_PALETTE[index % len(CATEGORICAL_PALETTE)]
        for index, label in enumerate(unique_labels)
    }


def _all_numeric(values: list[str]) -> bool:
    for value in values:
        try:
            float(value)
        except ValueError:
            return False
    return bool(values)


def _continuous_color(normalized: float) -> str:
    value = max(0.0, min(1.0, normalized))
    start = (230, 240, 255)
    end = (31, 78, 121)
    red = round(start[0] + value * (end[0] - start[0]))
    green = round(start[1] + value * (end[1] - start[1]))
    blue = round(start[2] + value * (end[2] - start[2]))
    return f"#{red:02x}{green:02x}{blue:02x}"


def _label_sort_key(value: str) -> tuple[int, float | str]:
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


def _footer_text(report: dict[str, Any]) -> str:
    status = (
        "validated solver artifact declared"
        if report.get("validated_solver_artifact")
        else "illustrative preview only"
    )
    return (
        f"scope={report['image_scope']}; color={report['color_by']}; "
        f"layout={report['layout_algorithm']}; seed={report['layout_seed']}; {status}"
    )


def _default_title(bundle_path: Path, scope: str, color_by: str) -> str:
    return f"{bundle_path.name} — {scope} preview colored by {color_by}"


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def result_to_dict(result: RenderResult) -> dict[str, Any]:
    """Convert a render result to a JSON-serializable dictionary."""

    return asdict(result)
